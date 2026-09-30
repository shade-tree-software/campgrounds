"""Day numbers, day counts and "stayed" durations on the trip page.

The day dividers lead with "Day N" and carry the day's stops and photos, and
each stop says how long it lasted instead of when it ended. None of this
needs real trip data, so the fixtures here are built by hand.

    python -m unittest tests.test_timeline_days -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ekko_trips_app as A  # noqa: E402


def _stay(idx, start, end, copy_num=1, sort_date=None, photos=0):
    return {"type": "stay", "idx": idx, "sort_date": sort_date or start,
            "start": start, "end": end, "copy_num": copy_num,
            "photos": [{}] * photos}


def _event(idx, day):
    return {"type": "event", "idx": idx, "sort_date": day}


class TestStayed(unittest.TestCase):
    def test_hours_and_minutes(self):
        self.assertEqual(A._stayed("11:10", "12:50"), "1h 40m")

    def test_under_an_hour(self):
        self.assertEqual(A._stayed("13:40", "13:52"), "12m")

    def test_minutes_are_padded_like_the_drive_chip(self):
        self.assertEqual(A._stayed("09:00", "10:05"), "1h 05m")

    def test_a_stop_past_midnight_wraps_instead_of_going_negative(self):
        self.assertEqual(A._stayed("22:40", "00:25"), "1h 45m")

    def test_nothing_rather_than_a_measured_looking_zero(self):
        for start, end in (("10:00", ""), ("", "10:00"), ("10:00", "10:00"),
                           ("10:00", None), ("junk", "11:00"), ("25:00", "26:00")):
            self.assertEqual(A._stayed(start, end), "", (start, end))


class TestDayNumbers(unittest.TestCase):
    def test_numbered_from_the_first_day(self):
        trip = {"start": "2025-10-02", "end": "2025-10-04", "timeline": [
            _stay(0, "2025-10-02", "2025-10-04"),
            _event(0, "2025-10-03"),
        ]}
        days, total = A._timeline_days(trip, {})
        self.assertEqual({d: v["num"] for d, v in days.items()},
                         {"2025-10-02": 1, "2025-10-03": 2, "2025-10-04": 3})
        self.assertEqual(total, 3)

    def test_a_day_with_no_cards_leaves_a_gap_rather_than_renumbering(self):
        # A three-night stay with nothing on its middle days: the day they
        # left is still Day 4, not Day 2.
        trip = {"start": "2025-06-01", "end": "2025-06-04", "timeline": [
            _stay(0, "2025-06-01", "2025-06-04"),
        ]}
        days, total = A._timeline_days(trip, {})
        self.assertEqual([v["num"] for v in days.values()], [1, 4])
        self.assertEqual(total, 4)

    def test_the_homeward_day_gets_a_number(self):
        # It has no card of its own; the template emits its divider after the
        # loop, and the picker needs it too.
        trip = {"start": "2025-10-02", "end": "2025-10-03", "timeline": [
            _stay(0, "2025-10-02", "2025-10-03"),
        ]}
        days, _ = A._timeline_days(trip, {})
        self.assertIn("2025-10-03", days)

    def test_an_event_before_the_first_campspot_is_day_one(self):
        trip = {"start": "2025-10-02", "end": "2025-10-03", "timeline": [
            _event(0, "2025-10-01"),
            _stay(0, "2025-10-02", "2025-10-03"),
        ]}
        days, total = A._timeline_days(trip, {})
        self.assertEqual(days["2025-10-01"]["num"], 1)
        self.assertEqual(days["2025-10-02"]["num"], 2)
        self.assertEqual(total, 3)

    def test_days_come_back_in_timeline_order(self):
        trip = {"start": "2025-10-02", "end": "2025-10-04", "timeline": [
            _event(0, "2025-10-02"), _event(1, "2025-10-03"),
            _stay(0, "2025-10-03", "2025-10-04"),
        ]}
        days, _ = A._timeline_days(trip, {})
        self.assertEqual(list(days), ["2025-10-02", "2025-10-03", "2025-10-04"])

    def test_an_empty_trip_has_no_days(self):
        self.assertEqual(A._timeline_days({"timeline": []}, {}), ({}, 0))


class TestDayCounts(unittest.TestCase):
    def test_stops_are_events_plus_campspots_arrived_at(self):
        trip = {"start": "2025-10-02", "end": "2025-10-04", "timeline": [
            _event(0, "2025-10-02"), _event(1, "2025-10-02"),
            _stay(0, "2025-10-02", "2025-10-04", copy_num=1),
            _event(2, "2025-10-03"),
            # The second night of a split stay is the same campspot, not
            # another stop.
            _stay(0, "2025-10-02", "2025-10-04", copy_num=2, sort_date="2025-10-03"),
        ]}
        days, _ = A._timeline_days(trip, {})
        self.assertEqual(days["2025-10-02"]["stops"], 3)
        self.assertEqual(days["2025-10-03"]["stops"], 1)

    def test_photos_are_the_ones_on_that_days_cards(self):
        trip = {"start": "2025-10-02", "end": "2025-10-03", "timeline": [
            _event(0, "2025-10-02"),
            _stay(0, "2025-10-02", "2025-10-03", photos=5),
            {"type": "road", "idx": "2025-10-02", "sort_date": "2025-10-02",
             "photos": [{}, {}]},
            _event(1, "2025-10-03"),
        ]}
        days, _ = A._timeline_days(trip, {0: [{}] * 6, 1: []})
        self.assertEqual(days["2025-10-02"]["photos"], 13)
        self.assertEqual(days["2025-10-03"]["photos"], 0)


if __name__ == "__main__":
    unittest.main()
