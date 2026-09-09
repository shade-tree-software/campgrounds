"""Visit windows: when did we arrive at, and leave, one particular place?

Backs the timeline cards' "Times from GPS" button, which exists because a card
added on the road carries the moment the admin opened the form rather than the
moment they arrived, and almost never an end time.

The tests pin the two rules that make it different from stop detection, both of
which come from how a phone actually reports:

  - a parked phone's fix wanders, so a visit must survive pings that drift out
    past the at-place radius without ever really leaving, and
  - a still phone stops reporting, so a genuine multi-hour dwell can be an
    arrival ping and a departure ping with nothing in between — elapsed time
    must never split a visit.

Run from the project root with the venv active:

    python -m unittest tests.test_visit_windows -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ekko_trips_app import (  # noqa: E402
    VISIT_AT_PLACE_M, VISIT_DEPART_M, _pick_visit, _visit_windows_at,
)

PLACE_LAT, PLACE_LNG = 40.0, -105.0
TZ = "America/Denver"
# 2026-08-27 08:00 local (14:00 UTC).
T0 = 1787839200
M_PER_DEG_LAT = 111320.0


def _ping(offset_s, meters_north):
    return {"tst": T0 + offset_s,
            "lat": PLACE_LAT + meters_north / M_PER_DEG_LAT,
            "lon": PLACE_LNG,
            "tz": TZ}


def _windows(*pairs):
    return _visit_windows_at([_ping(o, m) for (o, m) in pairs],
                             PLACE_LAT, PLACE_LNG)


class TestVisitWindows(unittest.TestCase):

    def test_radii_are_ordered(self):
        # The whole two-radius scheme collapses if these ever cross.
        self.assertLess(VISIT_AT_PLACE_M, VISIT_DEPART_M)

    def test_arrival_and_departure_are_the_first_and_last_fix(self):
        visits = _windows((0, 20), (300, 60), (600, 40), (900, 9000))
        self.assertEqual(len(visits), 1)
        self.assertEqual(visits[0]["start_tst"], T0)
        self.assertEqual(visits[0]["end_tst"], T0 + 600)
        self.assertEqual(visits[0]["ping_count"], 3)
        self.assertEqual(visits[0]["tz"], TZ)

    def test_drift_between_the_two_radii_does_not_end_the_visit(self):
        # A parked phone reporting 450 m off is still parked: it neither
        # extends the visit nor ends it.
        visits = _windows((0, 20), (300, 450), (600, 30), (900, 9000))
        self.assertEqual(len(visits), 1)
        self.assertEqual(visits[0]["end_tst"], T0 + 600)
        self.assertEqual(visits[0]["ping_count"], 2)

    def test_a_long_silence_is_not_a_departure(self):
        # Four hours between two fixes with nothing in between is what a
        # stationary phone looks like, not two visits.
        visits = _windows((0, 20), (4 * 3600, 40))
        self.assertEqual(len(visits), 1)
        self.assertEqual(visits[0]["end_tst"], T0 + 4 * 3600)

    def test_leaving_and_coming_back_is_two_visits(self):
        visits = _windows((0, 20), (300, 30),
                          (900, 9000), (1200, 12000), (1800, 9000),
                          (2400, 40), (2700, 25))
        self.assertEqual(len(visits), 2)
        self.assertEqual(
            [(v["start_tst"] - T0, v["end_tst"] - T0) for v in visits],
            [(0, 300), (2400, 2700)])

    def test_no_fixes_near_the_place_is_no_visit(self):
        self.assertEqual(_windows((0, 9000), (300, 12000)), [])

    def test_a_rival_card_keeps_its_own_pings(self):
        # Trip 95: North Park and the Hy-Vee 346 m away sit inside each
        # other's fringe band, so without the rival test the supermarket's
        # visit swallowed the hour at the park.
        rival = (PLACE_LAT + 346 / M_PER_DEG_LAT, PLACE_LNG)
        # The park's own fixes land 280 m out — inside this place's at-place
        # radius, but far nearer the park than here.
        pings = [_ping(0, 280), _ping(300, 290),      # at the rival
                 _ping(600, 30), _ping(900, 20)]      # at the place
        visits = _visit_windows_at(pings, PLACE_LAT, PLACE_LNG,
                                   other_anchors=[rival])
        self.assertEqual(len(visits), 1)
        self.assertEqual(visits[0]["start_tst"], T0 + 600)
        # Without the rival the whole run reads as one visit here, which is
        # the bug: an 18:02 stop reported as starting at 17:02.
        merged = _visit_windows_at(pings, PLACE_LAT, PLACE_LNG)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["start_tst"], T0)

    def test_a_distant_rival_costs_nothing(self):
        # Rivals beyond depart_m + at_place_m can never win a ping from
        # here, and are dropped before the per-ping scan.
        far = (PLACE_LAT + 5000 / M_PER_DEG_LAT, PLACE_LNG)
        with_rival = _visit_windows_at([_ping(0, 20), _ping(300, 40)],
                                       PLACE_LAT, PLACE_LNG,
                                       other_anchors=[far])
        self.assertEqual(len(with_rival), 1)
        self.assertEqual(with_rival[0]["ping_count"], 2)

    def test_a_single_fix_is_a_zero_length_visit(self):
        # Real: a drive-through waypoint the track caught once. The caller
        # reports the arrival and leaves the end time blank rather than
        # inventing a visit that started and ended at the same instant.
        visits = _windows((0, 9000), (300, 40), (600, 9000))
        self.assertEqual(len(visits), 1)
        self.assertEqual(visits[0]["start_tst"], visits[0]["end_tst"])


class TestPickVisit(unittest.TestCase):

    def _visits(self):
        return [
            {"start_tst": T0, "end_tst": T0 + 3600, "ping_count": 5},
            {"start_tst": T0 + 7200, "end_tst": T0 + 7500, "ping_count": 2},
        ]

    def test_the_visit_containing_the_cards_time_wins(self):
        visit, gap = _pick_visit(self._visits(), T0 + 1800)
        self.assertEqual(visit["start_tst"], T0)
        self.assertEqual(gap, 0)

    def test_otherwise_the_nearest_visit_wins(self):
        visit, gap = _pick_visit(self._visits(), T0 + 7000)
        self.assertEqual(visit["start_tst"], T0 + 7200)
        self.assertEqual(gap, 200)

    def test_with_no_time_on_the_card_the_longest_visit_wins(self):
        visit, gap = _pick_visit(self._visits(), None)
        self.assertEqual(visit["start_tst"], T0)
        self.assertIsNone(gap)

    def test_no_visits_picks_nothing(self):
        self.assertEqual(_pick_visit([], T0), (None, None))


if __name__ == "__main__":
    unittest.main()
