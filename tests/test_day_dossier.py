"""What a day's rollup is written FROM.

The dossier is the half of step 3 with a right answer. The prose is a judgement
call, but garbage in is confabulation out — a thin dossier is exactly what makes
a model reach for invented atmosphere, and a dossier full of gas stations is
what makes it write a paragraph about buying fuel.

The rule that matters most here is the last one: **a stop earns a mention in the
rollup exactly as it earns a card on the timeline** — by having photos or a
description. Two thirds of the library's events are auto-detected waypoints, and
a travel day's raw list is mostly rest areas (trip 95's 20 August: Amoco, I-70
West Rest Area, South Vienna Rest Area). Keeping the two tests identical also
keeps the page honest: a rollup must not describe something the timeline above
it has folded away.

Run from the project root with the venv active:

    python -m unittest tests.test_day_dossier -v
"""

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import process_rollups as R  # noqa: E402

DAY = "2026-08-23"


def _trip(**kw):
    t = {"id": 95, "summary": "Rocky Mountain National Park",
         "stays": [], "events": []}
    t.update(kw)
    return t


def _dossier(trip, driving=None, locations=None, memos=None,
             photos=None, card_photos=None):
    return R.day_dossier(trip, DAY, driving or {}, locations or {},
                         memos or {}, photos or {}, card_photos or {})


class TestWhatEarnsAMention(unittest.TestCase):
    def test_a_bare_waypoint_is_counted_not_named(self):
        trip = _trip(events=[{"date": DAY, "name": "Amoco", "waypoint": True}])
        d = _dossier(trip)
        self.assertEqual(d["stops"], [])
        self.assertEqual(d["unremarkable_stops"], 1)

    def test_a_waypoint_with_a_description_is_named(self):
        trip = _trip(events=[{"date": DAY, "name": "Greenfield Rest Area",
                              "waypoint": True, "description": "Dinner"}])
        d = _dossier(trip)
        self.assertEqual([s["name"] for s in d["stops"]], ["Greenfield Rest Area"])
        self.assertNotIn("unremarkable_stops", d)

    def test_a_waypoint_with_photos_is_named(self):
        trip = _trip(events=[{"date": DAY, "name": "Fort Necessity", "waypoint": True}])
        d = _dossier(trip, card_photos={"event-0": 3})
        self.assertEqual([s["name"] for s in d["stops"]], ["Fort Necessity"])
        self.assertEqual(d["stops"][0]["photos"], 3)

    def test_a_real_event_is_always_named(self):
        trip = _trip(events=[{"date": DAY, "name": "Bear Lake", "waypoint": False}])
        self.assertEqual([s["name"] for s in _dossier(trip)["stops"]], ["Bear Lake"])

    def test_other_days_events_are_not_included(self):
        trip = _trip(events=[{"date": "2026-08-22", "name": "Elsewhere"}])
        self.assertEqual(_dossier(trip)["stops"], [])

    def test_the_photo_index_follows_the_events_real_position(self):
        # card_photos is keyed "event-<index into trip['events']>", so an event
        # from another day sitting earlier in the list must not shift it.
        trip = _trip(events=[{"date": "2026-08-01", "name": "Other"},
                             {"date": DAY, "name": "Ours", "waypoint": True}])
        d = _dossier(trip, card_photos={"event-1": 2})
        self.assertEqual([s["name"] for s in d["stops"]], ["Ours"])

    def test_stops_come_out_in_time_order(self):
        trip = _trip(events=[
            {"date": DAY, "name": "Late", "time": "17:00"},
            {"date": DAY, "name": "Early", "time": "08:30"}])
        self.assertEqual([s["name"] for s in _dossier(trip)["stops"]],
                         ["Early", "Late"])


class TestFacts(unittest.TestCase):
    def test_driving_is_carried_when_the_gps_measured_it(self):
        d = _dossier(_trip(), driving={DAY: {"miles": 273, "moving": "5h 12m",
                                             "round_trip": False}})
        self.assertEqual(d["driving"], {"miles": 273, "time": "5h 12m",
                                        "round_trip": False})

    def test_a_day_that_did_not_drive_carries_no_driving_key(self):
        # Absent, not zero: "0 mi" reads as a measured stillness rather than as
        # nothing to say, and invites the model to remark on it.
        self.assertNotIn("driving", _dossier(_trip()))

    def test_arriving_and_leaving_are_distinguished(self):
        trip = _trip(stays=[{"start": DAY, "end": "2026-08-26",
                             "place": "Moraine Park", "campground_id": 2303}])
        night = _dossier(trip)["nights"][0]
        self.assertTrue(night["arriving"])
        self.assertFalse(night["leaving"])

    def test_campground_detail_is_attached_but_not_waterfront_boilerplate(self):
        trip = _trip(stays=[{"start": DAY, "end": DAY, "place": "Moraine Park",
                             "campground_id": 2303}])
        locations = {2303: {"elevation_meters": 2498, "waterfront": "not waterfront",
                            "ownership": "federal", "note": "NPS campground"}}
        night = _dossier(trip, locations=locations)["nights"][0]
        self.assertEqual(night["elevation_m"], 2498)
        self.assertEqual(night["campground_note"], "NPS campground")
        # "not waterfront" is the DEFAULT for an audited campground, so passing
        # it along would state a non-fact about every inland site in the library.
        self.assertNotIn("waterfront", night)

    def test_only_this_trips_memos_for_this_day(self):
        memos = {
            "a": {"trip_id": 95, "date": DAY, "speaker": "Andrew",
                  "transcript": "Elk in the meadow."},
            "b": {"trip_id": 95, "date": "2026-08-24", "transcript": "Other day."},
            "c": {"trip_id": 12, "date": DAY, "transcript": "Other trip."},
            "d": {"trip_id": 95, "date": DAY, "transcript": "   "},   # untranscribed
        }
        d = _dossier(_trip(), memos=memos)
        self.assertEqual(d["memos"],
                         [{"said_by": "Andrew", "said": "Elk in the meadow.", "at": ""}])


class TestTripDays(unittest.TestCase):
    def test_every_date_the_trip_mentions(self):
        trip = _trip(stays=[{"start": "2026-08-19", "end": "2026-08-20"}],
                     events=[{"date": "2026-08-21"}])
        self.assertEqual(R.trip_days(trip),
                         ["2026-08-19", "2026-08-20", "2026-08-21"])


class TestMergeAndWrite(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        p = mock.patch.object(R, "ROLLUPS_FILE",
                              os.path.join(self.tmp, "day_rollups.json"))
        p.start()
        self.addCleanup(p.stop)

    def test_an_edit_made_during_a_long_batch_is_not_clobbered(self):
        # Same contract as the memo transcriber: a batch takes minutes and the
        # app writes to this file, so deltas merge per-key against disk.
        R._merge_and_write({"95/2026-08-23": {"text": "first"}})
        R._merge_and_write({"95/2026-08-24": {"text": "second"}})
        with open(R.ROLLUPS_FILE) as f:
            data = json.load(f)
        self.assertEqual(set(data), {"95/2026-08-23", "95/2026-08-24"})

    def test_write_leaves_no_temp_file(self):
        R._merge_and_write({"95/2026-08-23": {"text": "x"}})
        self.assertEqual([f for f in os.listdir(self.tmp) if f.endswith(".tmp")], [])


if __name__ == "__main__":
    unittest.main()
