"""A voice memo files itself against the trips' own GPS tracks.

This is the load-bearing idea of the whole memo pipeline: filing is normally
the hard part of "just record and I'll sort it later" — which day, which
place — and EKKO already knows where the phone was, to a few minutes.

Three rules do the work, and each exists because of something real in the data:

  * **The trip's DATE RANGE decides the trip, not track proximity.** Track
    caches deliberately overrun their trip (start-1d to end+2d), so back-to-back
    trips' caches hold the SAME pings at the seam and nearest-ping distance
    cannot tell them apart.
  * **The track decides the DAY and the position.** The local day is read in
    the zone the phone was in, so a memo spoken at 9pm in Colorado lands on
    that evening rather than the next morning.
  * **A memo between trips goes to the NEAREST trip by date, within
    MEMO_ADOPT_DAYS.** That is the drive home. Past it, unfiled — a memo you
    place by hand beats one silently attached to the wrong week.

Run from the project root with the venv active:

    python -m unittest tests.test_memo_filing -v
"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ekko_trips_app as A  # noqa: E402

# 2025-06-10 12:00 UTC = 06:00 in Denver, so a UTC-vs-local day mix-up shows up.
JUN10_NOON_UTC = 1749556800
DAY = 86400
MDT = "America/Denver"


def _track(first_tst, days, tz=MDT):
    """A ping an hour for `days` days, the shape `_read_track_cache` returns."""
    return [{"lat": 40.0, "lon": -105.0, "tst": first_tst + h * 3600, "tid": "primary",
             "tz": tz}
            for h in range(days * 24)]


def _trip(tid, start, end, stays=None):
    return {"id": tid, "start": start, "end": end, "number": tid,
            "summary": f"Trip {tid}", "stays": stays or [], "events": []}


class MemoFilingCase(unittest.TestCase):
    """Two back-to-back trips whose track caches overlap at the seam, which is
    the arrangement every interesting rule here is about."""

    TRIPS = [
        _trip(1, "2025-06-09", "2025-06-12"),
        _trip(2, "2025-06-15", "2025-06-18"),
    ]
    # Trip 1's cache runs a day early and two days late, so it covers 06-08
    # through 06-14 — overlapping nothing here, but reaching well past 06-12.
    TRACKS = {
        1: _track(JUN10_NOON_UTC - 2 * DAY, 7),
        2: _track(JUN10_NOON_UTC + 4 * DAY, 7),
    }

    def setUp(self):
        patches = [
            mock.patch.object(A, "parse_trips", lambda: [dict(t) for t in self.TRIPS]),
            mock.patch.object(A, "_read_track_cache", lambda tid: self.TRACKS.get(tid)),
            mock.patch.object(A, "enrich_trip_locations", lambda trip: None),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def file(self, tst):
        return A._file_memo_by_time(tst)


class TestFilesToTheRightTrip(MemoFilingCase):
    def test_mid_trip_memo_lands_on_its_trip_and_day(self):
        got = self.file(JUN10_NOON_UTC)
        self.assertEqual(got["trip_id"], 1)
        # 12:00 UTC is 06:00 Denver — same date here, but read in the phone's
        # zone rather than UTC, which is what the next test proves matters.
        self.assertEqual(got["date"], "2025-06-10")

    def test_day_is_read_in_the_phones_zone_not_utc(self):
        # 03:00 UTC on the 11th is 21:00 Denver on the 10th. A memo spoken that
        # evening belongs to the 10th's card, not the next morning's.
        got = self.file(JUN10_NOON_UTC + 15 * 3600)
        self.assertEqual(got["date"], "2025-06-10")

    def test_position_and_gap_come_back(self):
        got = self.file(JUN10_NOON_UTC)
        self.assertEqual((got["lat"], got["lon"]), (40.0, -105.0))
        self.assertEqual(got["pos_gap_s"], 0)

    def test_far_from_any_ping_keeps_the_day_but_not_a_position(self):
        # Deep in a gap the track never covers: the trip and day are still
        # known, but inventing coordinates would be a lie.
        with mock.patch.object(A, "MEMO_NEAR_PING_S", 60):
            got = self.file(JUN10_NOON_UTC + 1800)
        self.assertEqual(got["trip_id"], 1)
        self.assertNotIn("lat", got)


class TestSeamsBetweenTrips(MemoFilingCase):
    def test_overlapping_cache_does_not_steal_the_next_trips_memo(self):
        # 06-16 is inside trip 2's dates. Trip 1's cache stops before it, but
        # this is the shape that filed trip 32's opening ping onto trip 31 when
        # nearest-ping distance was picking the trip.
        got = self.file(JUN10_NOON_UTC + 6 * DAY)
        self.assertEqual(got["trip_id"], 2)
        self.assertEqual(got["date"], "2025-06-16")

    def test_memo_just_after_a_trip_ends_stays_with_that_trip(self):
        # 06-13, the drive home. Belongs to trip 1 (ended 06-12), NOT trip 2
        # two days later — and the day is clamped so it names a day trip 1's
        # page can actually show.
        got = self.file(JUN10_NOON_UTC + 3 * DAY)
        self.assertEqual(got["trip_id"], 1)
        self.assertEqual(got["date"], "2025-06-12")

    def test_gap_memo_goes_to_the_nearer_trip_in_either_direction(self):
        # 06-14 is two days past trip 1's end and one day before trip 2's
        # start, so trip 2 takes it — the rule is nearest, not "the one you
        # just finished". The night before setting off is as plausibly about
        # the trip ahead as the drive home is about the trip behind.
        got = self.file(JUN10_NOON_UTC + 4 * DAY)
        self.assertEqual(got["trip_id"], 2)
        self.assertEqual(got["date"], "2025-06-15")     # clamped to trip 2's start

    def test_memo_beyond_the_adopt_window_is_unfiled(self):
        with mock.patch.object(A, "MEMO_ADOPT_DAYS", 0):
            self.assertEqual(self.file(JUN10_NOON_UTC + 4 * DAY), {})


class TestUnfilable(MemoFilingCase):
    def test_instant_in_no_trip_is_unfiled_not_guessed(self):
        # An empty answer is a normal outcome — a memo recorded at home, or
        # months after the trip it describes. The page offers a manual picker.
        self.assertEqual(self.file(JUN10_NOON_UTC - 200 * DAY), {})
        self.assertEqual(self.file(JUN10_NOON_UTC + 200 * DAY), {})

    def test_garbage_timestamp_is_unfiled_rather_than_raising(self):
        # The value arrives from a form field, so it must not be trusted.
        self.assertEqual(A._file_memo_by_time(None), {})
        self.assertEqual(A._file_memo_by_time("not a number"), {})

    def test_trip_without_a_track_still_files_by_date(self):
        with mock.patch.object(A, "_read_track_cache", lambda tid: None):
            got = self.file(JUN10_NOON_UTC)
        self.assertEqual(got["trip_id"], 1)
        self.assertEqual(got["date"], "2025-06-10")
        self.assertNotIn("lat", got)      # no track, no position


class TestPlaceNaming(MemoFilingCase):
    def test_nearby_stay_names_the_memo(self):
        trips = [_trip(1, "2025-06-09", "2025-06-12",
                       stays=[{"place": "Moraine Park", "lat": 40.0001, "lng": -105.0001}])]
        with mock.patch.object(A, "parse_trips", lambda: [dict(t) for t in trips]):
            self.assertEqual(self.file(JUN10_NOON_UTC)["place"], "Moraine Park")

    def test_distant_stay_does_not(self):
        trips = [_trip(1, "2025-06-09", "2025-06-12",
                       stays=[{"place": "Somewhere else", "lat": 41.0, "lng": -106.0}])]
        with mock.patch.object(A, "parse_trips", lambda: [dict(t) for t in trips]):
            self.assertEqual(self.file(JUN10_NOON_UTC)["place"], "")


if __name__ == "__main__":
    unittest.main()
