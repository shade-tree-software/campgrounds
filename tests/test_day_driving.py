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
    _day_totals, _drive_days, _moving_seconds, _most_driven_trip,
    DRIVE_DAY_MIN_M, DRIVE_MOVING_MAX_LEG_S, DRIVE_MOVING_MIN_MPS,
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


def _split(pts, leg_row):
    """What `_trip_driving_by_day` derives for one day, without the cache."""
    whole = _day_totals(pts, TZ)[0]
    if leg_row is None:
        return {"miles": round(whole[1] / 1609.344), "local_miles": 0,
                "round_trip": True}
    return {"miles": round(leg_row[1] / 1609.344),
            "local_miles": round(max(0, whole[1] - leg_row[1]) / 1609.344),
            "round_trip": False}


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


class TestTheTwoSurfacesCannotDisagree(unittest.TestCase):
    """The trip page's headline figure for a day that went somewhere IS the
    stats page's figure for that day — not a second measurement of it.

    Reporting the whole day in both places looked equivalent but was not:
    across the library only 14% of shared days rounded to the same mileage,
    and trip 26's 2024-04-08 read 5 mi on the stats page against 160 mi on the
    timeline. So an A->B day now reports the LEG, with the extra split out as
    `local_miles`, and an A->A day — which the stats page drops entirely —
    reports the whole day and says "round trip"."""

    # A morning errand out of camp and back (5 mi each way), THEN a 20-mile
    # drive to the next campground. The anchor trimming clips the errand off
    # the leg — it re-enters the starting circle — so the leg is 20 and the
    # other 10 are local. A day with no wander at either end has leg == whole
    # and no local miles at all, which is why the fixture needs the loop.
    A_TO_B = [(0, 0), (300, 5), (600, 0), (900, 20), (1200, 20)]

    def test_an_a_to_b_day_reports_the_leg_not_the_whole_day(self):
        pts = _line(*self.A_TO_B)
        leg = _drive_days(pts, TZ)[0]
        got = _split(pts, leg)
        self.assertEqual(got["miles"], round(leg[1] / 1609.344))
        self.assertAlmostEqual(got["miles"], 20, delta=1)
        self.assertFalse(got["round_trip"])
        self.assertAlmostEqual(got["local_miles"], 10, delta=1)

    def test_leg_plus_local_accounts_for_the_whole_day(self):
        pts = _line(*self.A_TO_B)
        leg = _drive_days(pts, TZ)[0]
        whole = _day_totals(pts, TZ)[0]
        got = _split(pts, leg)
        self.assertEqual(got["miles"] + got["local_miles"],
                         round(whole[1] / 1609.344))

    def test_a_day_with_no_wander_has_no_local_miles(self):
        """leg == whole, so the divider reads exactly like the stats row."""
        pts = _line((0, 0), (600, 20), (1200, 40))
        got = _split(pts, _drive_days(pts, TZ)[0])
        self.assertEqual(got["local_miles"], 0)

    def test_an_a_to_a_day_reports_the_whole_day_and_says_so(self):
        pts = _line((0, 0), (900, 15), (1800, 0))
        self.assertEqual(_drive_days(pts, TZ), [])     # the stats page drops it
        got = _split(pts, None)
        self.assertTrue(got["round_trip"])
        self.assertEqual(got["local_miles"], 0)
        self.assertAlmostEqual(got["miles"], 30, delta=1)

    def test_local_miles_can_never_go_negative(self):
        """The leg is a sub-span of the day so it cannot exceed it, but the
        guard is what stops a rounding edge printing "+ -1 local"."""
        for fixture in (self.A_TO_B, [(i * 600, i * 8) for i in range(10)]):
            pts = _line(*fixture)
            leg = _drive_days(pts, TZ)[0]
            self.assertGreaterEqual(_split(pts, leg)["local_miles"], 0)


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


class TestMostDrivenTrip(unittest.TestCase):
    """The stats page's "Most miles driven" record.

    Driven off injected `prepared` inputs rather than the on-disk route cache,
    so the ranking rule is pinned without depending on the library's data."""

    @staticmethod
    def _prepared(trips):
        """`trips` as `{id: [(meters, ...), ...]}` of day_totals rows."""
        by_id = {tid: {"id": tid, "number": tid, "summary": f"Trip {tid}"}
                 for tid in trips}
        entries = {tid: {"day_totals": [[f"2026-08-{i + 1:02d}", m, 3600]
                                        for i, m in enumerate(rows)]}
                   for tid, rows in trips.items()}
        return by_id, entries

    def test_picks_the_trip_with_the_most_total_mileage(self):
        got = _most_driven_trip(self._prepared({
            1: [500_000, 500_000],          # 1,000 km
            2: [900_000],                   #   900 km
            3: [100_000, 100_000, 100_000],  #  300 km
        }))
        self.assertEqual(got["trip_id"], 1)
        self.assertAlmostEqual(got["miles"], round(1_000_000 / 1609.344))

    def test_a_trip_of_only_round_trip_days_still_counts(self):
        """The reason it sums `day_totals` and not `days`: a week of day
        trips out of one campground has no A-to-B legs at all, and summing
        legs would score it zero."""
        got = _most_driven_trip(self._prepared({
            1: [80_000] * 6,                # 480 km of excursions, no legs
            2: [200_000],
        }))
        self.assertEqual(got["trip_id"], 1)

    def test_days_under_the_minimum_do_not_accumulate(self):
        """A fortnight parked at camp is not a driving record."""
        got = _most_driven_trip(self._prepared({
            1: [DRIVE_DAY_MIN_M - 1] * 30,
            2: [50_000],
        }))
        self.assertEqual(got["trip_id"], 2)

    def test_none_when_no_trip_has_a_track(self):
        self.assertIsNone(_most_driven_trip(({}, {})))
        self.assertIsNone(_most_driven_trip(self._prepared({1: []})))

    def test_a_trip_missing_from_the_trip_list_is_skipped(self):
        """The route cache can hold an entry for a trip the caller filtered
        out (a home-only trip, for a non-admin)."""
        by_id, entries = self._prepared({1: [50_000]})
        entries[99] = {"day_totals": [["2026-08-01", 9_000_000, 3600]]}
        self.assertEqual(_most_driven_trip((by_id, entries))["trip_id"], 1)

    def test_a_malformed_row_is_skipped_not_raised(self):
        by_id, entries = self._prepared({1: [50_000]})
        entries[1]["day_totals"].insert(0, ["2026-08-01"])   # short row
        self.assertEqual(_most_driven_trip((by_id, entries))["trip_id"], 1)

    def test_carries_what_the_template_renders(self):
        got = _most_driven_trip(self._prepared({7: [50_000]}))
        self.assertEqual(
            set(got) & {"trip_id", "number", "summary", "miles"},
            {"trip_id", "number", "summary", "miles"})
