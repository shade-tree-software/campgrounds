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
             photos=None, card_photos=None, card_captions=None):
    return R.day_dossier(trip, DAY, driving or {}, locations or {},
                         memos or {}, photos or {}, card_photos or {},
                         card_captions or {})


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
    def test_a_long_drive_is_a_bucket_never_a_figure(self):
        # No mileage and no duration reach the model: both are printed on the
        # day divider beside the entry, and given the numbers it writes "we
        # drove 124 miles in 2h 24m", which is not how anyone recalls a day.
        d = _dossier(_trip(), driving={DAY: {"miles": 460, "moving": "8h 10m",
                                             "round_trip": False}})
        self.assertEqual(d["driving"], "very long")
        self.assertNotIn("460", json.dumps(d))
        self.assertNotIn("8h 10m", json.dumps(d))

    def test_an_ordinary_drive_is_not_worth_mentioning(self):
        # Median A-to-B day in the library is 174 miles. A day like that is
        # just how you get to the next campground.
        d = _dossier(_trip(), driving={DAY: {"miles": 174, "moving": "3h 30m"}})
        self.assertNotIn("driving", d)

    def test_a_round_trip_is_never_mentioned_however_far(self):
        # A loop out of camp and back is the day's activity, not its travel;
        # trip 95's 54-mile run up to the Alpine Visitors Center is the drive.
        d = _dossier(_trip(), driving={DAY: {"miles": 191, "moving": "5h 00m",
                                             "round_trip": True}})
        self.assertNotIn("driving", d)

    def test_a_day_that_did_not_drive_carries_no_driving_key(self):
        # Absent, not zero: "0 mi" reads as a measured stillness rather than as
        # nothing to say, and invites the model to remark on it.
        self.assertNotIn("driving", _dossier(_trip()))

    def test_where_we_wake_and_where_we_sleep_are_separate_facts(self):
        trip = _trip(stays=[{"start": "2026-08-22", "end": DAY,
                             "place": "Spring Canyon"},
                            {"start": DAY, "end": "2026-08-26",
                             "place": "Moraine Park"}])
        d = _dossier(trip)
        self.assertEqual(d["woke_up_at"]["place"], "Spring Canyon")
        self.assertEqual(d["sleeping_at"]["place"], "Moraine Park")
        self.assertNotIn("ended", d)

    def test_the_last_day_of_a_trip_ends_at_home(self):
        # The bug this replaces: one `nights` list matched start <= day <= end,
        # so a departure day inherited the night BEFORE it and nothing said the
        # day ended anywhere else. Trip 95's 1 September came out as "that night
        # was our last at Bulltown Campground" — they had left that morning and
        # driven 243 miles home. Every trip's final day had this shape.
        trip = _trip(stays=[{"start": "2026-08-22", "end": DAY,
                             "place": "Bulltown Campground"}])
        d = _dossier(trip)
        self.assertEqual(d["woke_up_at"]["place"], "Bulltown Campground")
        self.assertNotIn("sleeping_at", d)
        self.assertIn("home", d["ended"])

    def test_a_day_in_the_middle_of_a_stay_is_only_sleeping_at(self):
        trip = _trip(stays=[{"start": "2026-08-22", "end": "2026-08-26",
                             "place": "Moraine Park"}])
        d = _dossier(trip)
        self.assertEqual(d["sleeping_at"]["place"], "Moraine Park")
        self.assertNotIn("ended", d)


class TestWhereThingsAre(unittest.TestCase):
    """An admin unit is not a place anyone says out loud.

    Nominatim's reverse geocode falls through city → town → village → hamlet →
    municipality → township → county, and a point outside every town's polygon
    lands on the last two: 29% of the library's 1,116 events (177 townships,
    144 counties). Handed to a writer that becomes "Bulltown Campground in
    Braxton County", which no traveller would write, and on trip 95 every one
    of Rocky Mountain's overlooks was "Larimer County, CO".
    """

    def test_a_named_town_is_kept(self):
        trip = _trip(events=[{"date": DAY, "name": "Rainbow Park",
                              "locale": "Wray", "state": "CO",
                              "description": "breakfast"}])
        self.assertEqual(_dossier(trip)["stops"][0]["where"], "Wray, CO")

    def test_a_county_or_township_is_dropped_the_state_survives(self):
        # The state is kept deliberately. On a day that crosses four of them,
        # breakfast in Pennsylvania and dinner in Indiana is how the day is
        # actually recalled; on a day that never leaves Colorado it is merely
        # redundant, which the model can judge. The county never is.
        for admin in ("Larimer County", "Wharton Township", "Iberville Parish",
                      "Bedminster Twp", "Municipality of Anchorage"):
            trip = _trip(events=[{"date": DAY, "name": "Forest Canyon Overlook",
                                  "locale": admin, "state": "CO",
                                  "description": "overlook"}])
            stop = _dossier(trip)["stops"][0]
            self.assertEqual(stop["where"], "CO", f"{admin!r} reached the model")

    def test_a_stop_with_no_locale_at_all_gets_no_where(self):
        trip = _trip(events=[{"date": DAY, "name": "Alpine Visitors Center",
                              "locale": "", "state": "", "description": "x"}])
        self.assertNotIn("where", _dossier(trip)["stops"][0])

    def test_a_stay_gets_the_same_treatment(self):
        trip = _trip(stays=[{"start": DAY, "end": "2026-09-01",
                             "place": "Bulltown Campground",
                             "locale": "Braxton County", "state": "WV"}])
        self.assertEqual(_dossier(trip)["sleeping_at"]["where"], "WV")
        self.assertNotIn("Braxton", json.dumps(_dossier(trip)))

    def test_campground_detail_is_attached_but_not_waterfront_boilerplate(self):
        trip = _trip(stays=[{"start": DAY, "end": "2026-08-26",
                             "place": "Moraine Park", "campground_id": 2303,
                             "notes": "8195 feet"}])
        locations = {2303: {"elevation_meters": 2498, "waterfront": "not waterfront",
                            "ownership": "federal", "note": "NPS campground"}}
        night = _dossier(trip, locations=locations)["sleeping_at"]
        self.assertEqual(night["elevation_m"], 2498)
        self.assertEqual(night["campground_note"], "NPS campground")
        # "not waterfront" is the DEFAULT for an audited campground, so passing
        # it along would state a non-fact about every inland site in the library.
        self.assertNotIn("waterfront", night)

    def test_a_places_description_is_told_once_on_the_day_you_pull_in(self):
        # Attached to every day of a stay it gets recited on each of them: trip
        # 95 described Prophetstown's prairie grass on both the 20th and the
        # 21st, and Moraine Park's elevation three days running.
        stay = {"start": "2026-08-20", "end": "2026-08-26",
                "place": "Moraine Park", "campground_id": 2303,
                "notes": "Prairie grass grown up around the park"}
        locations = {2303: {"note": "NPS campground"}}
        night = _dossier(_trip(stays=[stay]), locations=locations)["sleeping_at"]
        self.assertEqual(night["place"], "Moraine Park")
        self.assertNotIn("notes", night)
        self.assertNotIn("campground_note", night)

    def test_captions_reach_the_dossier(self):
        # They did not, for the life of the feature: the dossier carried photo
        # COUNTS and nothing else, so the most human material in the archive
        # after the memos never reached the writer.
        trip = _trip(events=[{"date": DAY, "name": "Bear Lake"}],
                     stays=[{"start": DAY, "end": "2026-08-26",
                             "place": "Moraine Park"}])
        d = _dossier(trip, card_photos={"event-0": 3, "stay-0": 2},
                     card_captions={"event-0": ["No mountains yet"],
                                    "stay-0": ["Just like the album cover"]})
        self.assertEqual(d["stops"][0]["photo_captions"], ["No mountains yet"])
        self.assertEqual(d["sleeping_at"]["photo_captions"],
                         ["Just like the album cover"])

    def test_a_day_with_no_captions_carries_no_caption_key(self):
        trip = _trip(events=[{"date": DAY, "name": "Bear Lake"}])
        d = _dossier(trip, card_photos={"event-0": 3})
        self.assertNotIn("photo_captions", d["stops"][0])

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
