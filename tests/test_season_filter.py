"""The campground map's Dates filter: which campgrounds are open on a stay's nights.

AWH 2026-11-07. It judges an entry by its OWN `season` — `year_round: true`, or
an `opens`/`closes` pair (MM-DD, recurring) — plus a temporary closure. Doc
§2.2 governs it like every structured filter: a campground with no usable
season (seasonal with no dates, or only one end known) is unknown and FADES;
only a season that misses the stay, or a known closure, hides it. At ship that
is about half the map faded under any seasonal range, which is the honest state
of the data.

The predicates are lifted verbatim from the template (the same block
`test_rating_filter` lifts) and run in quickjs, against hand-made rows for the
calendar edge cases and against the real `campgrounds.json` for the counts.

    python -m unittest tests.test_season_filter -v
"""

import datetime as dt
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_rating_filter import _markers, _predicate_source, quickjs  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _real_markers():
    """`_markers()` keeps only the rating/hookup/rate keys; add the season ones."""
    sys.path.insert(0, ROOT)
    import ekko_trips_app as A
    with open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8") as fh:
        rows = [r for r in json.load(fh)
                if r.get("kind", "campground") == "campground"]
    keep = ("year_round", "opens", "closes", "closed", "reopens")
    return [{k: m[k] for k in keep if k in m} for m in A._map_marker_rows(rows)]


class TestSeasonPayload(unittest.TestCase):
    """What rides inline (doc §8.4's fifth exception)."""

    def project(self, season):
        sys.path.insert(0, ROOT)
        import ekko_trips_app as A
        return A._map_marker_rows([{"id": 1, "name": "x", "season": season}])[0]

    def test_year_round(self):
        m = self.project({"year_round": True, "opens": "04-01", "closes": "10-31"})
        self.assertIs(m.get("year_round"), True)
        self.assertNotIn("opens", m, "year_round wins over a pair stored beside it")

    def test_pair(self):
        m = self.project({"year_round": False, "opens": "05-01", "closes": "10-15"})
        self.assertEqual((m["opens"], m["closes"]), ("05-01", "10-15"))
        self.assertNotIn("year_round", m)

    def test_unusable_seasons_carry_nothing(self):
        for s in ({"year_round": False}, {"year_round": False, "opens": "05-01"},
                  {"closes": "10-15"}, {"note": "loop B closes after Labor Day"}, None):
            with self.subTest(season=s):
                m = self.project(s)
                for k in ("year_round", "opens", "closes"):
                    self.assertNotIn(k, m)


@unittest.skipIf(quickjs is None, "quickjs not installed (pip install quickjs)")
class TestSeasonFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ctx = quickjs.Context()
        cls.ctx.eval("var STORE = {get: function (k, f) { return f; }};"
                     "var ratingMin = 0, priceMax = 0;")
        cls.ctx.eval(_predicate_source())
        cls.ctx.eval("""
            function verdicts(json, arrive, leave, mode) {
              var rows = JSON.parse(json);
              dateArrive = arrive; dateLeave = leave; dateMode = mode;
              var out = [];
              for (var i = 0; i < rows.length; i++) {
                var r = rows[i];
                out.push(!schemaPasses(r) ? 'fail' : schemaUnknown(r) ? 'unknown' : 'pass');
              }
              return JSON.stringify(out);
            }
        """)
        cls.real = _real_markers()

    def verdicts(self, rows, arrive, leave="", mode="any"):
        return json.loads(self.ctx.get("verdicts")(json.dumps(rows), arrive, leave, mode))

    def one(self, row, arrive, leave="", mode="any"):
        return self.verdicts([row], arrive, leave, mode)[0]

    SUMMER = {"opens": "05-01", "closes": "10-31"}
    WINTER = {"opens": "11-01", "closes": "04-30"}

    def test_inactive_without_an_arrival(self):
        self.assertEqual(self.one(self.SUMMER, ""), "pass")
        self.assertEqual(self.one({}, ""), "pass", "no filter, nothing unknown")

    def test_year_round_and_unknown(self):
        self.assertEqual(self.one({"year_round": True}, "2027-01-10"), "pass")
        self.assertEqual(self.one({}, "2027-01-10"), "unknown", "§2.2: fade, never hide")

    def test_simple_season(self):
        self.assertEqual(self.one(self.SUMMER, "2027-07-04"), "pass")
        self.assertEqual(self.one(self.SUMMER, "2027-01-10"), "fail")

    def test_closing_day_is_an_open_night(self):
        self.assertEqual(self.one(self.SUMMER, "2027-10-31"), "pass")
        self.assertEqual(self.one(self.SUMMER, "2027-11-01"), "fail")
        self.assertEqual(self.one(self.SUMMER, "2027-05-01"), "pass")
        self.assertEqual(self.one(self.SUMMER, "2027-04-30"), "fail")

    def test_season_over_new_year(self):
        self.assertEqual(self.one(self.WINTER, "2027-01-15"), "pass")
        self.assertEqual(self.one(self.WINTER, "2026-12-20", "2027-01-03"), "pass")
        self.assertEqual(self.one(self.WINTER, "2027-07-04"), "fail")

    def test_leave_is_the_morning_after_the_last_night(self):
        # Arrive Apr 28, leave May 1: nights Apr 28-30, all closed.
        self.assertEqual(self.one(self.SUMMER, "2027-04-28", "2027-05-01"), "fail")
        self.assertEqual(self.one(self.SUMMER, "2027-04-28", "2027-05-02"), "pass")

    def test_any_versus_every(self):
        stay = ("2027-10-29", "2027-11-03")
        self.assertEqual(self.one(self.SUMMER, *stay, mode="any"), "pass")
        self.assertEqual(self.one(self.SUMMER, *stay, mode="every"), "fail")
        self.assertEqual(self.one(self.SUMMER, "2027-06-01", "2027-06-08", "every"), "pass")

    def test_a_stay_over_a_year_long(self):
        self.assertEqual(self.one(self.SUMMER, "2027-01-01", "2028-06-01", "every"), "fail")
        self.assertEqual(self.one(self.SUMMER, "2027-01-01", "2028-06-01", "any"), "pass")

    def test_leap_day_folds_onto_feb_28(self):
        row = {"opens": "02-28", "closes": "02-28"}
        self.assertEqual(self.one(row, "2028-02-29"), "pass")
        self.assertEqual(self.one(row, "2028-03-01"), "fail")

    def test_closure_with_a_year(self):
        row = {"year_round": True, "closed": True, "reopens": "2028 (DNR)"}
        self.assertEqual(self.one(row, "2027-07-04"), "fail")
        self.assertEqual(self.one(row, "2028-07-04"), "unknown",
                         "the closure may run on; it no longer proves closed")
        # A stay that straddles the year: some nights unknown, so not a fail...
        self.assertEqual(self.one(row, "2027-12-30", "2028-01-03"), "unknown")
        # ...unless every night must be open.
        self.assertEqual(self.one(row, "2027-12-30", "2028-01-03", "every"), "fail")

    def test_closure_after_a_year(self):
        row = {"year_round": True, "closed": True, "reopens": "after 2026"}
        self.assertEqual(self.one(row, "2026-12-20"), "fail")
        self.assertEqual(self.one(row, "2027-03-01"), "unknown")

    def test_closure_with_no_date(self):
        today = dt.date.today()
        soon = (today + dt.timedelta(days=3)).isoformat()
        later = (today + dt.timedelta(days=200)).isoformat()
        row = {"year_round": True, "closed": True, "reopens": "until further notice"}
        self.assertEqual(self.one(row, soon), "fail")
        self.assertEqual(self.one(row, later), "unknown")
        # Off-season stays fail whatever the closure says.
        self.assertEqual(self.one(dict(self.SUMMER, closed=True), "2028-01-10"), "fail")

    def test_real_data_counts(self):
        """Under a winter night: year-round passes, a summer pair hides, the rest fades."""
        v = self.verdicts(self.real, "2027-01-15")
        open_ = [m for m in self.real if not m.get("closed")]
        vo = [x for m, x in zip(self.real, v) if not m.get("closed")]
        unusable = sum(1 for m in open_ if not m.get("year_round") and "opens" not in m)
        self.assertGreater(unusable, 0, "fixture no longer exercises §2.2")
        self.assertEqual(vo.count("unknown"), unusable)
        self.assertEqual(vo.count("pass") + vo.count("fail"), len(open_) - unusable)
        self.assertGreater(vo.count("fail"), 1000, "winter should close most seasonal pairs")
        self.assertEqual(len(v), len(self.real))


if __name__ == "__main__":
    unittest.main()
