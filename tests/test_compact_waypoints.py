"""Which waypoints collapse to a one-line row.

Folding runs of them into "N brief stops" chips was withdrawn: a fuel stop
outside a town you remember is a landmark in the day's sequence even carrying
nothing to read, and hiding it took away the scaffolding a reader navigates by.
The answer instead is a lighter RENDERING — every stop still visible, still in
its own slot, at about a third the height.

The predicate is the load-bearing part, and it is deliberately narrower than
the folding one was: a family visit is never a throwaway, and anything still
flagged for review has to stay findable.

    python -m unittest tests.test_compact_waypoints -v
"""

import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ekko_trips_app as A  # noqa: E402


def _render(trip_id=95):
    client = A.app.test_client()
    import json
    with open(os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "users.json")) as fh:
        admin = next(u for u, v in json.load(fh).items() if v.get("is_admin"))
    with client.session_transaction() as sess:
        sess["_user_id"] = admin
        sess["_fresh"] = True
    return client.get(f"/trips/{trip_id}").data.decode("utf-8", "replace")


class TestThePredicate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = _render()

    def _cards(self):
        return re.findall(r'<div class="(event-card[^"]*)" id="event-\d+"', self.html)

    def test_some_waypoints_render_as_rows(self):
        self.assertTrue([c for c in self._cards() if "wp-compact" in c])

    def test_a_row_is_always_a_waypoint(self):
        for c in self._cards():
            if "wp-compact" in c:
                self.assertIn("waypoint", c)
                self.assertNotIn("family-visit", c)

    def test_a_flagged_stop_is_never_a_row(self):
        # The "Needs review" badge exists to be found; a row is not where you
        # find things.
        for c in self._cards():
            if "needs-vetting" in c:
                self.assertNotIn("wp-compact", c)

    def test_a_row_keeps_bare_so_a_drag_can_still_target_it(self):
        # `body.photo-dragging .event-card.bare .event-body` is what reveals a
        # drop target on a card with no photos. Dropping the class would make
        # every compact row untargetable.
        for c in self._cards():
            if "wp-compact" in c:
                self.assertIn("bare", c)

    def test_a_waypoint_with_something_to_read_keeps_its_card(self):
        # Photos and descriptions are the escape hatch — the row is never
        # hiding anything.
        self.assertTrue([c for c in self._cards()
                         if "waypoint" in c and "wp-compact" not in c],
                        "every waypoint collapsed; the escape hatch is broken")


class TestWhatARowShows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = _render()

    def test_a_row_drops_the_date_the_divider_already_gives(self):
        row = re.search(r'wp-compact[\s\S]{0,900}?<div class="event-meta">\s*([^<]*)',
                        self.html)
        self.assertIsNotNone(row)
        self.assertNotRegex(row.group(1), r"\d{4}-\d{2}-\d{2}")

    def test_a_full_card_still_carries_its_date(self):
        m = re.search(r'<div class="event-card(?![^"]*wp-compact)[^"]*" id="event-\d+"'
                      r'[\s\S]{0,1600}?<div class="event-meta">\s*([^<]*)', self.html)
        self.assertIsNotNone(m)
        self.assertRegex(m.group(1), r"\d{4}-\d{2}-\d{2}")

    def test_a_row_does_not_say_the_same_place_twice(self):
        # "Point of Rocks · Point of Rocks, MD" spends most of a line saying
        # nothing.
        for name, where in re.findall(
                r'wp-compact[\s\S]{0,900}?<h3>([^<]*)(?:<span class="card-where">([^<]*)</span>)?',
                self.html):
            if where:
                self.assertFalse(where.lower().startswith(name.lower().strip()),
                                 f"{name!r} repeated by {where!r}")


if __name__ == "__main__":
    unittest.main()
