"""What a day's write-up is built FROM.

The dossier is the half with a right answer. The prose is a judgement call, but
garbage in is confabulation out.

**What this file mostly pins is what the dossier REFUSES to carry.** The long
rollups were rejected because they restated the timeline, and they restated it
because the dossier handed the model the day's stops by name, their
descriptions, the captions on their photos and the notes on the campground —
all of which are printed on the cards directly below the write-up. A model
handed a list of places will name them; no prompt rule survives contact with
the data. So the fix was to stop offering them.

What is left is the part a reader scrolling the cards cannot assemble: how far,
which way, across what, how high it ended, and where the day sits in the trip.
`states` is the one fact that was nowhere in the trip record — a day's stops
name only the states it STOPPED in, silently dropping every state it merely
drove across.

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


def _stay(start, end, **kw):
    s = {"start": start, "end": end, "place": "Moraine Park",
         "where_label": "5 miles west of Estes Park, CO", "state": "CO",
         "campground_id": 7, "lat": 40.36, "lng": -105.58}
    s.update(kw)
    return s


def _dossier(trip, driving=None, elevations=None, states=None,
             trip_miles=None, day_index=None, day=DAY, track_known=True):
    return R.day_dossier(trip, day, driving or {}, elevations or {},
                         states, trip_miles, day_index, track_known)


class TestNamesInDescriptionsOut(unittest.TestCase):
    """Where the line sits, and it has moved once.

    The long rollups were rejected for restating the cards, so the first short
    dossier withheld every name too — which left a day spent at one campground
    with nothing to say but its mileage, the least interesting fact about it
    (AWH: "on local days the driving is not the important part"). A NAME is not
    a description. Names are in; what the cards say ABOUT them stays out."""

    def _full_day(self):
        trip = _trip(
            stays=[_stay("2026-08-22", "2026-08-24", notes="prairie grass",
                         site="7")],
            events=[{"date": DAY, "sort_date": DAY, "type": "event",
                     "name": "Alpine Visitor Center",
                     "description": "a ranger talk", "time": "10:00"},
                    {"date": DAY, "sort_date": DAY, "type": "event",
                     "name": "Sinclair, Benkelman", "waypoint": True},
                    {"date": DAY, "sort_date": DAY, "type": "event",
                     "name": "Lunch with the Svendsens",
                     "family_visit": "The Svendsens"}])
        trip["timeline"] = trip["events"]
        return _dossier(trip, driving={DAY: {"miles": 273, "moving": "5h 27m"}})

    def test_a_real_event_is_named(self):
        self.assertEqual(self._full_day()["events"], ["Alpine Visitor Center"])

    def test_a_family_visit_is_named_by_its_label(self):
        self.assertEqual(self._full_day()["family_visits"], ["The Svendsens"])

    def test_a_waypoint_is_counted_never_named(self):
        """Two thirds of the library's events are auto-detected stops and a
        travel day's raw list is mostly rest areas — the same test that decides
        whether one earns a card on the timeline."""
        d = self._full_day()
        self.assertEqual(d["waypoint_stops"], 1)
        self.assertNotIn("Sinclair", json.dumps(d))

    def test_the_campground_is_named_and_placed(self):
        d = self._full_day()
        self.assertEqual(d["to"]["place"], "Moraine Park")
        self.assertEqual(d["to"]["where"], "5 miles west of Estes Park, CO")

    def test_no_descriptions_notes_or_site_numbers(self):
        """The half that did NOT move: naming a place is the end of what the
        dossier knows about it."""
        blob = json.dumps(self._full_day())
        for leaked in ("ranger talk", "prairie grass", "Site", '"7"'):
            self.assertNotIn(leaked, blob)

    def test_no_photo_counts(self):
        """Photo counts told the old dossier which stops mattered most. With
        the stops named outright they are just a number to pad a sentence."""
        self.assertNotIn("photos", json.dumps(self._full_day()))


class TestTheShapeOfTheDay(unittest.TestCase):
    def test_mileage_is_a_real_figure_not_a_bucket(self):
        """The old dossier said "very long" and the approved summaries all
        quote exact miles, so the bucket could never have produced them."""
        d = _dossier(_trip(), driving={DAY: {"miles": 520, "moving": "9h 01m"}})
        self.assertEqual(d["miles"], 520)
        self.assertEqual(d["driving_time"], "9h 01m")

    def test_a_day_that_did_not_drive_carries_no_mileage(self):
        self.assertNotIn("miles", _dossier(_trip()))

    def test_a_round_trip_is_flagged_and_has_no_heading(self):
        """It started and ended in one place, so a compass direction would be
        a fiction — and the prompt needs to know to describe a different kind
        of day."""
        trip = _trip(stays=[_stay("2026-08-22", "2026-08-25")])
        d = _dossier(trip, driving={DAY: {"miles": 54, "round_trip": True}})
        self.assertTrue(d["round_trip"])
        self.assertNotIn("heading", d)

    def test_heading_comes_from_where_the_day_started_and_ended(self):
        trip = _trip(stays=[
            _stay("2026-08-22", DAY, lat=40.0, lng=-100.0),
            _stay(DAY, "2026-08-24", lat=40.0, lng=-105.0)])
        self.assertEqual(_dossier(trip, driving={DAY: {"miles": 273}})["heading"],
                         "west")

    def test_a_day_that_barely_moved_gets_no_heading(self):
        """Two campsites at the same park are not a direction of travel."""
        trip = _trip(stays=[_stay("2026-08-22", DAY, lat=40.36, lng=-105.58),
                            _stay(DAY, "2026-08-24", lat=40.37, lng=-105.59)])
        self.assertNotIn("heading", _dossier(trip, driving={DAY: {"miles": 3}}))


class TestAbsentMileageIsNotZero(unittest.TestCase):
    """The bug the first back-catalogue run actually shipped.

    `_trip_driving_by_day` omits a day rather than reporting "0 mi", so the
    dossier had no figure for a day with no GPS — and the model read the
    silence as zero. It wrote "the trip opened parked" for a day that drove
    from home, and "a second day without driving" for one that moved between
    two campgrounds. Three of the four track-less days in the library were
    wrong. Whether a day moved is knowable from the beds alone, so it is now
    stated rather than inferred."""

    def test_a_measured_day_under_the_threshold_says_it_stayed_put(self):
        d = _dossier(_trip(stays=[_stay("2026-08-22", "2026-08-25")]),
                     track_known=True)
        self.assertIn("negligible", d["driving"])
        self.assertNotIn("mileage", d)
        self.assertNotIn("moved", d)

    def test_an_unmeasured_day_says_the_distance_is_unknown(self):
        d = _dossier(_trip(stays=[_stay("2026-08-22", "2026-08-25")]),
                     track_known=False)
        self.assertIn("not recorded", d["mileage"])
        self.assertNotIn("driving", d)

    def test_an_unmeasured_day_that_changed_campground_reports_moved(self):
        """Trip 47's 2024-11-22: Grove City to Silver Canoe, drafted as
        "parked in western Pennsylvania"."""
        trip = _trip(stays=[_stay("2026-08-22", DAY, where_label="in Mercer, PA"),
                            _stay(DAY, "2026-08-24",
                                  where_label="in Rural Valley, PA")])
        self.assertTrue(_dossier(trip, track_known=False)["moved"])

    def test_an_unmeasured_first_day_reports_moved(self):
        """Only a destination: they drove out from home. Drafted as "the trip
        opened parked"."""
        trip = _trip(stays=[_stay(DAY, "2026-08-24")])
        self.assertTrue(_dossier(trip, track_known=False)["moved"])

    def test_an_unmeasured_last_day_reports_moved(self):
        trip = _trip(stays=[_stay("2026-08-22", DAY)])
        self.assertTrue(_dossier(trip, track_known=False)["moved"])

    def test_an_unmeasured_day_in_one_place_reports_not_moved(self):
        """The one of the four that was right, and must stay right."""
        trip = _trip(stays=[_stay("2026-08-22", "2026-08-25")])
        self.assertFalse(_dossier(trip, track_known=False)["moved"])


class TestWhereTheDayBeganAndEnded(unittest.TestCase):
    def test_waking_and_sleeping_are_separate_facts(self):
        trip = _trip(stays=[_stay("2026-08-22", DAY, state="NE",
                                  where_label="in Trenton, NE"),
                            _stay(DAY, "2026-08-24")])
        d = _dossier(trip)
        self.assertEqual(d["from"]["where"], "in Trenton, NE")
        self.assertEqual(d["to"]["where"], "5 miles west of Estes Park, CO")

    def test_the_last_day_has_no_destination(self):
        """They drove home; there is no next campground. The prompt reads the
        absence, together with day N of N, as the turn for home."""
        d = _dossier(_trip(stays=[_stay("2026-08-22", DAY)]))
        self.assertIn("from", d)
        self.assertNotIn("to", d)

    def test_mid_stay_days_wake_and_sleep_in_the_same_place(self):
        d = _dossier(_trip(stays=[_stay("2026-08-22", "2026-08-25")]))
        self.assertEqual(d["from"]["where"], d["to"]["where"])

    def test_a_county_or_township_is_dropped_the_state_survives(self):
        """An admin unit is not a place anyone says out loud."""
        trip = _trip(stays=[_stay(DAY, "2026-08-24", where_label=None,
                                  locale="Braxton County", state="WV")])
        self.assertEqual(_dossier(trip)["to"]["where"], "WV")

    def test_a_resolved_label_is_not_given_its_state_twice(self):
        trip = _trip(stays=[_stay(DAY, "2026-08-24",
                                  where_label="1 mile east of Battle Ground, IN",
                                  state="IN")])
        self.assertEqual(_dossier(trip)["to"]["where"],
                         "1 mile east of Battle Ground, IN")


class TestElevation(unittest.TestCase):
    """The only licence the prompt gives for saying anything about terrain."""

    def test_offered_for_where_the_day_ended(self):
        trip = _trip(stays=[_stay(DAY, "2026-08-24", campground_id=7)])
        self.assertEqual(_dossier(trip, elevations={7: 8196})["to"]["elevation_ft"],
                         8200)

    def test_never_offered_for_where_it_began(self):
        """Both ends would invite narrating a climb whose profile the model
        cannot see."""
        trip = _trip(stays=[_stay("2026-08-22", DAY, campground_id=7),
                            _stay(DAY, "2026-08-24", campground_id=9)])
        d = _dossier(trip, elevations={7: 8196, 9: 1200})
        self.assertNotIn("elevation_ft", d["from"])
        self.assertIn("elevation_ft", d["to"])

    def test_an_unknown_elevation_is_simply_absent(self):
        trip = _trip(stays=[_stay(DAY, "2026-08-24", campground_id=7)])
        self.assertNotIn("elevation_ft", _dossier(trip, elevations={})["to"])


class TestStatesCrossed(unittest.TestCase):
    """The fact that was nowhere in the trip record."""

    def _pings(self, *states):
        # One ping per state, in order; the stub resolves by longitude.
        return [{"lat": 40.0, "lng": i, "lon": i} for i, _ in enumerate(states)]

    def _with_gazetteer(self, states):
        seq = list(states)

        class Stub:
            @staticmethod
            def load(): pass

            @staticmethod
            def nearest_town(lat, lon):
                return {"state": seq[int(lon)]}
        return mock.patch.dict(sys.modules, {"nearest_town": Stub})

    def test_order_is_preserved_and_repeats_collapse(self):
        states = ["MD", "PA", "PA", "WV", "OH", "OH", "IN"]
        with self._with_gazetteer(states):
            self.assertEqual(R.states_crossed(self._pings(*states), samples=99),
                             ["MD", "PA", "WV", "OH", "IN"])

    def test_a_state_re_entered_later_is_listed_again(self):
        """Not a set: crossing back is part of the day's shape."""
        states = ["VA", "WV", "VA"]
        with self._with_gazetteer(states):
            self.assertEqual(R.states_crossed(self._pings(*states), samples=99),
                             ["VA", "WV", "VA"])

    def test_no_track_means_no_states_not_an_error(self):
        self.assertEqual(R.states_crossed([]), [])
        self.assertEqual(R.states_crossed(None), [])

    def test_a_host_with_no_gazetteer_just_loses_the_field(self):
        """The USB build and a fresh clone must still draft."""
        with mock.patch.dict(sys.modules, {"nearest_town": None}):
            self.assertEqual(R.states_crossed([{"lat": 1, "lon": 1}]), [])


class TestPlaceInTheTrip(unittest.TestCase):
    def test_the_day_is_numbered_within_the_trip(self):
        d = _dossier(_trip(), day_index=(2, 14))
        self.assertEqual((d["day_of_trip"], d["trip_days"]), (2, 14))

    def test_every_days_mileage_is_offered_in_order(self):
        """What lets the model say "the biggest driving day of the trip"
        without being told which day that was."""
        miles = [124, 520, 405]
        self.assertEqual(_dossier(_trip(), trip_miles=miles)["trip_miles_by_day"],
                         miles)


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
        # A batch takes minutes and the app writes to this file, so deltas
        # merge per-key against disk.
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
