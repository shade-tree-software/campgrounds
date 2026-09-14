"""Reading a season off the recreation.gov calendar without inventing one.

`recgov_calendar.py` derives a campground's open season from availability
statuses. Every rule below corrects something the live API actually did during
development, and each failure mode is silent — a wrong season looks exactly like
a right one in the stored entry.

The two that would have been most expensive:

* **NYR is not a closure.** Beyond a facility's booking window every date reads
  "NYR" (not yet released). Counting that as closed reports every campground in
  the federal system shutting exactly six months out, which is both wrong and
  perfectly plausible-looking.
* **A short closure is not a season.** Dennis Cove had ONE closed day and
  yielded "opens 09-11, closes 09-09"; Backbone Rock produced four edges inside
  ten days. Real seasonal closures run for months.

    python -m unittest tests.test_recgov_calendar -v
"""

import unittest

import recgov_calendar as rc


def entry(**months):
    """Cache entry from {'YYYY_MM': 'occ?...'} — underscore for kwarg syntax."""
    return {"months": {k.replace("_", "-"): v for k, v in months.items()}}


def year(pattern):
    """Build a full-year entry from 12 (month, char) pairs of equal fill."""
    import calendar
    out = {}
    for m, ch in enumerate(pattern, start=1):
        out[f"2026-{m:02d}"] = ch * calendar.monthrange(2026, m)[1]
    return {"months": out}


class TestStatusReading(unittest.TestCase):

    def test_reserved_counts_as_open(self):
        # Somebody is camping there: the strongest evidence of being in service.
        got = rc.month_string({"s1": {"2026-07-01T00:00:00Z": "Reserved"}}, 2026, 7)
        self.assertEqual(got[0], rc.OPEN)

    def test_nyr_is_unknown_not_closed(self):
        got = rc.month_string({"s1": {"2026-07-01T00:00:00Z": "NYR"}}, 2026, 7)
        self.assertEqual(got[0], rc.UNKNOWN)

    def test_all_sites_not_reservable_is_closed(self):
        avail = {"s1": {"2026-07-01T00:00:00Z": "Not Reservable"},
                 "s2": {"2026-07-01T00:00:00Z": "Not Reservable"}}
        self.assertEqual(rc.month_string(avail, 2026, 7)[0], rc.CLOSED)

    def test_one_bookable_site_makes_the_day_open(self):
        # Some sites unbookable mid-season is a closed loop or a walk-up area,
        # not a closure of the campground.
        avail = {"s1": {"2026-07-01T00:00:00Z": "Not Reservable"},
                 "s2": {"2026-07-01T00:00:00Z": "Available"}}
        self.assertEqual(rc.month_string(avail, 2026, 7)[0], rc.OPEN)

    def test_a_day_with_nothing_returned_is_unknown(self):
        self.assertEqual(rc.month_string({}, 2026, 7), rc.UNKNOWN * 31)


class TestSmoothing(unittest.TestCase):

    def test_a_single_closed_day_is_erased(self):
        # The Dennis Cove case: one closed day became a whole season boundary.
        days = {f"09-{d:02d}": rc.OPEN for d in range(1, 31)}
        days["09-10"] = rc.CLOSED
        smoothed = rc.smooth(days)
        self.assertNotIn("09-10", smoothed)
        self.assertEqual(rc.season_edges(smoothed), [])

    def test_a_short_run_is_erased_not_flipped(self):
        # Three closed days are not evidence the place was OPEN either.
        days = {f"09-{d:02d}": rc.OPEN for d in range(1, 31)}
        for d in (10, 11, 12):
            days[f"09-{d:02d}"] = rc.CLOSED
        smoothed = rc.smooth(days)
        for d in (10, 11, 12):
            self.assertNotIn(f"09-{d:02d}", smoothed)

    def test_a_months_long_closure_survives(self):
        days = {f"07-{d:02d}": rc.OPEN for d in range(1, 32)}
        days.update({f"08-{d:02d}": rc.CLOSED for d in range(1, 32)})
        smoothed = rc.smooth(days)
        self.assertEqual(len(smoothed), len(days))


class TestEdges(unittest.TestCase):

    def test_an_adjacent_transition_is_an_edge(self):
        days = {f"09-{d:02d}": rc.OPEN for d in range(1, 16)}
        days.update({f"09-{d:02d}": rc.CLOSED for d in range(16, 31)})
        self.assertIn(("closes", "09-15"), rc.season_edges(days))

    def test_a_wide_gap_places_no_edge(self):
        # Open through September, nothing for October, closed in November: the
        # boundary is somewhere in a two-month hole and cannot be placed.
        days = {f"09-{d:02d}": rc.OPEN for d in range(1, 31)}
        days.update({f"11-{d:02d}": rc.CLOSED for d in range(1, 31)})
        self.assertEqual(rc.season_edges(days), [])

    def test_edges_are_found_in_both_directions(self):
        days = {f"04-{d:02d}": rc.CLOSED for d in range(1, 31)}
        days.update({f"05-{d:02d}": rc.OPEN for d in range(1, 32)})
        days.update({f"06-{d:02d}": rc.OPEN for d in range(1, 31)})
        kinds = [k for k, _ in rc.season_edges(days)]
        self.assertIn("opens", kinds)


class TestDerivation(unittest.TestCase):

    def test_a_clean_seasonal_campground(self):
        # Closed Jan-Apr, open May-Sep, closed Oct-Dec.
        season, reason = rc.derive_season(
            year("cccc" + "ooooo" + "ccc"))
        self.assertEqual(season, {"opens": "05-01", "closes": "09-30"})

    def test_year_round_needs_near_complete_coverage(self):
        season, _ = rc.derive_season(year("o" * 12))
        self.assertEqual(season, {"year_round": True})

    def test_four_open_months_is_not_year_round(self):
        # The common real case: ~120 observed days, the rest NYR. Claiming
        # year-round here asserts something about 245 unobserved days.
        season, reason = rc.derive_season(year("???" + "oooo" + "?????"))
        self.assertIsNone(season)
        self.assertIn("no transition", reason)

    def test_nyr_beyond_the_window_never_becomes_a_closing_date(self):
        # Open Jun-Sep then unreleased: must NOT read as "closes 09-30".
        season, _ = rc.derive_season(year("?????" + "oooo" + "???"))
        self.assertIsNone(season)

    def test_ambiguous_multiple_edges_yield_nothing(self):
        e = year("cc" + "oo" + "cc" + "oo" + "cccc")
        season, reason = rc.derive_season(e)
        self.assertIsNone(season)
        self.assertIn("ambiguous", reason)

    def test_no_calendar_data_is_reported_as_such(self):
        season, reason = rc.derive_season({"months": {}})
        self.assertIsNone(season)
        self.assertIn("no calendar data", reason)

    def test_a_partial_answer_is_still_an_answer(self):
        # Only the closing edge observed: record it, leave `opens` unknown.
        e = year("???" + "ooooo" + "cccc")
        season, _ = rc.derive_season(e)
        self.assertEqual(season, {"closes": "08-31"})

    def test_derived_season_satisfies_the_schema(self):
        import campground_schema as cs
        season, _ = rc.derive_season(year("cccc" + "ooooo" + "ccc"))
        staged = {}
        cs.apply_update(staged, {"season": season})
        self.assertEqual(staged["season"], season)


class TestFacilityIds(unittest.TestCase):

    def test_only_campground_urls_are_taken(self):
        entries = [
            {"id": 1, "website": "https://www.recreation.gov/camping/campgrounds/232762"},
            {"id": 2, "website": "https://www.recreation.gov/camping/poi/259059"},
            {"id": 3, "website": "https://example.com/"},
        ]
        got = rc.facility_ids(entries)
        self.assertEqual(got, {1: "232762"})


if __name__ == "__main__":
    unittest.main()
