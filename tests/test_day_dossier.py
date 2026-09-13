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
             trip_outline=None, day_index=None, day=DAY, track_known=True,
             day_times=None, home_pt=None, contexts=None, high_point_ft=None):
    return R.day_dossier(trip, day, driving or {}, elevations or {},
                         states, trip_outline, day_index, track_known,
                         day_times, home_pt, contexts, high_point_ft)


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

    def test_a_real_event_is_named_with_its_time(self):
        """The time is half the fact. Without it a single event reads as having
        filled the day and the first of several reads as the morning — AWH on
        trip 14's Ocean City, which ran 19:30 to 20:47 — AWH: "We didn't spend
        the day in Ocean City. We spent only a short part of the evening
        there."
        """
        self.assertEqual(self._full_day()["events"],
                         [{"name": "Alpine Visitor Center", "time": "10:00"}])

    def test_an_event_with_no_time_still_carries_its_name(self):
        trip = _trip(events=[{"date": DAY, "sort_date": DAY, "type": "event",
                              "name": "Somewhere"}])
        trip["timeline"] = trip["events"]
        self.assertEqual(_dossier(trip)["events"], [{"name": "Somewhere"}])

    def test_a_family_visit_is_named_by_its_label(self):
        self.assertEqual(self._full_day()["family_visits"], ["The Svendsens"])

    def test_a_waypoint_is_absent_entirely_not_even_counted(self):
        """AWH: "If a stop is interesting, it's my job to mark it as an event
        rather than a waypoint, not the model's job to reinterpret." A count
        could only be characterised by guessing what was at them — seven
        scenic overlooks and seven fuel stops are the same integer."""
        d = self._full_day()
        self.assertNotIn("waypoint_stops", d)
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

    def test_a_round_trip_carries_no_distance_at_all(self):
        """Flagged, but with no mileage and no driving time: on a day based at
        one campground the distance is the least interesting fact about it, and
        a figure in the dossier is a figure that ends up in the prose. A
        compass heading would be a fiction too."""
        trip = _trip(stays=[_stay("2026-08-22", "2026-08-25")])
        d = _dossier(trip, driving={DAY: {"miles": 54, "moving": "1h 57m",
                                          "round_trip": True}})
        self.assertTrue(d["round_trip"])
        for absent in ("miles", "driving_time", "heading"):
            self.assertNotIn(absent, d)

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

    def test_the_whole_trip_is_outlined_in_order(self):
        """Distance AND where each day slept. Mileage alone reached "the
        biggest driving day" but nothing about continuity — "a second day
        based at X", "the highest point of the trip" — which is what a day
        with no distance of its own has to be placed by."""
        outline = [{"day": 1, "miles": 124, "slept": "Rocky Gap"},
                   {"day": 2, "miles": None, "slept": "Moraine Park",
                    "elevation_ft": 8200}]
        self.assertEqual(_dossier(_trip(), trip_outline=outline)["trip_outline"],
                         outline)


class TestTripDays(unittest.TestCase):
    def test_every_date_the_trip_mentions(self):
        trip = _trip(stays=[{"start": "2026-08-19", "end": "2026-08-20"}],
                     events=[{"date": "2026-08-21"}])
        self.assertEqual(R.trip_days(trip),
                         ["2026-08-19", "2026-08-20", "2026-08-21"])

    def test_a_day_only_the_TIMELINE_names_still_counts(self):
        """An interior night of a split multi-night stay appears nowhere in the
        record, but the page puts a divider — and a write-up slot — on it."""
        trip = _trip(stays=[{"start": "2023-11-22", "end": "2023-11-26"}],
                     timeline=[{"sort_date": "2023-11-24"}])
        self.assertIn("2023-11-24", R.trip_days(trip))

    def test_the_day_the_trip_drove_home_still_counts(self):
        """`end` carries no timeline card on a trip that left the morning after
        its last night — the union is what keeps it."""
        trip = _trip(stays=[{"start": "2024-04-21", "end": "2024-04-22"}],
                     timeline=[{"sort_date": "2024-04-21"}])
        self.assertEqual(R.trip_days(trip), ["2024-04-21", "2024-04-22"])


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


class TestTheDayIsAnchoredOnTheBedsNotThePings(unittest.TestCase):
    """The fix for the most heavily rewritten entry in the library.

    OwnTracks suspends reporting while a device sits still, so the first ping
    of a day that began at home is routinely already miles away — on trip 90's
    first day it was the drive to work. Anchored on that ping, the departure
    circle formed around the office and the dossier reported a fourteen-hour
    span for a two-hour evening drive.
    """

    HOME = (38.93, -77.37)
    CAMP = (40.08, -76.90)

    def _pings(self):
        def p(tst, lat, lon):
            return {"tst": tst, "lat": lat, "lon": lon, "tz": "UTC"}
        return [
            p(1000, 38.96, -77.33),      # 07:10-ish, out at work
            p(2000, *self.HOME),         # home again all afternoon
            p(3000, 38.94, -77.34),      # leaving for good
            p(4000, 39.50, -77.10),      # on the road
            p(5000, *self.CAMP),         # arrived
        ]

    def test_the_departure_is_the_last_time_it_left_home(self):
        clock = R.day_clock(self._pings(), start_pt=self.HOME, end_pt=self.CAMP)
        self.assertEqual(clock["left_at"], "00:33")      # tst 2000, UTC
        self.assertEqual(clock["arrived_at"], "01:23")   # tst 5000

    def test_without_the_beds_the_commute_becomes_the_departure(self):
        """What the old behaviour was, kept as the fallback for a day whose
        beds can't be resolved: earlier is worse, but it is never invented."""
        clock = R.day_clock(self._pings())
        self.assertEqual(clock["left_at"], "00:16")      # tst 1000, the commute

    def test_home_is_the_anchor_only_on_the_first_and_last_day(self):
        trip = _trip(stays=[_stay("2026-08-19", "2026-08-21")])
        home = (38.93, -77.37)
        # Day 1: woke at home, slept at the campground.
        self.assertEqual(R.day_anchors(trip, "2026-08-19", home, (1, 3))[0], home)
        # Last day: woke at the campground, came home.
        self.assertEqual(R.day_anchors(trip, "2026-08-21", home, (3, 3))[1], home)
        # A mid-trip day with no stay is a gap in the record, not a night home.
        self.assertEqual(R.day_anchors(trip, "2026-08-25", home, (2, 3)),
                         (None, None))


class TestTheCompass(unittest.TestCase):
    """Cardinals get a 60-degree bucket, diagonals 30.

    People say "south" for a drive 28 degrees off south: AWH's note for the
    409-mile run to South Carolina (bearing 208) says "South", where an even
    eight-point split says southwest. The diagonals stay for the drives that
    really are diagonal — home to western Pennsylvania is 42 degrees off north
    and reads "northwest" to anyone who has driven it.
    """

    def _at(self, bearing):
        """A point that bearing-degrees away from a fixed origin."""
        import math
        lat0, lng0 = 39.0, -78.0
        d = math.radians(bearing)
        return (lat0 + 3 * math.cos(d), lng0 + 3 * math.sin(d) / math.cos(math.radians(lat0)))

    def test_a_drive_nearly_south_is_called_south(self):
        self.assertEqual(R._heading((39.0, -78.0), self._at(208)), "south")

    def test_a_genuinely_diagonal_drive_keeps_its_diagonal(self):
        self.assertEqual(R._heading((39.0, -78.0), self._at(318)), "northwest")

    def test_every_bucket_lands_where_it_should(self):
        """The diagonal index was off by one bucket when this was written, and
        a run home to the southeast came out "northeast"."""
        for bearing, want in ((0, "north"), (45, "northeast"), (95, "east"),
                              (123, "southeast"), (185, "south"),
                              (220, "southwest"), (270, "west"),
                              (310, "northwest"), (350, "north")):
            self.assertEqual(R._heading((39.0, -78.0), self._at(bearing)), want,
                             f"bearing {bearing}")


class TestHeadingOnTheDaysThatLeaveAndReturn(unittest.TestCase):
    """Every wrong compass word in the library was one of these two days.

    `_heading` needs a stay at both ends and those days have one, so the field
    was absent and the model guessed from the state list: a run to western
    Pennsylvania read "north" (northwest) and two runs home from the northwest
    read "south" (southeast).
    """

    HOME = (38.93, -77.37)

    def test_the_first_day_takes_its_heading_from_home(self):
        trip = _trip(stays=[_stay("2026-05-08", "2026-05-10",
                                  lat=41.30, lng=-80.20)])
        d = _dossier(trip, day="2026-05-08", day_index=(1, 3), home_pt=self.HOME)
        self.assertEqual(d["heading"], "northwest")

    def test_the_last_day_heads_home(self):
        trip = _trip(stays=[_stay("2026-05-08", "2026-05-10",
                                  lat=41.30, lng=-80.20)])
        d = _dossier(trip, day="2026-05-10", day_index=(3, 3), home_pt=self.HOME)
        self.assertEqual(d["heading"], "southeast")

    def test_no_home_configured_just_loses_the_field(self):
        trip = _trip(stays=[_stay("2026-05-08", "2026-05-10")])
        self.assertNotIn("heading",
                         _dossier(trip, day="2026-05-08", day_index=(1, 3)))


class TestWhatTheCampgroundSitsIn(unittest.TestCase):
    """Read off the campground record, never off the model's geography.

    This is the one kind of scene-setting the entries are allowed, which is
    why it has to be precise: a wrong river is worse than no river.
    """

    def test_the_water_and_the_park_come_off_the_note(self):
        ctx = R.campground_context(
            {"name": "Deep Bend Landing", "waterfront": "riverfront",
             "note": "Family-owned campground on the Satilla River."})
        self.assertEqual(ctx, {"waterfront": "riverfront",
                               "water": "Satilla River"})

    def test_a_dry_campground_is_never_given_water(self):
        """A lake named in the note of a campground that doesn't front one is
        a nearby lake, not this one's."""
        ctx = R.campground_context(
            {"name": "Pine Hollow", "waterfront": "not waterfront",
             "note": "Ten minutes from Raystown Lake."})
        self.assertNotIn("water", ctx)
        self.assertNotIn("waterfront", ctx)

    def test_a_name_never_runs_across_a_clause_boundary(self):
        """Without the clause bound, "...Boundary Campground. USFS Cherokee
        National Forest" parses as one four-word park name."""
        ctx = R.campground_context(
            {"name": "Indian Boundary Campground", "waterfront": "lakefront",
             "note": "Indian Boundary Campground. USFS Cherokee National Forest."})
        self.assertEqual(ctx.get("within"), "Cherokee National Forest")

    def test_the_campground_s_own_name_is_not_repeated_back(self):
        ctx = R.campground_context(
            {"name": "Clearwater Lake campground", "waterfront": "lakeview",
             "note": "Gate code required after 6pm."})
        self.assertEqual(ctx, {"waterfront": "lakeview"})

    def test_it_reaches_the_dossier_on_where_the_day_ENDED(self):
        trip = _trip(stays=[_stay("2026-08-22", "2026-08-24")])
        d = _dossier(trip, day="2026-08-23",
                     contexts={7: {"waterfront": "lakefront"}})
        self.assertEqual(d["to"]["waterfront"], "lakefront")
        self.assertNotIn("waterfront", d["from"])


class TestTheDayHighPoint(unittest.TestCase):
    """Where the day WENT, as against where it slept.

    A day spent on Trail Ridge Road near 12,000 feet was written up as "based
    at Moraine Park at 8,200 feet" — the elevation of the bed it left and came
    back to, the only height the dossier knew.
    """

    def setUp(self):
        # The DEM answers are cached by coordinate, so two tests over the same
        # made-up track would otherwise share one answer — which is the point
        # of the cache in the field and a trap in here.
        tmp = tempfile.mkdtemp()
        p = mock.patch.object(R, "ELEVATION_CACHE",
                              os.path.join(tmp, "elev.json"))
        p.start()
        self.addCleanup(p.stop)

    def _pings(self, n=8):
        return [{"tst": 100 * i, "lat": 40.0 + i / 100, "lon": -105.0,
                 "tz": "UTC"} for i in range(n)]

    def test_offered_when_it_clears_both_beds(self):
        with mock.patch.object(R, "_fetch_max_elevation_m", return_value=3700):
            feet = R.day_high_point_ft(self._pings(), bed_elevations=[8200])
        self.assertEqual(feet, 12100)

    def test_withheld_when_the_day_barely_rose_above_camp(self):
        """A figure in the dossier is a figure that ends up in the prose."""
        with mock.patch.object(R, "_fetch_max_elevation_m", return_value=2550):
            self.assertIsNone(
                R.day_high_point_ft(self._pings(), bed_elevations=[8200]))

    def test_a_host_with_no_network_simply_loses_the_field(self):
        with mock.patch.object(R, "_fetch_max_elevation_m", return_value=None):
            self.assertIsNone(R.day_high_point_ft(self._pings()))

    def test_a_day_with_almost_no_track_asks_nothing(self):
        with mock.patch.object(R, "_fetch_max_elevation_m") as fetch:
            self.assertIsNone(R.day_high_point_ft([{"tst": 1, "lat": 1, "lon": 1}]))
        fetch.assert_not_called()

    def test_samples_are_spaced_along_the_drive_not_by_ping(self):
        """Ping density is highest where the day STOPPED moving; an hour
        parked at a rest area would otherwise outweigh a mountain pass."""
        pings = ([{"tst": i, "lat": 40.0, "lon": -105.0} for i in range(20)]
                 + [{"tst": 100, "lat": 41.0, "lon": -105.0}])
        got = R._even_samples(pings, 5)
        self.assertEqual(len(got), 5)
        self.assertAlmostEqual(got[2][0], 40.5, places=2)


if __name__ == "__main__":
    unittest.main()
