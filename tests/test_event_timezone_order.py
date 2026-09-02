"""Events must be ordered by the instant they happened, not by their wall clock.

A trip that crosses a time-zone line westward sets the clock BACK an hour, so a
stop that happened later can carry an earlier "HH:MM" stamp than one that came
before it. Sorting those strings puts the day in the wrong order. Trip 95 hit
this for real on 2026-08-23: the Macklin Bay overlook (08:47 CDT, Hitchcock
County NE) precedes the Benkelman gas stop (08:35 MDT) by 44 minutes, and the
timeline showed them backwards. Eastward crossings hide the bug — the clock
jumps forward, which happens to preserve the order.

These tests pin three things:

  1. the westward crossing sorts by true instant, on the stored `events` array
     (which photo indices are keyed on) and on the displayed `timeline` alike;
  2. a trip whose events carry NO zone is ordered exactly as the old naive sort
     ordered it — that no-op property is what made this safe to apply to the
     whole library;
  3. zone-crossing never moves an event to a neighbouring DAY, because a
     timeline day is a local day.

Run from the project root with the venv active:

    python -m unittest tests.test_event_timezone_order -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import trips  # noqa: E402

CENTRAL = "America/Chicago"
MOUNTAIN = "America/Denver"
EASTERN = "America/New_York"


def _event(name, date, time, tz=""):
    return {"date": date, "time": time, "end_time": "", "name": name,
            "description": "", "location": "", "locale": "", "state": "",
            "waypoint": True, "family_id": None, "needs_vetting": False,
            "tz": tz}


def _names(trip, date=None):
    """Event names in timeline order, optionally limited to one day."""
    return [i["name"] for i in trip["timeline"]
            if i["type"] == "event" and (date is None or i["sort_date"] == date)]


class TestWestwardCrossing(unittest.TestCase):
    """The real trip-95 case: a later stop wearing an earlier wall clock."""

    # Macklin Bay is 44 minutes AFTER Sinclair in real time despite reading
    # 12 minutes earlier on the clock.
    EVENTS = [
        _event("Sinclair Gas", "2026-08-23", "08:35", MOUNTAIN),
        _event("Macklin Bay", "2026-08-23", "08:47", CENTRAL),
    ]

    def test_timeline_orders_by_instant(self):
        trip = trips._make_trip(1, [], "", [dict(e) for e in self.EVENTS])
        self.assertEqual(_names(trip), ["Macklin Bay", "Sinclair Gas"])

    def test_naive_sort_would_get_it_wrong(self):
        """Guards the test itself: without zones this ordering is the reverse,
        so a passing test above is really exercising the zone logic."""
        naive = [dict(e, tz="") for e in self.EVENTS]
        trip = trips._make_trip(1, [], "", naive)
        self.assertEqual(_names(trip), ["Sinclair Gas", "Macklin Bay"])

    def test_storage_sort_agrees_with_timeline(self):
        """`_sort_events` drives photo-directory numbering, so it must use the
        same rule as the display order or the two disagree about index N."""
        events = [dict(e) for e in self.EVENTS]
        trips._sort_events(events)
        self.assertEqual([e["name"] for e in events],
                         ["Macklin Bay", "Sinclair Gas"])

    def test_eastward_crossing_already_reads_in_order(self):
        """The same pair driven the other way: the clock jumps forward, so the
        naive order was already right and must stay right."""
        events = [
            _event("Macklin Bay", "2026-08-23", "08:47", MOUNTAIN),
            _event("Sinclair Gas", "2026-08-23", "10:35", CENTRAL),
        ]
        trip = trips._make_trip(1, [], "", events)
        self.assertEqual(_names(trip), ["Macklin Bay", "Sinclair Gas"])


class TestNoOpWithoutZones(unittest.TestCase):
    """A trip carrying no zones must sort exactly as it always did."""

    def test_unzoned_events_keep_wall_clock_order(self):
        events = [_event("C", "2026-05-02", "18:00"),
                  _event("A", "2026-05-02", "07:15"),
                  _event("B", "2026-05-02", "12:30")]
        trip = trips._make_trip(1, [], "", events)
        self.assertEqual(_names(trip), ["A", "B", "C"])

    def test_untimed_event_still_sorts_at_noon(self):
        events = [_event("morning", "2026-05-02", "09:00"),
                  _event("untimed", "2026-05-02", ""),
                  _event("evening", "2026-05-02", "17:00")]
        trip = trips._make_trip(1, [], "", events)
        self.assertEqual(_names(trip), ["morning", "untimed", "evening"])

    def test_unzoned_events_ride_the_reference_zone(self):
        """A trip where only SOME events carry a zone: the bare ones are read
        in the reference zone, so they interleave correctly rather than being
        treated as UTC (which would fling them hours away)."""
        events = [_event("zoned 09:00 MDT", "2026-05-02", "09:00", MOUNTAIN),
                  _event("bare 08:00", "2026-05-02", "08:00"),
                  _event("bare 10:00", "2026-05-02", "10:00")]
        trip = trips._make_trip(1, [], "", events)
        self.assertEqual(_names(trip),
                         ["bare 08:00", "zoned 09:00 MDT", "bare 10:00"])


class TestDayGroupingIsPreserved(unittest.TestCase):
    """An offset must never migrate an event onto a neighbouring day's card."""

    def test_late_and_early_events_stay_on_their_stored_dates(self):
        events = [_event("late on the 1st", "2026-05-01", "23:30", EASTERN),
                  _event("early on the 2nd", "2026-05-02", "00:30", MOUNTAIN)]
        trip = trips._make_trip(1, [], "", events)
        self.assertEqual(_names(trip, "2026-05-01"), ["late on the 1st"])
        self.assertEqual(_names(trip, "2026-05-02"), ["early on the 2nd"])


class TestZoneLabelling(unittest.TestCase):
    """Times are labelled only when the trip actually spans several zones."""

    def test_single_zone_trip_is_not_labelled(self):
        events = [_event("a", "2026-08-23", "09:00", MOUNTAIN),
                  _event("b", "2026-08-23", "11:00", MOUNTAIN)]
        trip = trips._make_trip(1, [], "", events)
        self.assertFalse(trip["multi_timezone"])

    def test_multi_zone_trip_is_labelled(self):
        events = [_event("a", "2026-08-23", "08:47", CENTRAL),
                  _event("b", "2026-08-23", "08:35", MOUNTAIN)]
        trip = trips._make_trip(1, [], "", events)
        self.assertTrue(trip["multi_timezone"])
        self.assertEqual([i["tz_abbr"] for i in trip["timeline"]], ["CDT", "MDT"])

    def test_same_abbreviation_is_not_a_distinction(self):
        """Two different IANA zones that both print MDT tell a reader nothing,
        so they must not switch the label on."""
        events = [_event("a", "2026-08-23", "09:00", MOUNTAIN),
                  _event("b", "2026-08-23", "11:00", "America/Boise")]
        trip = trips._make_trip(1, [], "", events)
        self.assertTrue(all(i["tz_abbr"] == "MDT" for i in trip["timeline"]))
        self.assertFalse(trip["multi_timezone"])

    def test_abbreviation_follows_the_date_across_dst(self):
        winter = trips.tz_abbrev("2026-12-15", "09:00", MOUNTAIN)
        summer = trips.tz_abbrev("2026-08-15", "09:00", MOUNTAIN)
        self.assertEqual((winter, summer), ("MST", "MDT"))


class TestDegradesSafely(unittest.TestCase):
    """Malformed or missing inputs fall back rather than raising."""

    def test_unknown_zone_falls_back_to_the_wall_clock(self):
        events = [_event("a", "2026-08-23", "09:00", "Not/AZone"),
                  _event("b", "2026-08-23", "11:00", "Not/AZone")]
        trip = trips._make_trip(1, [], "", events)
        self.assertEqual(_names(trip), ["a", "b"])
        self.assertEqual([i["tz_abbr"] for i in trip["timeline"]], ["", ""])

    def test_garbage_time_sorts_at_noon(self):
        self.assertEqual(trips._minutes_of_day("25:99"), 720)
        self.assertEqual(trips._minutes_of_day(None), 720)
        self.assertEqual(trips._minutes_of_day(""), 720)

    def test_reference_zone_of_an_unzoned_trip_is_blank(self):
        self.assertEqual(trips.reference_timezone(
            [_event("a", "2026-08-23", "09:00")]), "")


if __name__ == "__main__":
    unittest.main()
