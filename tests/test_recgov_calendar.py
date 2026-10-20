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

import datetime
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


class TestBookingHorizon(unittest.TestCase):
    """The 2026-10-20 walk read June 2027, fetched 225 days out, as Not
    Reservable throughout for 28 campgrounds whose June 2026 had shown open
    days, and wrote "opens 07-01" off the month boundary (Clear Lake 2355)."""

    def clear_lake(self):
        return {"months": {"2026-06": "?" * 21 + "o" * 9, "2026-07": "o" * 31,
                           "2026-08": "o" * 31, "2026-09": "o" * 30,
                           "2027-06": "c" * 30},
                "fetched": {"2026-06": "2026-09-20", "2026-07": "2026-09-20",
                            "2026-08": "2026-09-20", "2026-09": "2026-09-20",
                            "2027-06": "2026-10-20"}}

    def test_a_closed_reading_past_the_horizon_is_no_information(self):
        days = rc.day_map(self.clear_lake())
        self.assertNotIn("06-01", days)
        self.assertNotEqual(rc.derive_season(self.clear_lake())[0], {"opens": "07-01"})

    def test_an_open_reading_past_the_horizon_still_counts(self):
        e = self.clear_lake()
        e["months"]["2027-06"] = "o" * 30
        self.assertEqual(rc.day_map(e)["06-01"], "o")

    def test_a_far_closure_counts_where_that_fetch_reached_further(self):
        # Blue Bend, fetched 2026-09-20: April 2027 closed, May open.
        e = {"months": {"2027-04": "c" * 30, "2027-05": "o" * 31},
             "fetched": {"2027-04": "2026-09-20", "2027-05": "2026-09-20"}}
        self.assertEqual(rc.day_map(e)["04-15"], "c")
        self.assertEqual(rc.derive_season(e)[0], {"opens": "05-01"})

    def test_two_years_that_disagree_leave_the_day_unknown(self):
        e = entry(**{"2026_06": "?" * 21 + "o" * 9, "2027_06": "c" * 30})
        days = rc.day_map(e)
        self.assertNotIn("06-25", days)
        self.assertEqual(days["06-01"], "c")


class TestResultingSeason(unittest.TestCase):

    def test_year_round_replaces_dates(self):
        # Mather: 03-01 to 11-30 was its reservation window; it is open all year.
        was = {"year_round": False, "opens": "03-01", "closes": "11-30"}
        self.assertEqual(rc.resulting_season(was, {"year_round": True}),
                         {"year_round": True})

    def test_a_seasonal_reading_keeps_an_edge_it_could_not_see(self):
        was = {"opens": "05-01", "closes": "10-15"}
        self.assertEqual(rc.resulting_season(was, {"closes": "10-20"}),
                         {"opens": "05-01", "closes": "10-20"})


class TestFetchWindow(unittest.TestCase):
    """rec.gov marks the ten days before a fetch and the few after it Not
    Reservable on every site. The 2026-09-21 walk read that as a closure and
    wrote "opens 09-24" for Lane Spring, open all summer (and nine others)."""

    def test_the_booking_window_is_not_an_opening(self):
        e = entry(**{"2026_07": "o" * 31, "2026_08": "o" * 31,
                     "2026_09": "o" * 9 + "c" * 14 + "o" * 7, "2026_10": "o" * 31})
        e["checked"] = "2026-09-20"
        season, reason = rc.derive_season(e)
        self.assertIsNone(season)
        self.assertIn("booking window", reason)

    def test_a_closure_running_past_the_window_keeps_its_edge(self):
        # Brooklyn Lake: open through 09-12, then closed for as far as the
        # calendar answered. Only a closed run wholly inside the window goes.
        e = entry(**{"2026_07": "o" * 31, "2026_08": "o" * 31,
                     "2026_09": "o" * 12 + "c" * 18, "2026_10": "c" * 20 + "?" * 11})
        e["checked"] = "2026-09-20"
        self.assertEqual(rc.derive_season(e)[0], {"closes": "09-12"})

    def test_the_run_is_kept_so_no_new_edge_appears(self):
        # The Narrows (WY) as walked: erasing the window's closed days would
        # merge the open week after them into the summer and yield "closes
        # 09-21", an edge nobody checked. Only edges go, so it keeps no verdict.
        e = entry(**{"2026_07": "o" * 31, "2026_08": "o" * 31,
                     "2026_09": "ooooooo??cccccoooooooccccccccc",
                     "2027_05": "?" * 10 + "c" * 11 + "?" * 10})
        e["checked"] = "2026-09-20"
        self.assertIsNone(rc.derive_season({"months": e["months"]})[0])
        self.assertIsNone(rc.derive_season(e)[0])

    def test_a_walk_pins_each_months_fetch_date(self):
        # `checked` moves on with every walk; the window needs the date each
        # month was actually read.
        saved = rc.fetch_availability_month
        rc.fetch_availability_month = lambda *a, **k: {}
        try:
            e = {"checked": "2026-09-21", "months": {"2026-09": "o" * 30}}
            rc.walk_months("1", [(2026, 9), (2026, 11)], e, pause=0)
        finally:
            rc.fetch_availability_month = saved
        self.assertEqual(e["fetched"]["2026-09"], "2026-09-21")
        self.assertEqual(e["fetched"]["2026-11"], e["checked"])


class TestRewalk(unittest.TestCase):
    """Which months a re-walk asks for again (2026-10-20)."""

    def walk(self, entry, months):
        asked = []
        saved = rc.fetch_availability_month
        rc.fetch_availability_month = lambda fid, y, m, **k: asked.append((y, m)) or {}
        try:
            rc.walk_months("1", months, entry, pause=0)
        finally:
            rc.fetch_availability_month = saved
        return asked

    def month(self, offset):
        d = datetime.date.today().replace(day=1)
        m = d.month - 1 + offset
        return d.year + m // 12, m % 12 + 1

    def key(self, ym):
        return f"{ym[0]:04d}-{ym[1]:02d}"

    def entry(self, months, fetched_days_ago=30):
        on = (datetime.date.today() - datetime.timedelta(days=fetched_days_ago)).isoformat()
        return {"checked": on, "months": dict(months), "fetched": {k: on for k in months}}

    def test_an_all_nyr_month_the_window_may_now_reach_is_asked_again(self):
        now, nxt = self.month(0), self.month(1)
        e = self.entry({self.key(now): "o" * 28, self.key(nxt): "?" * 28})
        self.assertEqual(self.walk(e, [now, nxt]), [nxt])

    def test_a_month_with_any_observation_is_kept(self):
        nxt = self.month(1)
        e = self.entry({self.key(nxt): "o" * 10 + "?" * 18})
        self.assertEqual(self.walk(e, [nxt]), [])

    def test_a_past_all_nyr_month_is_not_asked_again(self):
        past, now = self.month(-1), self.month(0)
        e = self.entry({self.key(past): "?" * 28, self.key(now): "o" * 28})
        self.assertEqual(self.walk(e, [past]), [])

    def test_a_month_beyond_the_windows_reach_is_not_asked(self):
        now, far = self.month(0), self.month(8)
        e = self.entry({self.key(now): "o" * 10 + "?" * 18}, fetched_days_ago=0)
        self.assertEqual(self.walk(e, [far]), [])

    def test_a_facility_never_observed_is_walked_as_before(self):
        nxt, far = self.month(1), self.month(8)
        e = self.entry({self.key(nxt): "?" * 28})
        self.assertEqual(self.walk(e, [nxt, far]), [far])


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
