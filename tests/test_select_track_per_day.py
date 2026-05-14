"""Unit tests for _select_track_per_day — the per-day primary/alt tid
selector for trip GPS tracks. Pure-function tests; no Flask context
needed, no network, no cache files.

Run from the project root with the venv active:

    python -m unittest tests.test_select_track_per_day -v

Cases covered (letters match the algorithm doc in
_select_track_per_day's docstring):

  - A: override wins (both 'primary' and 'alt')
  - B: only one tid has pings → that tid wins (the existing gap-fill case)
  - C: neither tid has pings → no contribution, prev_choice records
  - D-i:   one tid encountered an anchor, the other didn't
  - D-ii:  both encountered → earliest-tst wins; tie → primary
  - D-iii: neither encountered → inherit previous day
  - D-iv:  first day no encounter, home set → farther-from-home wins
  - D-v:   first day no encounter, no home → primary
  - Multi-day inheritance carrying across anchor-less days
  - Midnight-boundary bucketing using the ping's `tz` field
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ekko_trips_app import _select_track_per_day, _local_date_of_ping


# Reston, VA — used as a generic "home" coordinate. Day-1 fallback uses
# this when present.
HOME = (38.9296, -77.3672)

# A few sample anchor coords spaced across the country so we can tell
# them apart from home / from each other.
ANCHOR_BOONSBORO_MD = (39.5328, -77.6208)   # ~80 km NW of home
ANCHOR_OUTER_BANKS = (35.7000, -75.4900)    # ~470 km SE of home
ANCHOR_HARPERS_FERRY = (39.3195, -77.7131)  # ~70 km W of home


def _ping(tst, lat, lon, tz="America/New_York"):
    """Build a minimal ping dict matching what _enrich_with_timezone produces."""
    return {"tst": tst, "lat": lat, "lon": lon, "tz": tz}


def _epoch_for_local(date_iso, hour=12, minute=0):
    """Return a UTC epoch second whose America/New_York local date is
    `date_iso` at the given hour. Uses EDT (UTC-4) so the math is
    stable for our August test dates."""
    import datetime as dt
    y, m, d = (int(x) for x in date_iso.split("-"))
    # EDT = UTC-4 in August; subtract 4 hours-worth of seconds to push
    # local 12:00 to UTC 16:00.
    local = dt.datetime(y, m, d, hour, minute)
    utc = local + dt.timedelta(hours=4)
    return int(utc.replace(tzinfo=dt.timezone.utc).timestamp())


class TestSelectTrackPerDay(unittest.TestCase):

    # ── A: overrides ─────────────────────────────────────────────────

    def test_override_primary_wins_even_when_alt_only_has_pings(self):
        """An admin-set override beats every heuristic, including the
        'only one tid has pings' shortcut."""
        d = "2025-08-02"
        chosen, choices = _select_track_per_day(
            primary_points=[],
            alt_points=[_ping(_epoch_for_local(d, 14), 39.0, -77.5)],
            anchors=[],
            home=HOME,
            trip_start=d, trip_end=d,
            tid_overrides={d: "primary"},
        )
        self.assertEqual(chosen, [])  # primary had nothing today
        self.assertEqual(choices, {d: "override:primary"})

    def test_override_alt_returns_alt_pings(self):
        d = "2025-08-02"
        alt_ping = _ping(_epoch_for_local(d, 14), 39.0, -77.5)
        chosen, choices = _select_track_per_day(
            primary_points=[_ping(_epoch_for_local(d, 10), 38.9, -77.4)],
            alt_points=[alt_ping],
            anchors=[],
            home=HOME,
            trip_start=d, trip_end=d,
            tid_overrides={d: "alt"},
        )
        self.assertEqual(chosen, [alt_ping])
        self.assertEqual(choices, {d: "override:alt"})

    def test_unknown_override_value_ignored(self):
        """A garbage value in tid_overrides falls through to the heuristic."""
        d = "2025-08-02"
        p = _ping(_epoch_for_local(d, 10), 38.9, -77.4)
        chosen, choices = _select_track_per_day(
            primary_points=[p], alt_points=[], anchors=[], home=HOME,
            trip_start=d, trip_end=d,
            tid_overrides={d: "garbage"},
        )
        self.assertEqual(chosen, [p])
        self.assertEqual(choices, {d: "primary"})

    # ── B: only-one-tid-has-pings (gap-fill) ─────────────────────────

    def test_only_primary_has_pings(self):
        d = "2025-08-02"
        p = _ping(_epoch_for_local(d, 10), 38.9, -77.4)
        chosen, choices = _select_track_per_day(
            primary_points=[p], alt_points=[],
            anchors=[], home=HOME, trip_start=d, trip_end=d,
        )
        self.assertEqual(chosen, [p])
        self.assertEqual(choices, {d: "primary"})

    def test_only_alt_has_pings(self):
        d = "2025-08-02"
        a = _ping(_epoch_for_local(d, 10), 38.9, -77.4)
        chosen, choices = _select_track_per_day(
            primary_points=[], alt_points=[a],
            anchors=[], home=HOME, trip_start=d, trip_end=d,
        )
        self.assertEqual(chosen, [a])
        self.assertEqual(choices, {d: "alt"})

    # ── C: neither has pings ────────────────────────────────────────

    def test_no_pings_either_tid(self):
        d = "2025-08-02"
        chosen, choices = _select_track_per_day(
            primary_points=[], alt_points=[],
            anchors=[], home=HOME, trip_start=d, trip_end=d,
        )
        self.assertEqual(chosen, [])
        # Default prev_choice when nothing has been decided yet is "primary".
        self.assertEqual(choices, {d: "primary"})

    # ── D-i / D-ii: anchor encounters ───────────────────────────────

    def test_one_tid_encounters_anchor_other_does_not(self):
        d = "2025-08-02"
        # Primary stays near home; alt drives to Boonsboro.
        p = _ping(_epoch_for_local(d, 10), HOME[0], HOME[1])
        a = _ping(_epoch_for_local(d, 14), *ANCHOR_BOONSBORO_MD)
        chosen, choices = _select_track_per_day(
            primary_points=[p], alt_points=[a],
            anchors=[ANCHOR_BOONSBORO_MD], home=HOME,
            trip_start=d, trip_end=d,
        )
        self.assertEqual(chosen, [a])
        self.assertEqual(choices, {d: "alt"})

    def test_both_encounter_earliest_wins(self):
        d = "2025-08-02"
        # Primary hits the anchor at 14:00, alt at 12:00 → alt wins.
        p = _ping(_epoch_for_local(d, 14), *ANCHOR_BOONSBORO_MD)
        a = _ping(_epoch_for_local(d, 12), *ANCHOR_BOONSBORO_MD)
        chosen, choices = _select_track_per_day(
            primary_points=[p], alt_points=[a],
            anchors=[ANCHOR_BOONSBORO_MD], home=HOME,
            trip_start=d, trip_end=d,
        )
        self.assertEqual(chosen, [a])
        self.assertEqual(choices, {d: "alt"})

    def test_both_encounter_tie_goes_to_primary(self):
        d = "2025-08-02"
        same_tst = _epoch_for_local(d, 12)
        p = _ping(same_tst, *ANCHOR_BOONSBORO_MD)
        a = _ping(same_tst, *ANCHOR_BOONSBORO_MD)
        chosen, choices = _select_track_per_day(
            primary_points=[p], alt_points=[a],
            anchors=[ANCHOR_BOONSBORO_MD], home=HOME,
            trip_start=d, trip_end=d,
        )
        self.assertEqual(chosen, [p])
        self.assertEqual(choices, {d: "primary"})

    def test_distant_ping_does_not_count_as_encounter(self):
        """A ping 6 km from an anchor is outside the 5 km radius."""
        d = "2025-08-02"
        # Move 6 km east of Boonsboro. 1 deg lon ≈ 87 km at 39.5°N, so
        # 0.07 deg ≈ 6 km.
        far_lng = ANCHOR_BOONSBORO_MD[1] + 0.07
        # Primary is far from the anchor; alt is right on it.
        p = _ping(_epoch_for_local(d, 10), ANCHOR_BOONSBORO_MD[0], far_lng)
        a = _ping(_epoch_for_local(d, 14), *ANCHOR_BOONSBORO_MD)
        chosen, choices = _select_track_per_day(
            primary_points=[p], alt_points=[a],
            anchors=[ANCHOR_BOONSBORO_MD], home=HOME,
            trip_start=d, trip_end=d,
        )
        self.assertEqual(chosen, [a])
        self.assertEqual(choices, {d: "alt"})

    # ── D-iii: inherit previous day ──────────────────────────────────

    def test_neither_encounters_inherits_previous_day(self):
        d1, d2 = "2025-08-02", "2025-08-03"
        # Day 1: only alt encounters the anchor → alt wins day 1.
        p1 = _ping(_epoch_for_local(d1, 10), HOME[0], HOME[1])
        a1 = _ping(_epoch_for_local(d1, 14), *ANCHOR_BOONSBORO_MD)
        # Day 2: both tids have pings, neither near an anchor (just
        # generic driving coords). Inheritance should pick alt.
        p2 = _ping(_epoch_for_local(d2, 10), 40.0, -78.0)
        a2 = _ping(_epoch_for_local(d2, 14), 40.5, -78.5)
        chosen, choices = _select_track_per_day(
            primary_points=[p1, p2], alt_points=[a1, a2],
            anchors=[ANCHOR_BOONSBORO_MD], home=HOME,
            trip_start=d1, trip_end=d2,
        )
        self.assertEqual(choices, {d1: "alt", d2: "alt"})
        self.assertEqual(chosen, [a1, a2])

    def test_inheritance_across_pings_less_day(self):
        """Inheritance continuity holds even on a day where neither tid
        has any pings (e.g. logging gap), so the next day's inheritance
        still reaches back to the original decision."""
        d1, d2, d3 = "2025-08-02", "2025-08-03", "2025-08-04"
        # Day 1: alt encounters Boonsboro → alt.
        a1 = _ping(_epoch_for_local(d1, 14), *ANCHOR_BOONSBORO_MD)
        # Day 2: nothing at all.
        # Day 3: both tids have un-encountered pings.
        p3 = _ping(_epoch_for_local(d3, 10), 40.0, -78.0)
        a3 = _ping(_epoch_for_local(d3, 14), 40.5, -78.5)
        chosen, choices = _select_track_per_day(
            primary_points=[p3], alt_points=[a1, a3],
            anchors=[ANCHOR_BOONSBORO_MD], home=HOME,
            trip_start=d1, trip_end=d3,
        )
        self.assertEqual(choices, {d1: "alt", d2: "alt", d3: "alt"})
        self.assertEqual(chosen, [a1, a3])

    # ── D-iv / D-v: day-1 fallback ──────────────────────────────────

    def test_day1_no_anchor_farther_from_home_wins(self):
        d = "2025-08-02"
        # Primary stays right at home; alt is in Boonsboro (~80 km).
        # No anchor is configured for the trip (e.g., trip is just
        # campsite-less day excursions and the user hasn't added events
        # yet). Alt should win by max-distance-from-home.
        p = _ping(_epoch_for_local(d, 10), HOME[0], HOME[1])
        a = _ping(_epoch_for_local(d, 14), *ANCHOR_BOONSBORO_MD)
        chosen, choices = _select_track_per_day(
            primary_points=[p], alt_points=[a],
            anchors=[],  # no anchors!
            home=HOME, trip_start=d, trip_end=d,
        )
        self.assertEqual(chosen, [a])
        self.assertEqual(choices, {d: "alt"})

    def test_day1_no_home_falls_back_to_primary(self):
        d = "2025-08-02"
        p = _ping(_epoch_for_local(d, 10), 40.0, -78.0)
        a = _ping(_epoch_for_local(d, 14), 45.0, -80.0)
        chosen, choices = _select_track_per_day(
            primary_points=[p], alt_points=[a],
            anchors=[], home=None,
            trip_start=d, trip_end=d,
        )
        self.assertEqual(chosen, [p])
        self.assertEqual(choices, {d: "primary"})

    def test_day1_home_distance_tie_goes_to_primary(self):
        """Both phones leave home together — max distances are ~equal.
        Implementation uses `>=` for primary so the tie resolves there."""
        d = "2025-08-02"
        # Identical coords for both tids.
        p = _ping(_epoch_for_local(d, 10), *ANCHOR_BOONSBORO_MD)
        a = _ping(_epoch_for_local(d, 14), *ANCHOR_BOONSBORO_MD)
        chosen, choices = _select_track_per_day(
            primary_points=[p], alt_points=[a],
            anchors=[], home=HOME,
            trip_start=d, trip_end=d,
        )
        self.assertEqual(chosen, [p])
        self.assertEqual(choices, {d: "primary"})

    # ── Multi-day chain combining cases ─────────────────────────────

    def test_realistic_three_day_trip(self):
        """Day 1: both phones leave home, neither hits an anchor yet —
        day-1 fallback picks farther-from-home, alt wins. Day 2: both
        at the campground (Boonsboro), both encounter it — primary's
        encounter is earlier, primary wins. Day 3: phones split, only
        primary visits Harpers Ferry — primary wins."""
        d1, d2, d3 = "2025-08-01", "2025-08-02", "2025-08-03"
        # Day 1 — alt leaves home, primary stays close.
        p_d1 = _ping(_epoch_for_local(d1, 16), 39.0, -77.5)  # ~30 km from home
        a_d1 = _ping(_epoch_for_local(d1, 18), 39.5, -77.6)  # ~80 km from home
        # Day 2 — both at Boonsboro. Primary's encounter is at 10:00,
        # alt's at 11:00.
        p_d2 = _ping(_epoch_for_local(d2, 10), *ANCHOR_BOONSBORO_MD)
        a_d2 = _ping(_epoch_for_local(d2, 11), *ANCHOR_BOONSBORO_MD)
        # Day 3 — only primary hits Harpers Ferry.
        p_d3 = _ping(_epoch_for_local(d3, 14), *ANCHOR_HARPERS_FERRY)
        a_d3 = _ping(_epoch_for_local(d3, 14), 40.0, -78.0)
        chosen, choices = _select_track_per_day(
            primary_points=[p_d1, p_d2, p_d3],
            alt_points=[a_d1, a_d2, a_d3],
            anchors=[ANCHOR_BOONSBORO_MD, ANCHOR_HARPERS_FERRY],
            home=HOME,
            trip_start=d1, trip_end=d3,
        )
        self.assertEqual(choices, {d1: "alt", d2: "primary", d3: "primary"})
        self.assertEqual(chosen, [a_d1, p_d2, p_d3])

    def test_override_locks_in_for_inheritance(self):
        """An override on day 1 is what the day-2 inheritance sees,
        even when no encounter happens on day 2."""
        d1, d2 = "2025-08-02", "2025-08-03"
        p_d1 = _ping(_epoch_for_local(d1, 14), *ANCHOR_BOONSBORO_MD)
        a_d1 = _ping(_epoch_for_local(d1, 10), HOME[0], HOME[1])
        # Day 2: both have generic pings, neither anchor-near.
        p_d2 = _ping(_epoch_for_local(d2, 10), 40.0, -78.0)
        a_d2 = _ping(_epoch_for_local(d2, 14), 40.5, -78.5)
        # Without override, day 1's primary would win (only it
        # encounters Boonsboro) and day 2 would inherit primary.
        # The override forces alt on day 1; day 2 should inherit alt.
        chosen, choices = _select_track_per_day(
            primary_points=[p_d1, p_d2], alt_points=[a_d1, a_d2],
            anchors=[ANCHOR_BOONSBORO_MD], home=HOME,
            trip_start=d1, trip_end=d2,
            tid_overrides={d1: "alt"},
        )
        self.assertEqual(choices, {d1: "override:alt", d2: "alt"})
        self.assertEqual(chosen, [a_d1, a_d2])

    # ── Midnight-boundary bucketing ─────────────────────────────────

    def test_ping_tz_field_governs_local_date_bucketing(self):
        """A UTC timestamp that's day-1 in NY but day-2 in UTC should
        bucket to day-1 because we use the ping's `tz` field."""
        # 2025-08-02 23:30 in NY is 2025-08-03 03:30 UTC.
        import datetime as dt
        local_august_2_2330 = dt.datetime(2025, 8, 2, 23, 30)
        utc = local_august_2_2330 + dt.timedelta(hours=4)  # EDT → UTC
        tst = int(utc.replace(tzinfo=dt.timezone.utc).timestamp())
        # Sanity: UTC date is 2025-08-03 but NY-local date is 2025-08-02.
        self.assertEqual(_local_date_of_ping(
            {"tst": tst, "lat": 0, "lon": 0, "tz": "America/New_York"}), "2025-08-02")

        p = _ping(tst, *ANCHOR_BOONSBORO_MD)
        chosen, choices = _select_track_per_day(
            primary_points=[p], alt_points=[],
            anchors=[ANCHOR_BOONSBORO_MD], home=HOME,
            trip_start="2025-08-02", trip_end="2025-08-02",
        )
        self.assertEqual(chosen, [p])
        self.assertEqual(choices, {"2025-08-02": "primary"})

    # ── Output ordering ─────────────────────────────────────────────

    def test_chosen_points_are_sorted_by_tst(self):
        """Multi-day chosen pings must come out in chronological order
        regardless of which day's bucket they came from."""
        d1, d2 = "2025-08-02", "2025-08-03"
        # Same tid wins both days. Submit pings out of order — output
        # should still sort.
        p_late = _ping(_epoch_for_local(d2, 9), 40.0, -78.0)
        p_early = _ping(_epoch_for_local(d1, 14), *ANCHOR_BOONSBORO_MD)
        chosen, choices = _select_track_per_day(
            primary_points=[p_late, p_early], alt_points=[],
            anchors=[ANCHOR_BOONSBORO_MD], home=HOME,
            trip_start=d1, trip_end=d2,
        )
        self.assertEqual(chosen, [p_early, p_late])
        self.assertEqual(choices, {d1: "primary", d2: "primary"})


if __name__ == "__main__":
    unittest.main()
