"""Gap-fill anchors must be timestamped in the zone they happened in.

`_trip_route_stops` builds the timestamped day-by-day anchor walk that fills
holes in a trip's GPS line. Those timestamps decide WHICH GAP an anchor is
spliced into, so a zone error here does not nudge the line — it teleports an
anchor into a different gap entirely.

Stamping every anchor in the HOME zone did exactly that on trip 95: a 09:11
Mountain waypoint (Roaring Fork) read as Eastern became 07:11 Mountain, which
landed it inside the PREVIOUS NIGHT's 20:42 -> 07:59 gap. The gap-filler
dutifully routed the line out to it and back, drawing a 9.3 km spike across
Lake Granby while the travelers were asleep at Sunset Point. Six such detours
existed across trips 32 and 95 — every trip whose events sit outside the home
zone.

The same bug lived in the detail map's `localEpoch`, which used the BROWSER's
zone, so the spike appeared for a reader in Eastern and vanished for one in
Colorado. Both now stamp each anchor with its own zone.

Run from the project root with the venv active:

    python -m unittest tests.test_route_anchor_timezones -v
"""

import os
import sys
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ekko_trips_app import _trip_route_stops  # noqa: E402

HOME = (38.9296, -77.3672)          # Reston, VA — Eastern
HOME_TZ = "America/New_York"
MOUNTAIN = ZoneInfo("America/Denver")

# Sunset Point Campground and the Roaring Fork waypoint, both Mountain time.
SUNSET_POINT = (40.14893, -105.87563)
ROARING_FORK = (40.13011, -105.76672)


def _trip(events, stays):
    dates = ([s["start"] for s in stays] + [s["end"] for s in stays]
             + [e["date"] for e in events])
    return {"id": 1, "start": min(dates), "end": max(dates),
            "stays": stays, "events": events}


def _stay(start, end, pt):
    return {"start": start, "end": end, "lat": pt[0], "lng": pt[1]}


def _event(date, time, pt, tz, name="waypoint"):
    return {"date": date, "time": time, "name": name, "tz": tz,
            "lat": pt[0], "lng": pt[1], "waypoint": True}


def _at(stops, pt):
    """The timestamp of the anchor at `pt`, or None."""
    for tst, ll in stops:
        if abs(ll[0] - pt[0]) < 1e-6 and abs(ll[1] - pt[1]) < 1e-6:
            return tst
    return None


class TestEventAnchorsUseTheirOwnZone(unittest.TestCase):

    # A night at Sunset Point, then the Roaring Fork stop at 09:11 the
    # next morning — the real trip-95 shape, minimised.
    STAYS = [_stay("2026-08-26", "2026-08-28", SUNSET_POINT)]
    EVENTS = [_event("2026-08-27", "09:11", ROARING_FORK, "America/Denver",
                     "Roaring Fork")]

    def test_anchor_lands_at_the_real_instant(self):
        stops = _trip_route_stops(_trip(self.EVENTS, self.STAYS), HOME, HOME_TZ)
        tst = _at(stops, ROARING_FORK)
        self.assertIsNotNone(tst, "Roaring Fork anchor missing")
        local = datetime.fromtimestamp(tst, MOUNTAIN)
        self.assertEqual(local.strftime("%Y-%m-%d %H:%M"), "2026-08-27 09:11")

    def test_anchor_is_not_stamped_two_hours_early(self):
        """The specific regression: read as Eastern this was 07:11 Mountain."""
        stops = _trip_route_stops(_trip(self.EVENTS, self.STAYS), HOME, HOME_TZ)
        local = datetime.fromtimestamp(_at(stops, ROARING_FORK), MOUNTAIN)
        self.assertNotEqual(local.strftime("%H:%M"), "07:11")

    def test_anchor_falls_after_the_overnight_gap_not_inside_it(self):
        """What actually drew the spike: the anchor has to sort AFTER the
        morning's first ping, or the gap-filler splices it into last night."""
        stops = _trip_route_stops(_trip(self.EVENTS, self.STAYS), HOME, HOME_TZ)
        # 07:59 Mountain — the first ping of 08-27 on the real trip.
        first_ping = datetime(2026, 8, 27, 7, 59, tzinfo=MOUNTAIN).timestamp()
        self.assertGreater(_at(stops, ROARING_FORK), first_ping)

    def test_an_eastern_event_is_unaffected(self):
        """A trip that never leaves the home zone must stamp exactly as before."""
        events = [_event("2026-08-27", "09:11", (39.5, -77.6), HOME_TZ)]
        stays = [_stay("2026-08-26", "2026-08-28", (39.4, -77.5))]
        stops = _trip_route_stops(_trip(events, stays), HOME, HOME_TZ)
        tst = _at(stops, (39.5, -77.6))
        self.assertEqual(
            datetime.fromtimestamp(tst, ZoneInfo(HOME_TZ)).strftime("%H:%M"),
            "09:11")


class TestDayBoundaryAnchorsUseTheStaysZone(unittest.TestCase):
    """Midnight is when the travelers reached it, not when the reader did."""

    def test_day_boundary_anchor_is_local_midnight_at_the_campground(self):
        """The 08-26 evening anchor is 23:59 at Sunset Point — Mountain, not
        Eastern. (The 08-27 morning anchor is the same place, so it collapses
        into this one, which is why 23:59 is what survives.)"""
        stays = [_stay("2026-08-26", "2026-08-28", SUNSET_POINT)]
        stops = _trip_route_stops(_trip([], stays), HOME, HOME_TZ)
        tst = _at(stops, SUNSET_POINT)
        self.assertIsNotNone(tst)
        self.assertEqual(
            datetime(2026, 8, 26, 23, 59, tzinfo=MOUNTAIN).timestamp(), tst)
        # And emphatically not the same wall clock read in the home zone,
        # which is what it used to be (two hours earlier in real terms).
        self.assertNotEqual(
            datetime(2026, 8, 26, 23, 59,
                     tzinfo=ZoneInfo(HOME_TZ)).timestamp(), tst)

    def test_home_falls_back_to_the_home_zone(self):
        """A day with no stay anchors resolves to HOME, which is Eastern."""
        events = [_event("2026-08-27", "09:11", (39.5, -77.6), HOME_TZ)]
        stops = _trip_route_stops(_trip(events, []), HOME, HOME_TZ)
        want = datetime(2026, 8, 27, 0, 0,
                        tzinfo=ZoneInfo(HOME_TZ)).timestamp()
        self.assertIn(want, [t for t, _ll in stops])


class TestOrderingIsStillChronological(unittest.TestCase):

    def test_a_westward_crossing_day_walks_in_the_right_order(self):
        """Anchors come out in true time order across a zone line — the same
        rule the timeline sorts by, applied to the map's walk."""
        stays = [_stay("2026-08-22", "2026-08-24", (40.14, -101.07))]
        events = [
            _event("2026-08-23", "08:47", (40.17410, -101.09860),
                   "America/Chicago", "Macklin Bay"),
            _event("2026-08-23", "08:35", (40.05777, -101.53213),
                   "America/Denver", "Sinclair Gas"),
        ]
        stops = _trip_route_stops(_trip(events, stays), HOME, HOME_TZ)
        self.assertLess(_at(stops, (40.17410, -101.09860)),
                        _at(stops, (40.05777, -101.53213)))

    def test_anchors_are_monotonically_ordered(self):
        stays = [_stay("2026-08-26", "2026-08-28", SUNSET_POINT)]
        events = [
            _event("2026-08-27", "18:10", (40.25132, -105.81799),
                   "America/Denver"),
            _event("2026-08-27", "09:11", ROARING_FORK, "America/Denver"),
            _event("2026-08-27", "13:07", (40.08505, -105.93377),
                   "America/Denver"),
        ]
        tsts = [t for t, _ll in _trip_route_stops(
            _trip(events, stays), HOME, HOME_TZ)]
        self.assertEqual(tsts, sorted(tsts))


class TestDegradesSafely(unittest.TestCase):

    def test_events_without_a_zone_fall_back_to_home(self):
        events = [{"date": "2026-08-27", "time": "09:11", "name": "x",
                   "lat": 39.5, "lng": -77.6}]
        stays = [_stay("2026-08-26", "2026-08-28", (39.4, -77.5))]
        stops = _trip_route_stops(_trip(events, stays), HOME, HOME_TZ)
        tst = _at(stops, (39.5, -77.6))
        self.assertEqual(
            datetime.fromtimestamp(tst, ZoneInfo(HOME_TZ)).strftime("%H:%M"),
            "09:11")

    def test_no_home_zone_still_produces_anchors(self):
        stays = [_stay("2026-08-26", "2026-08-28", SUNSET_POINT)]
        events = [_event("2026-08-27", "09:11", ROARING_FORK, "America/Denver")]
        stops = _trip_route_stops(_trip(events, stays), HOME, None)
        self.assertTrue(stops)
        self.assertIsNotNone(_at(stops, ROARING_FORK))


if __name__ == "__main__":
    unittest.main()
