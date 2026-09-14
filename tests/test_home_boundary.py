"""The home departure is only a departure if the track actually left home.

`_find_home_boundary_tsts` reports the away streak's first ping as the moment
the trip left home. Nothing in that definition checks the ping is anywhere near
home -- it is one only when the track begins at home, which is the normal case
and was silently assumed.

It stops being true when somebody else drives the EKKO out. Their phone isn't
reporting, the trip's `bad_track_windows` carves those days away, and the first
surviving ping is hundreds of miles down the road days later. Trip 58 left on a
Tuesday and its earliest ping is Friday 12:39 at Royersford, 131 miles out; the
home card printed that as the Tuesday departure. Trip 47 does the same thing
across a Thursday-to-Saturday gap.

The guard is a DATE test, not a distance one, and the difference matters. The
ordinary failure is OwnTracks going quiet over the real departure, which leaves
the first away ping tens of miles out on the RIGHT day -- trip 2 after a
213-minute silence (26 mi), trip 5 with nothing between home at 10:28 and camp
at 21:31 (46 mi). Those times are late, but the day is right and the drive is
real; a distance threshold separating them from the driven-out trips would have
to sit somewhere between 2.3 and 26 miles with nothing to anchor it. A wrong
DAY is unambiguous.

    python -m unittest tests.test_home_boundary -v
"""

import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ekko_trips_app as A  # noqa: E402

HOME = (38.929648, -77.367182)
EAST = timezone(timedelta(hours=-4))


def _tst(day, hh, mm):
    y, m, d = (int(x) for x in day.split("-"))
    return int(datetime(y, m, d, hh, mm, tzinfo=EAST).timestamp())


def _ping(day, hh, mm, lat, lon):
    return {"tst": _tst(day, hh, mm), "lat": lat, "lon": lon}


def _away_run(day, start_hh, lat, lon, hours=3):
    """A stationary away-from-home run long enough to clear the 1-hour lock.

    Stepped in half hours off a base timestamp rather than by incrementing the
    hour field, so a run starting in the evening can't walk past 23:00."""
    base = _tst(day, start_hh, 0)
    return [{"tst": base + n * 1800, "lat": lat, "lon": lon}
            for n in range(hours * 2 + 1)]


class TestDepartureOnALaterDay(unittest.TestCase):
    """Trip 58's shape: the track starts days late and far from home."""

    def setUp(self):
        # Nothing on the Tuesday or Wednesday -- the EKKO was driven out by
        # someone whose phone wasn't reporting. The first ping is Friday, in
        # Pennsylvania, and the drive home follows it.
        self.points = (_away_run("2025-05-23", 12, 40.1846, -75.5407)
                       + [_ping("2025-05-23", 19, 25, *HOME)])

    def test_departure_is_withheld(self):
        dep, arr = A._find_home_boundary_tsts(
            self.points, HOME, trip_start_date="2025-05-20")
        self.assertIsNone(
            dep, "a Friday ping 131 miles out is not a Tuesday home departure")
        self.assertIsNotNone(arr, "the arrival is still observed")

    def test_arrival_is_untouched(self):
        """The arrival is the first at-home ping after the streak, so it is
        anchored at home by construction and the guard must not touch it."""
        _, guarded = A._find_home_boundary_tsts(
            self.points, HOME, trip_start_date="2025-05-20")
        _, plain = A._find_home_boundary_tsts(self.points, HOME)
        self.assertEqual(guarded, plain)
        self.assertEqual(
            datetime.fromtimestamp(guarded, EAST).strftime("%H:%M"), "19:25")

    def test_without_a_start_date_nothing_changes(self):
        """Callers that pass no date get the original behaviour, byte for
        byte -- the guard is opt-in, so no consumer changes by accident."""
        self.assertEqual(
            A._find_home_boundary_tsts(self.points, HOME),
            A._find_home_boundary_tsts(self.points, HOME, trip_start_date=None))


class TestDepartureOnTheStartDay(unittest.TestCase):
    """Trips 2 and 5: a reporting gap over the real departure. The time is
    late, but it belongs to the day the trip left, and the drive is real."""

    def test_a_far_away_first_ping_on_the_right_day_survives(self):
        points = ([_ping("2022-09-09", 9, 1, *HOME)]
                  # 213 minutes of silence, then already 26 miles out
                  + _away_run("2022-09-09", 18, 39.2000, -77.0000)
                  + [_ping("2022-09-10", 21, 0, *HOME)])
        dep, _ = A._find_home_boundary_tsts(
            points, HOME, trip_start_date="2022-09-09")
        self.assertIsNotNone(
            dep, "a late departure on the correct day is still a departure")
        self.assertEqual(
            datetime.fromtimestamp(dep, EAST).date().isoformat(), "2022-09-09")

    def test_an_ordinary_trip_is_unaffected(self):
        """The overwhelming majority: the track leaves home on the start date
        and the first away ping is about a mile out."""
        points = ([_ping("2026-07-03", 13, 30, *HOME)]
                  + _away_run("2026-07-03", 14, 38.9500, -77.3500)
                  + [_ping("2026-07-05", 18, 0, *HOME)])
        with_guard = A._find_home_boundary_tsts(
            points, HOME, trip_start_date="2026-07-03")
        without = A._find_home_boundary_tsts(points, HOME)
        self.assertEqual(with_guard, without)
        self.assertIsNotNone(with_guard[0])


class TestLocalDateHelper(unittest.TestCase):
    def test_resolves_in_the_named_zone(self):
        """Evening in Denver is already the next day in UTC -- the guard
        compares LOCAL dates, so it has to resolve them in the home zone."""
        tst = int(datetime(2026, 8, 28, 22, 0,
                           tzinfo=timezone(timedelta(hours=-6))).timestamp())
        self.assertEqual(
            A._local_date_of_tst(tst, "America/Denver"), "2026-08-28")

    def test_none_in_none_out(self):
        self.assertIsNone(A._local_date_of_tst(None, "America/New_York"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
