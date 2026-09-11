"""When a day's write-up gets drafted: the narrow fingerprint and the settle gate.

Together these are what make an unattended drafting run safe to schedule, and
both encode a judgement that is easy to get backwards.

`day_signature` must stay NARROW. A trip gathers hundreds of edits while it
happens and for weeks afterwards — photos, captions, descriptions, waypoints,
notes, reordering — and none of them change what a summary says, which
is what kind of day it was: how far, which way, where you slept. A wider hash
(`_trip_route_signature`, say, which hashes the whole raw trip record and is
right for a route) would make every one of those edits look like a reason to
spend money rewriting prose nobody asked to have rewritten.

`day_settled` must stay CONSERVATIVE. An in-progress trip re-polls the tail of
its track, so a day that is over can still gain distance; drafted early it says
"312 miles" about a day that ends at 400, and reads as finished either way.

    python -m unittest tests.test_rollup_scheduling -v
"""

import os
import sys
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import process_rollups as R  # noqa: E402

DAY = "2026-08-28"

TRIP = {
    "id": 95,
    "stays": [
        {"place": "Prairie Dog State Park", "locale": "Norton", "state": "KS",
         "start": "2026-08-28", "end": "2026-08-29", "site": "12",
         "notes": "cottonwoods along the creek"},
        {"place": "Moraine Park", "locale": "Estes Park", "state": "CO",
         "start": "2026-08-24", "end": "2026-08-28"},
    ],
    "events": [{"date": DAY, "name": "Granby", "description": "a long stop"}],
}
DRIVING = {DAY: {"miles": 412, "seconds": 27000, "round_trip": False}}


_UNSET = object()


def sig(trip=_UNSET, driving=_UNSET, day=DAY):
    # Sentinels, not `or` — an empty driving dict is a real case (the day
    # recorded no driving at all) and `{} or DRIVING` would silently skip it.
    return R.day_signature(TRIP if trip is _UNSET else trip, day,
                           DRIVING if driving is _UNSET else driving)


class TestSignatureIsNarrow(unittest.TestCase):
    """The edits a trip actually accumulates must not move the fingerprint."""

    def _unchanged(self, mutate):
        trip = {**TRIP,
                "stays": [dict(s) for s in TRIP["stays"]],
                "events": [dict(e) for e in TRIP["events"]]}
        mutate(trip)
        self.assertEqual(sig(trip), sig(),
                         "an edit that cannot change the summary moved the hash")

    def test_adding_an_event_does_not_move_it(self):
        self._unchanged(lambda t: t["events"].append(
            {"date": DAY, "name": "Sinclair, Benkelman"}))

    def test_editing_a_description_does_not_move_it(self):
        self._unchanged(lambda t: t["events"][0].update(
            description="we talked to a group of men on Harleys"))

    def test_editing_a_campspot_note_does_not_move_it(self):
        """Notes are the most tempting thing to include and still wrong: the
        summary deliberately says nothing the cards below it already say."""
        self._unchanged(lambda t: t["stays"][0].update(notes="rewritten later"))

    def test_the_site_number_does_not_move_it(self):
        self._unchanged(lambda t: t["stays"][0].update(site="14"))

    def test_photos_and_captions_are_not_even_inputs(self):
        """They reach the dossier but never the signature — which is the whole
        reason a nightly run over the library costs nothing."""
        self._unchanged(lambda t: t.update(photos=500, captions=["new one"]))


class TestSignatureCatchesRealChanges(unittest.TestCase):
    """The narrow set is small, so everything in it must actually count."""

    def test_mileage_moving_redrafts_the_day(self):
        self.assertNotEqual(sig(driving={DAY: {"miles": 460, "seconds": 27000}}),
                            sig())

    def test_a_day_gaining_driving_redrafts_it(self):
        self.assertNotEqual(sig(driving={}), sig())

    def test_changing_where_you_slept_redrafts_the_day(self):
        trip = {**TRIP, "stays": [dict(s) for s in TRIP["stays"]]}
        trip["stays"][0]["place"] = "Elmwood Park"
        self.assertNotEqual(sig(trip), sig())

    def test_moving_a_stays_dates_redrafts_the_day(self):
        """A date edit re-sorts the trip and changes which nights bound the
        day — the one edit in the narrow set someone makes by hand."""
        trip = {**TRIP, "stays": [dict(s) for s in TRIP["stays"]]}
        trip["stays"][0]["end"] = "2026-08-30"
        self.assertNotEqual(sig(trip), sig())

    def test_it_is_stable_across_runs(self):
        self.assertEqual(sig(), sig())


class TestSettleGate(unittest.TestCase):
    def _at(self, dt):
        return R.day_settled(DAY, now=dt, settle_s=48 * 3600)

    def ends(self):
        return datetime(2026, 8, 29)          # local midnight after DAY

    def test_a_day_just_over_is_not_settled(self):
        self.assertFalse(self._at(self.ends() + timedelta(minutes=10)))

    def test_a_day_inside_the_refetch_window_is_not_settled(self):
        """The exact case: the trip is still running, the track is still being
        re-polled, and the mileage can still grow."""
        self.assertFalse(self._at(self.ends() + timedelta(hours=47)))

    def test_settled_once_the_window_has_passed(self):
        self.assertTrue(self._at(self.ends() + timedelta(hours=48)))

    def test_the_back_catalogue_is_all_settled(self):
        self.assertTrue(self._at(datetime(2027, 1, 1)))

    def test_the_window_is_measured_from_the_day_not_the_trip(self):
        """One rule covers both cases only because it keys on the day's own
        end — which is what lets a still-running trip have its older days
        written up while today is still being driven."""
        self.assertTrue(R.day_settled("2026-08-20", now=self.ends(),
                                      settle_s=48 * 3600))

    def test_an_undated_day_is_never_settled(self):
        """So it is never drafted — an unparseable date must not read as old."""
        self.assertFalse(R.day_settled("", now=datetime(2030, 1, 1)))
        self.assertFalse(R.day_settled("not-a-date", now=datetime(2030, 1, 1)))

    def test_the_app_owns_the_window(self):
        """The settle window IS the track re-fetch window; main() reads it off
        the app so a tuning change can't leave a stale copy here."""
        import ekko_trips_app as A
        self.assertEqual(A.TRACK_REFETCH_OVERLAP_S, R.SETTLE_AFTER_S)


if __name__ == "__main__":
    unittest.main()
