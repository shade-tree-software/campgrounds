"""Per-day driving: what a trip's day dividers report, and how it's measured.

Two different questions share one pass over the track:

  - `_drive_days` measures a LEG — leaving where the day started to reaching
    where it ended. Right for ranking the longest drives, but degenerate for a
    day that ends where it began, so those days are dropped entirely. Across
    the library that silently omitted 68 days and ~3,000 miles: every park day
    run out of a base camp.
  - `_day_totals` measures the WHOLE DAY, so every day the track covers gets a
    number. That is what "miles driven that day" means on a trip page.

Both take driving time from `_moving_seconds`, so the stats page and the trip
page can't disagree about what an hour at the wheel is.

Run from the project root with the venv active:

    python -m unittest tests.test_day_driving -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ekko_trips_app import (  # noqa: E402
    _day_totals, _drive_days, _moving_seconds,
    DRIVE_MOVING_MAX_LEG_S, DRIVE_MOVING_MIN_MPS,
)

TZ = "America/Denver"
# 2026-08-27 08:00 local (14:00 UTC).
T0 = 1787839200
# Degrees of latitude per mile, near enough for fixtures.
MI = 1.0 / 69.0


def _ping(offset_s, mile_north, tz=TZ):
    return {"tst": T0 + offset_s, "lat": 40.0 + mile_north * MI,
            "lon": -105.8, "tz": tz}


def _line(*pairs):
    """Pings from (seconds_from_T0, miles_north) pairs."""
    return [_ping(s, m) for s, m in pairs]


class TestMovingSeconds(unittest.TestCase):

    def test_a_fast_leg_counts_in_full(self):
        # 1 mile in 60 s — unambiguously moving.
        self.assertEqual(_moving_seconds(_line((0, 0), (60, 1))), 60)

    def test_a_slow_leg_does_not_count(self):
        # 1 mile in 2 hours — walking pace, not driving.
        self.assertEqual(_moving_seconds(_line((0, 0), (7200, 1))), 0)

    def test_a_long_leg_is_clamped_not_trusted(self):
        """The trip-12 case: a six-hour logging gap covering 31 miles averages
        just over walking pace and used to be credited whole."""
        legs = _line((0, 0), (6 * 3600, 31))
        self.assertEqual(_moving_seconds(legs), DRIVE_MOVING_MAX_LEG_S)

    def test_a_long_leg_is_not_dropped_either(self):
        """Dropping over-corrected on sparsely-logged old trips, where real
        highway driving lives inside long legs."""
        self.assertGreater(_moving_seconds(_line((0, 0), (6 * 3600, 31))), 0)

    def test_a_leg_just_under_the_cap_is_untouched(self):
        dt = DRIVE_MOVING_MAX_LEG_S - 1
        self.assertEqual(_moving_seconds(_line((0, 0), (dt, 10))), dt)

    def test_zero_and_negative_intervals_are_skipped(self):
        dup = [_ping(0, 0), _ping(0, 1), _ping(60, 2)]
        self.assertEqual(_moving_seconds(dup), 60)

    def test_a_single_ping_has_no_moving_time(self):
        self.assertEqual(_moving_seconds([_ping(0, 0)]), 0)
        self.assertEqual(_moving_seconds([]), 0)

    def test_the_speed_gate_is_the_documented_one(self):
        """A leg exactly at the threshold counts; well under does not."""
        fast = _line((0, 0), (100, 100 * DRIVE_MOVING_MIN_MPS / 1609.344 * 1.01))
        self.assertEqual(_moving_seconds(fast), 100)


class TestDayTotals(unittest.TestCase):

    def test_every_day_with_movement_is_reported(self):
        pts = _line((0, 0), (600, 10), (1200, 20))
        rows = _day_totals(pts, TZ)
        self.assertEqual(len(rows), 1)
        day, meters, moving = rows[0]
        self.assertEqual(day, "2026-08-27")
        self.assertAlmostEqual(meters / 1609.344, 20, delta=0.5)
        self.assertEqual(moving, 1200)

    def test_a_loop_day_is_reported_here_but_not_by_drive_days(self):
        """The whole reason this exists: out and back to the same campground.
        `_drive_days` drops it (the day never leaves its starting circle);
        a day-by-day readout must not."""
        out_and_back = _line((0, 0), (900, 15), (1800, 0))
        self.assertEqual(_drive_days(out_and_back, TZ), [])
        rows = _day_totals(out_and_back, TZ)
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0][1] / 1609.344, 30, delta=1.0)

    def test_distance_is_the_path_not_the_displacement(self):
        """30 miles driven, zero net displacement."""
        rows = _day_totals(_line((0, 0), (900, 15), (1800, 0)), TZ)
        self.assertGreater(rows[0][1], 40000)   # ~48 km of path

    def test_a_day_parked_at_camp_reports_almost_nothing(self):
        """Reported rather than dropped; the caller decides it's not worth
        printing, so the threshold lives in one place."""
        jitter = [_ping(i * 300, i * 0.002) for i in range(12)]
        rows = _day_totals(jitter, TZ)
        self.assertEqual(len(rows), 1)
        self.assertLess(rows[0][1], 1609)

    def test_days_split_by_the_pings_own_timezone(self):
        """A trip that crosses a zone line splits its days where the driver's
        clock did — the same rule everything else here buckets by."""
        pts = [_ping(0, 0), _ping(3600, 10),
               # 23:30 Denver on the 27th is 00:30 Chicago on the 28th.
               {"tst": T0 + 55800, "lat": 41.0, "lon": -101.0,
                "tz": "America/Chicago"},
               {"tst": T0 + 56400, "lat": 41.1, "lon": -101.0,
                "tz": "America/Chicago"}]
        self.assertEqual([r[0] for r in _day_totals(pts, TZ)],
                         ["2026-08-27", "2026-08-28"])

    def test_a_day_with_one_ping_is_skipped(self):
        self.assertEqual(_day_totals([_ping(0, 0)], TZ), [])

    def test_empty_input(self):
        self.assertEqual(_day_totals([], TZ), [])

    def test_rows_come_out_in_date_order(self):
        pts = ([_ping(i * 600, i) for i in range(3)]
               + [_ping(86400 + i * 600, 50 + i) for i in range(3)])
        self.assertEqual([r[0] for r in _day_totals(pts, TZ)],
                         ["2026-08-27", "2026-08-28"])


class TestBothMeasuresAgreeOnATravelDay(unittest.TestCase):
    """On a day that actually goes somewhere the two should be close; they
    only diverge where the leg framing breaks down."""

    def test_a_straight_travel_day_matches_within_a_few_percent(self):
        pts = _line(*[(i * 600, i * 8) for i in range(10)])
        leg = _drive_days(pts, TZ)
        whole = _day_totals(pts, TZ)
        self.assertEqual(len(leg), 1)
        self.assertEqual(len(whole), 1)
        self.assertAlmostEqual(leg[0][1], whole[0][1],
                               delta=whole[0][1] * 0.05)

    def test_driving_time_uses_the_same_helper_on_both(self):
        pts = _line(*[(i * 600, i * 8) for i in range(10)])
        self.assertEqual(_drive_days(pts, TZ)[0][3], _moving_seconds(pts))


if __name__ == "__main__":
    unittest.main()
