"""A waypoint only earns a timeline card by carrying something worth reading.

Detect Stops is generous on purpose — 747 of the library's 1,116 events are
waypoints, 68 on trip 95 alone — so rendering every one of them buries the days
the timeline exists to describe. `_collapse_waypoint_runs` folds runs of the
empty ones into a single "N brief stops" chip.

Two rules do the work, and both are easy to break by accident:

  * A waypoint escapes folding if it has PHOTOS, a DESCRIPTION, or (for an
    admin) an unvetted flag that still wants attention. Photos are the one the
    owner named: nobody cares that we stopped at a gas station, unless there's
    a picture of it.
  * A run folds IN PLACE, so it may never straddle a day boundary — a day
    divider is emitted between two dates and a chip cannot span one.

Run from the project root with the venv active:

    python -m unittest tests.test_waypoint_runs -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ekko_trips_app import _collapse_waypoint_runs  # noqa: E402

D1, D2 = "2026-08-19", "2026-08-20"


def _wp(idx, date=D1, **kw):
    item = {"type": "event", "idx": idx, "sort_date": date, "waypoint": True,
            "name": "Stop %d" % idx, "description": ""}
    item.update(kw)
    return item


def _event(idx, date=D1, **kw):
    item = {"type": "event", "idx": idx, "sort_date": date, "waypoint": False,
            "name": "Event %d" % idx, "description": "A real event"}
    item.update(kw)
    return item


def _stay(idx, date=D1):
    return {"type": "stay", "idx": idx, "sort_date": date}


def _run(timeline, photos=None, is_admin=False):
    _collapse_waypoint_runs(timeline, photos or {}, is_admin)
    return [bool(i.get("wp_collapsed")) for i in timeline]


class TestWhatEarnsACard(unittest.TestCase):
    def test_empty_waypoint_folds(self):
        self.assertEqual(_run([_wp(0)]), [True])

    def test_waypoint_with_photos_keeps_its_card(self):
        # The owner's rule: a photo is what makes a gas station worth a row.
        self.assertEqual(_run([_wp(0)], photos={0: [{"filename": "a.jpg"}]}),
                         [False])

    def test_waypoint_with_description_keeps_its_card(self):
        self.assertEqual(_run([_wp(0, description="Great pie")]), [False])

    def test_whitespace_description_is_not_a_description(self):
        self.assertEqual(_run([_wp(0, description="   ")]), [True])

    def test_regular_events_and_stays_never_fold(self):
        self.assertEqual(_run([_event(0), _stay(0)]), [False, False])

    def test_family_visit_never_folds(self):
        self.assertEqual(_run([_wp(0, family_visit="Grandma")]), [False])

    def test_unvetted_waypoint_stays_visible_for_admins_only(self):
        # The "Needs review" badge exists to be findable; folding it away would
        # hide the one thing the admin is meant to act on. A reader has no
        # badge to look for, so for them it is just another brief stop.
        self.assertEqual(_run([_wp(0, needs_vetting=True)], is_admin=True),
                         [False])
        self.assertEqual(_run([_wp(0, needs_vetting=True)], is_admin=False),
                         [True])


class TestRunBoundaries(unittest.TestCase):
    def test_run_breaks_on_a_card_worthy_item(self):
        timeline = [_wp(0), _wp(1), _event(2), _wp(3), _wp(4)]
        self.assertEqual(_run(timeline), [True, True, False, True, True])
        self.assertEqual(timeline[0]["wp_run_len"], 2)
        self.assertEqual(timeline[3]["wp_run_len"], 2)
        self.assertNotIn("wp_run_len", timeline[1])
        self.assertNotIn("wp_run_len", timeline[4])

    def test_run_never_straddles_a_day_boundary(self):
        # A day divider renders between these two, so one chip cannot cover
        # both — they must be two runs.
        timeline = [_wp(0, date=D1), _wp(1, date=D2)]
        self.assertEqual(_run(timeline), [True, True])
        self.assertEqual(timeline[0]["wp_run_len"], 1)
        self.assertEqual(timeline[1]["wp_run_len"], 1)
        self.assertNotEqual(timeline[0]["wp_run_id"], timeline[1]["wp_run_id"])

    def test_members_of_one_run_share_an_id(self):
        timeline = [_wp(7), _wp(8), _wp(9)]
        _run(timeline)
        ids = {i["wp_run_id"] for i in timeline}
        self.assertEqual(ids, {"wp-7"})       # the head's idx names the run
        self.assertEqual(timeline[0]["wp_run_len"], 3)

    def test_chip_tooltip_names_the_folded_stops(self):
        timeline = [_wp(0, name="Point of Rocks"), _wp(1, name="Sheetz")]
        _run(timeline)
        self.assertEqual(timeline[0]["wp_run_names"],
                         "Point of Rocks · Sheetz")

    def test_trailing_run_is_closed(self):
        # The final run has no following item to trigger the close, so the
        # loop's tail has to do it. Miss this and the last chip never renders.
        timeline = [_event(0), _wp(1), _wp(2)]
        _run(timeline)
        self.assertEqual(timeline[1]["wp_run_len"], 2)


if __name__ == "__main__":
    unittest.main()
