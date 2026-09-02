"""A stop you added from Detect Stops and then deleted must not come back clean.

Stop detection re-scans the same GPS track on every run. The trip's own stays
and events normally suppress a cluster (`_drop_stops_at_known_locations`), so
an accepted stop stops being offered — but DELETING that event removes exactly
the anchor that was doing the suppressing. The stop therefore reappears
*because* it was rejected, looking indistinguishable from a fresh discovery.

`dismissed_stops` on the trip record remembers the rejection. It FLAGS rather
than drops: the row still renders, dimmed and unchecked, with a tag. The
admin's earlier "no" is information, not a veto — they may have deleted the
event for an unrelated reason, and a row withheld is one they can never
reconsider.

Run from the project root with the venv active:

    python -m unittest tests.test_dismissed_stops -v
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import trips  # noqa: E402
from ekko_trips_app import _flag_dismissed_stops  # noqa: E402

# Roaring Fork, Grand County CO — the waypoint from the trip-95 report.
LAT, LNG = 40.130105, -105.766723
DATE = "2026-08-27"


def _cluster(lat=LAT, lng=LNG, coords=None, tz="America/Denver",
             start_tst=1787839860, end_tst=1787841000):
    """A stop cluster shaped like `_detect_stops` emits."""
    return {"center_lat": lat, "center_lng": lng,
            "coords": coords if coords is not None else [(lat, lng)],
            "start_tst": start_tst, "end_tst": end_tst, "tz": tz}


def _dismissal(lat=LAT, lng=LNG, date=DATE, name="Roaring Fork"):
    return {"lat": lat, "lng": lng, "date": date, "name": name,
            "removed_at": "2026-09-02"}


class TestFlagging(unittest.TestCase):
    """Pure matching: which clusters a dismissal marks."""

    def test_same_place_same_day_is_flagged(self):
        stops = [_cluster()]
        _flag_dismissed_stops(stops, [_dismissal()])
        self.assertEqual(stops[0]["_dismissed"]["name"], "Roaring Fork")
        self.assertEqual(stops[0]["_dismissed"]["removed_at"], "2026-09-02")

    def test_a_different_place_is_not_flagged(self):
        stops = [_cluster(lat=40.18, lng=-105.80, coords=[(40.18, -105.80)])]
        _flag_dismissed_stops(stops, [_dismissal()])
        self.assertIsNone(stops[0].get("_dismissed"))

    def test_same_place_on_another_day_is_not_flagged(self):
        """The same rest area outbound and on the return is two stops — the
        same rule `_drop_stops_at_known_locations` applies to its anchors."""
        stops = [_cluster(start_tst=1787839860 - 86400 * 2,
                          end_tst=1787841000 - 86400 * 2)]
        _flag_dismissed_stops(stops, [_dismissal()])
        self.assertIsNone(stops[0].get("_dismissed"))

    def test_a_dateless_dismissal_matches_on_position_alone(self):
        stops = [_cluster(start_tst=1787839860 - 86400 * 2,
                          end_tst=1787841000 - 86400 * 2)]
        _flag_dismissed_stops(stops, [_dismissal(date="")])
        self.assertIsNotNone(stops[0].get("_dismissed"))

    def test_any_ping_in_the_cluster_counts_not_just_the_centroid(self):
        """An asymmetric cluster's centroid is pulled off the place it sat;
        the dwell pings are what identify it (the trip-9 Mountain Top case)."""
        stops = [_cluster(lat=40.1340, lng=-105.7700,      # centroid ~400 m off
                          coords=[(40.1340, -105.7700), (LAT, LNG)])]
        _flag_dismissed_stops(stops, [_dismissal()])
        self.assertIsNotNone(stops[0].get("_dismissed"))

    def test_no_dismissals_flags_nothing(self):
        stops = [_cluster()]
        _flag_dismissed_stops(stops, [])
        self.assertIsNone(stops[0].get("_dismissed"))

    def test_a_malformed_dismissal_is_skipped_not_raised(self):
        stops = [_cluster()]
        _flag_dismissed_stops(stops, [{"name": "no coords"}, _dismissal()])
        self.assertIsNotNone(stops[0].get("_dismissed"))


class TestRecordingOnDelete(unittest.TestCase):
    """Deleting an event is what writes the dismissal."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._saved = (trips._DIR, trips.UPLOAD_DIR, trips.TRIPS_JSON)
        trips._DIR = self.tmp
        trips.UPLOAD_DIR = os.path.join(self.tmp, "photo_uploads")
        trips.TRIPS_JSON = os.path.join(self.tmp, "trip_data", "trips.json")
        os.makedirs(os.path.join(self.tmp, "trip_data"), exist_ok=True)

    def tearDown(self):
        trips._DIR, trips.UPLOAD_DIR, trips.TRIPS_JSON = self._saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _seed(self, events):
        with open(trips.TRIPS_JSON, "w") as f:
            json.dump([{"id": 1, "trip_note": "", "stays": [],
                        "events": events}], f, indent=2)

    def _record(self):
        with open(trips.TRIPS_JSON) as f:
            return json.load(f)[0]

    @staticmethod
    def _event(name="Roaring Fork", location=f"{LAT},{LNG}", date=DATE):
        return {"date": date, "time": "09:11", "end_time": "", "name": name,
                "description": "", "location": location, "locale": "",
                "state": "", "waypoint": True, "family_id": None,
                "needs_vetting": True, "tz": "America/Denver"}

    def test_delete_records_a_dismissal(self):
        self._seed([self._event()])
        trips.delete_event(1, 0)
        got = self._record()["dismissed_stops"]
        self.assertEqual(len(got), 1)
        self.assertAlmostEqual(got[0]["lat"], LAT)
        self.assertAlmostEqual(got[0]["lng"], LNG)
        self.assertEqual(got[0]["date"], DATE)
        self.assertEqual(got[0]["name"], "Roaring Fork")

    def test_an_event_with_no_location_records_nothing(self):
        """Nothing to match a future cluster against, so nothing to store."""
        self._seed([self._event(location="")])
        trips.delete_event(1, 0)
        self.assertNotIn("dismissed_stops", self._record())

    def test_repeated_add_and_delete_does_not_grow_the_list(self):
        for _ in range(3):
            self._seed([self._event()])
            record = self._record()
            trips.delete_event(1, 0)
        self.assertEqual(len(self._record()["dismissed_stops"]), 1)

    def test_two_different_places_are_both_kept(self):
        self._seed([self._event(), self._event(name="Elsewhere",
                                               location="40.20,-105.90")])
        trips.delete_event(1, 1)
        trips.delete_event(1, 0)
        self.assertEqual(len(self._record()["dismissed_stops"]), 2)

    def test_get_dismissed_stops_reads_them_back(self):
        self._seed([self._event()])
        trips.delete_event(1, 0)
        self.assertEqual(len(trips.get_dismissed_stops(1)), 1)
        self.assertEqual(trips.get_dismissed_stops(999), [])

    def test_the_flag_survives_the_round_trip(self):
        """The whole point: delete, then a re-detection of that cluster is
        flagged rather than offered as new."""
        self._seed([self._event()])
        trips.delete_event(1, 0)
        stops = [_cluster()]
        _flag_dismissed_stops(stops, trips.get_dismissed_stops(1))
        self.assertIsNotNone(stops[0].get("_dismissed"))


class TestClearingOnReAccept(unittest.TestCase):
    """Re-creating a stop where one was rejected is a change of mind."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._saved = (trips._DIR, trips.TRIPS_JSON)
        trips._DIR = self.tmp
        trips.TRIPS_JSON = os.path.join(self.tmp, "trip_data", "trips.json")
        os.makedirs(os.path.join(self.tmp, "trip_data"), exist_ok=True)
        with open(trips.TRIPS_JSON, "w") as f:
            json.dump([{"id": 1, "trip_note": "", "stays": [], "events": [],
                        "dismissed_stops": [_dismissal()]}], f, indent=2)

    def tearDown(self):
        trips._DIR, trips.TRIPS_JSON = self._saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_accepting_there_retires_the_dismissal(self):
        left = trips.clear_dismissed_stops_near(1, [(LAT, LNG, DATE)])
        self.assertEqual(left, [])
        self.assertEqual(trips.get_dismissed_stops(1), [])
        # An emptied list is removed from the record, not left as `[]` —
        # same housekeeping `remove_suppressed_pings` does.
        with open(trips.TRIPS_JSON) as f:
            self.assertNotIn("dismissed_stops", json.load(f)[0])

    def test_small_centroid_drift_between_runs_still_matches(self):
        """Detection re-derives the centroid each run; a few metres of drift
        must not leave a stale dismissal behind."""
        left = trips.clear_dismissed_stops_near(
            1, [(LAT + 0.0003, LNG - 0.0003, DATE)])
        self.assertEqual(left, [])

    def test_accepting_somewhere_else_leaves_it_alone(self):
        left = trips.clear_dismissed_stops_near(1, [(40.20, -105.90, DATE)])
        self.assertEqual(len(left), 1)

    def test_unknown_trip_returns_none(self):
        self.assertIsNone(trips.clear_dismissed_stops_near(999, [(1, 2, "")]))


if __name__ == "__main__":
    unittest.main()
