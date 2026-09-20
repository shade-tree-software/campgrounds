"""The Good Sam directory match, and what it is allowed to conclude.

Every rule here exists because the first run got it wrong on real data: the
subset names wrote a discount onto three public campgrounds, and the bands are
what let a legitimate pair sit 1.9 km apart (the directory geocodes a mailing
address; this database pins the campground).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import goodsam_discounts as gs


def park(name, lat, lng, is_gs=False, military=False, pid="p1"):
    return {"id": pid, "name": name, "lat": lat, "lng": lng, "gs": is_gs,
            "military": military, "city": None, "state": None, "country": "US",
            "type": None, "advertiser": None, "phone": None}


def entry(name, lat, lng, ownership="private", eid=1, **extra):
    row = {"id": eid, "kind": "campground", "name": name,
           "location": f"{lat},{lng}", "ownership": ownership}
    row.update(extra)
    return row


def at(lat, lng, metres, bearing_east=True):
    """A coordinate `metres` away, east or north."""
    deg = metres / 111320.0
    return (lat, lng + deg) if bearing_east else (lat + deg, lng)


class SimilarityTest(unittest.TestCase):
    def test_whole_match_on_identical_names(self):
        score, whole = gs.similarity("Shoshone RV Park", "Shoshone RV Park")
        self.assertEqual(score, 1.0)
        self.assertTrue(whole)

    def test_noise_words_do_not_matter(self):
        score, whole = gs.similarity("Shoshone RV Park", "Shoshone Campground")
        self.assertEqual(score, 1.0)
        self.assertTrue(whole)

    def test_punctuation_and_spelling_still_whole(self):
        # "Ballard's" vs "Ballards" is the same park 1.4 km from its mailing pin.
        _score, whole = gs.similarity("Ballards Campground & RV Park",
                                      "Ballard's Campground & RV Park")
        self.assertTrue(whole)

    def test_subset_name_scores_high_but_is_not_whole(self):
        # The failure this guard exists for: a private park whose name is
        # contained in a state park's, 1.7 km away.
        score, whole = gs.similarity("Eagle Nest Lake State Park", "Camp Eagle Nest")
        self.assertGreaterEqual(score, 0.9)
        self.assertFalse(whole)

    def test_good_sam_parent_child_naming(self):
        # Good Sam writes public campgrounds as `Parent/Child`.
        _score, whole = gs.similarity("Keller Ferry Campground",
                                      "Lake Roosevelt NRA/Keller Ferry Campground")
        self.assertTrue(whole)

    def test_parenthetical_is_a_variant(self):
        score, _whole = gs.similarity("Riverview Campground (Madison)", "Riverview Campground")
        self.assertEqual(score, 1.0)

    def test_distinguishing_modifier_is_a_veto(self):
        # Silver Lake East and Silver Lake West are different campgrounds.
        score, whole = gs.similarity("Silver Lake West Campground", "Silver Lake East")
        self.assertLessEqual(score, 0.45)
        self.assertFalse(whole)


class BandTest(unittest.TestCase):
    def test_far_pair_needs_a_whole_match(self):
        self.assertTrue(gs.accepts(1.0, True, 1900))
        self.assertFalse(gs.accepts(1.0, False, 1900))

    def test_close_pair_tolerates_a_subset(self):
        self.assertTrue(gs.accepts(0.7, False, 200))

    def test_nothing_is_accepted_past_the_search_radius(self):
        self.assertFalse(gs.accepts(1.0, True, 3500))

    def test_a_poor_name_is_never_rescued_by_distance(self):
        # Two different parks 90 m apart: "Sabine River RV Park" / "Tiger Town".
        self.assertFalse(gs.accepts(0.3, False, 5))


class MatchTest(unittest.TestCase):
    def setUp(self):
        self.lat, self.lng = 40.0, -75.0

    def grid(self, *parks):
        return gs.build_grid({p["id"]: p for p in parks})

    def test_matches_the_listing_at_the_same_place(self):
        grid = self.grid(park("Shoshone RV Park", *at(self.lat, self.lng, 40), is_gs=True))
        found = gs.match(entry("Shoshone RV Park", self.lat, self.lng), grid)
        self.assertIsNotNone(found)
        self.assertTrue(found[0]["gs"])

    def test_no_match_when_nothing_is_near(self):
        grid = self.grid(park("Shoshone RV Park", 41.0, -76.0, is_gs=True))
        self.assertIsNone(gs.match(entry("Shoshone RV Park", self.lat, self.lng), grid))

    def test_disagreeing_neighbours_are_ambiguous_not_guessed(self):
        # A resort next door to the county park, both plausible, one a network
        # park: answering either way invents a fact.
        grid = self.grid(
            park("Lakeview Campground", *at(self.lat, self.lng, 60), is_gs=True, pid="a"),
            park("Lakeview Camp", *at(self.lat, self.lng, 90), is_gs=False, pid="b"))
        self.assertIsNone(gs.match(entry("Lakeview Campground", self.lat, self.lng), grid))

    def test_agreeing_neighbours_are_not_ambiguous(self):
        grid = self.grid(
            park("Lakeview Campground", *at(self.lat, self.lng, 60), is_gs=False, pid="a"),
            park("Lakeview Camp", *at(self.lat, self.lng, 90), is_gs=False, pid="b"))
        self.assertIsNotNone(gs.match(entry("Lakeview Campground", self.lat, self.lng), grid))

    def test_entry_without_coordinates_is_skipped(self):
        grid = self.grid(park("Shoshone RV Park", self.lat, self.lng, is_gs=True))
        row = entry("Shoshone RV Park", self.lat, self.lng)
        row["location"] = ""
        self.assertIsNone(gs.match(row, grid))


class DeriveTest(unittest.TestCase):
    def test_network_park_gives_the_discount(self):
        found = gs.derive(park("X", 0, 0, is_gs=True), entry("X", 0, 0))
        self.assertEqual(found["good_sam"], True)

    def test_listed_private_park_that_is_not_a_network_park_is_a_measured_no(self):
        found = gs.derive(park("X", 0, 0, is_gs=False), entry("X", 0, 0, ownership="private"))
        self.assertEqual(found["good_sam"], False)

    def test_public_campground_gets_no_negative(self):
        # A national forest campground carrying "no Good Sam discount" is noise;
        # the positive is still written wherever it is found (AWH 2026-09-20).
        found = gs.derive(park("X", 0, 0, is_gs=False), entry("X", 0, 0, ownership="federal"))
        self.assertNotIn("good_sam", found)
        found = gs.derive(park("X", 0, 0, is_gs=True), entry("X", 0, 0, ownership="federal"))
        self.assertEqual(found["good_sam"], True)

    def test_military_is_true_only(self):
        self.assertEqual(gs.derive(park("X", 0, 0, military=True), entry("X", 0, 0))["military"],
                         True)
        self.assertNotIn("military", gs.derive(park("X", 0, 0, military=False), entry("X", 0, 0)))


class PlanTest(unittest.TestCase):
    def setUp(self):
        self.lat, self.lng = 39.5, -76.5
        self.parks = {"a": park("Shoshone RV Park", *at(self.lat, self.lng, 30),
                                is_gs=True, military=True, pid="a")}

    def test_fills_an_absent_key(self):
        rows = [entry("Shoshone RV Park", self.lat, self.lng)]
        fills, conflicts, matches, _skipped = gs.plan(rows, self.parks)
        self.assertEqual(fills, {1: {"good_sam": True, "military": True}})
        self.assertEqual(conflicts, [])
        self.assertEqual(len(matches), 1)

    def test_a_person_is_never_overwritten(self):
        rows = [entry("Shoshone RV Park", self.lat, self.lng,
                      discounts={"good_sam": False},
                      provenance={"discounts": {"source": "called the park",
                                                "checked": "2026-01-01",
                                                "method": "reported"}})]
        fills, conflicts, _matches, skipped = gs.plan(rows, self.parks)
        self.assertEqual(fills, {})
        self.assertEqual(conflicts, [])
        self.assertIn("discounts verified by a person", skipped)

    def test_a_held_machine_value_is_reported_not_replaced(self):
        rows = [entry("Shoshone RV Park", self.lat, self.lng,
                      discounts={"good_sam": False})]
        fills, conflicts, _matches, _skipped = gs.plan(rows, self.parks)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(fills, {1: {"military": True}})
        self.assertNotIn("good_sam", fills[1])

    def test_family_entries_are_not_campgrounds(self):
        rows = [dict(entry("Shoshone RV Park", self.lat, self.lng), kind="family")]
        fills, _conflicts, matches, _skipped = gs.plan(rows, self.parks)
        self.assertEqual((fills, matches), ({}, []))


if __name__ == "__main__":
    unittest.main()
