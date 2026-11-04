"""Weather Finder's forecast cache is shared across processes (AWH 2026-11-04).

On a multi-worker host each process had its own in-memory cache, so a re-search
that landed on another worker re-bought the cells the first search had already
fetched: "search again to widen it" did nothing the second time and only worked
the third. The SQLite tier at CACHE_PATH is what every worker shares. Clearing
the in-process dict between searches below stands in for "the next request
reached a different worker".

Run from the project root:

    python -m unittest tests.test_weather_cache -v
"""

import io
import json
import os
import tempfile
import unittest
import urllib.error
import urllib.parse
from unittest import mock

import weather_finder as wf

DAYS = [f"2026-11-{d:02d}" for d in range(5, 21)]


def _daily():
    return {"time": DAYS, "temperature_2m_max": [70] * 16,
            "temperature_2m_min": [50] * 16, "precipitation_sum": [0] * 16,
            "precipitation_probability_max": [0] * 16, "weather_code": [0] * 16}


def _campgrounds(n):
    # One campground per grid cell, strung out east of the origin, each in its
    # own 0.1° cell so every one is a separate forecast point.
    return [{"id": i, "kind": "campground", "name": f"CG {i}", "state": "PA",
             "location": f"40.0,{-80.0 + 0.15 * i:.2f}", "delta_temp": 0.0}
            for i in range(n)]


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class SharedCacheTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self._saved = (wf.CACHE_PATH, dict(wf._forecast_cache))
        wf.CACHE_PATH = os.path.join(self.tmp.name, "forecast_cache.sqlite")
        wf._forecast_cache.clear()
        self.requested = []   # locations per HTTP call
        self.fail_after = None  # 429 once this many calls have succeeded

        def urlopen(req, timeout=None):
            if self.fail_after is not None and len(self.requested) >= self.fail_after:
                raise urllib.error.HTTPError(req.full_url, 429, "Too Many", {}, None)
            q = urllib.parse.parse_qs(urllib.parse.urlparse(req.full_url).query)
            n = len(q["latitude"][0].split(","))
            self.requested.append(n)
            body = [{"daily": _daily()} for _ in range(n)]
            return _Response(json.dumps(body[0] if n == 1 else body).encode())

        patcher = mock.patch.object(wf.urllib.request, "urlopen", side_effect=urlopen)
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        wf.CACHE_PATH = self._saved[0]
        wf._forecast_cache.clear()
        wf._forecast_cache.update(self._saved[1])

    def search(self, cgs, budget):
        return wf.find_matching_days(cgs, (40.0, -80.0), max_miles=500,
                                     forecast_budget=budget, batch_size=10)

    def test_second_search_on_another_worker_widens_coverage(self):
        cgs = _campgrounds(50)
        first = self.search(cgs, budget=20)
        self.assertEqual((first["fetched"], first["from_cache"]), (20, 0))

        wf._forecast_cache.clear()  # the retry reaches a different worker
        second = self.search(cgs, budget=20)
        self.assertEqual(second["from_cache"], 20)
        self.assertEqual(second["fetched"], 20)
        self.assertGreater(second["considered"], first["considered"])

        wf._forecast_cache.clear()
        third = self.search(cgs, budget=20)
        self.assertEqual((third["fetched"], third["from_cache"]), (10, 40))
        self.assertEqual(third["considered"], third["eligible"])

    def test_rate_limit_midway_keeps_the_batches_already_fetched(self):
        cgs = _campgrounds(30)
        self.fail_after = 2   # two batches of 10 succeed, the third 429s
        with self.assertRaises(wf.RateLimited):
            self.search(cgs, budget=100)

        self.fail_after = None
        wf._forecast_cache.clear()
        retry = self.search(cgs, budget=100)
        self.assertEqual((retry["fetched"], retry["from_cache"]), (10, 20))
        self.assertEqual(retry["considered"], retry["eligible"])

    def test_expired_rows_are_not_served(self):
        cgs = _campgrounds(5)
        self.search(cgs, budget=100)
        wf._forecast_cache.clear()
        later = wf.time.time() + wf.FORECAST_TTL_S + 1
        with mock.patch.object(wf.time, "time", return_value=later):
            again = self.search(cgs, budget=100)
        self.assertEqual((again["fetched"], again["from_cache"]), (5, 0))

    def test_unusable_cache_file_degrades_to_in_process(self):
        wf.CACHE_PATH = os.path.join(self.tmp.name, "missing-dir", "cache.sqlite")
        with self.assertLogs("weather_finder", level="WARNING"):
            wf._db_warned = False
            first = self.search(_campgrounds(5), budget=100)
        self.assertEqual(first["fetched"], 5)
        second = self.search(_campgrounds(5), budget=100)
        self.assertEqual((second["fetched"], second["from_cache"]), (0, 5))

    def test_lookup_shares_the_file(self):
        wf.forecast_for_point(40.0, -79.0)
        wf._forecast_cache.clear()
        calls = len(self.requested)
        self.assertIsNotNone(wf.forecast_for_point(40.0, -79.0))
        self.assertEqual(len(self.requested), calls)


if __name__ == "__main__":
    unittest.main()
