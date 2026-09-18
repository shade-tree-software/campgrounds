"""`recgov_hookups.derive`: what a facility's RIDB campsites establish.

The rules are about when silence stays silence (doc §2.1). A catalog is dense
where it says ELECTRIC / NONELECTRIC in the site type and sparse everywhere
else, so a derivation that read a missing Water Hookup as "no" would write
thousands of false negatives — and the map's Hookups filter HIDES a measured no
where it only fades an unknown.

Run from the project root:

    python -m unittest tests.test_recgov_hookups -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import recgov_hookups as R


def site(t, equip=(), name="", reservable=True, **attrs):
    names = {"elec": "Electricity Hookup", "water": "Water Hookup",
             "sewer": "Sewer Hookup"}
    return {"type": t, "equip": list(equip), "name": name,
            "reservable": reservable,
            "attrs": {names[k]: v for k, v in attrs.items()}}


class TestDerive(unittest.TestCase):

    def test_highest_amperage_wins(self):
        got = R.derive([site("STANDARD ELECTRIC", elec="30"),
                        site("RV ELECTRIC", elec="20/30/50"),
                        site("STANDARD NONELECTRIC")])
        self.assertEqual(got["electric"], 50)

    def test_all_nonelectric_is_a_measured_zero(self):
        got = R.derive([site("STANDARD NONELECTRIC"), site("RV NONELECTRIC")])
        self.assertEqual(got, {"electric": 0})

    def test_one_untyped_site_keeps_electric_unknown(self):
        """A type saying neither is silence, so 0 would be a guess."""
        got = R.derive([site("STANDARD NONELECTRIC"), site("STANDARD")])
        self.assertNotIn("electric", got)

    def test_electric_site_without_amperage_writes_nothing(self):
        """The schema holds amps, and inventing 30 is a placeholder."""
        got = R.derive([site("STANDARD ELECTRIC", elec="")])
        self.assertNotIn("electric", got)

    def test_amperage_snaps_down_never_up(self):
        self.assertEqual(R.derive([site("RV ELECTRIC", elec="40")])["electric"], 30)
        self.assertNotIn("electric", R.derive([site("RV ELECTRIC", elec="15")]))

    def test_missing_water_attribute_is_not_a_no(self):
        got = R.derive([site("STANDARD ELECTRIC", elec="30", water="No"),
                        site("STANDARD NONELECTRIC")])
        self.assertNotIn("water", got, "one site said nothing")

    def test_every_site_saying_no_is_a_no(self):
        got = R.derive([site("STANDARD ELECTRIC", elec="30", water="No", sewer="N"),
                        site("STANDARD NONELECTRIC", water="No", sewer="No")])
        self.assertIs(got["water"], False)
        self.assertIs(got["sewer"], False)

    def test_any_yes_is_a_yes(self):
        got = R.derive([site("RV ELECTRIC", elec="50", water="Yes", sewer="Y"),
                        site("STANDARD NONELECTRIC")])
        self.assertIs(got["water"], True)
        self.assertIs(got["sewer"], True)

    def test_only_sites_an_rv_can_book_count(self):
        """Group, tent-only, walk-to and host sites answer a different question."""
        got = R.derive([site("GROUP STANDARD ELECTRIC", elec="50"),
                        site("TENT ONLY ELECTRIC", elec="30"),
                        site("MANAGEMENT", elec="50"),
                        site("STANDARD NONELECTRIC")])
        self.assertEqual(got, {"electric": 0})

    def test_a_standard_site_listing_only_tents_is_not_an_rv_site(self):
        got = R.derive([site("STANDARD ELECTRIC", equip=["TENT"], elec="50"),
                        site("STANDARD NONELECTRIC", equip=["RV", "TENT"])])
        self.assertEqual(got, {"electric": 0})

    def test_a_site_named_host_is_not_a_public_site(self):
        """Boise Creek: the only electric site is a STANDARD ELECTRIC called Host."""
        got = R.derive([site("STANDARD ELECTRIC", name="Host", elec="50",
                             water="Yes"),
                        site("STANDARD NONELECTRIC")])
        self.assertEqual(got, {"electric": 0})

    def test_a_lone_unbookable_electric_site_may_be_the_hosts(self):
        """AWH: it may never be available to the public. Unknown, never 0."""
        got = R.derive([site("RV ELECTRIC", reservable=False, elec="50",
                             water="Yes", sewer="Yes"),
                        site("STANDARD NONELECTRIC", reservable=False)])
        self.assertEqual(got, {})

    def test_a_lone_bookable_electric_site_is_public(self):
        """Reservable on recreation.gov means anyone can book it."""
        got = R.derive([site("STANDARD ELECTRIC", elec="30"),
                        site("STANDARD NONELECTRIC")])
        self.assertEqual(got["electric"], 30)

    def test_the_host_rule_only_applies_to_a_few_electric_sites(self):
        """An all-walk-up campground with 20 electric sites is not one host pad."""
        sites = [site("STANDARD ELECTRIC", reservable=False, elec="50")
                 for _ in range(20)]
        self.assertEqual(R.derive(sites)["electric"], 50)

    def test_no_rv_sites_says_nothing(self):
        self.assertEqual(R.derive([site("TENT ONLY NONELECTRIC")]), {})
        self.assertEqual(R.derive([]), {})


class TestUnstablePaging(unittest.TestCase):
    """RIDB's offset paging can repeat one site and skip another."""

    def test_pages_are_reread_until_every_site_is_seen(self):
        ids = [str(i) for i in range(60)]
        reads = {"n": 0}

        def fake_get(path, params):
            # First read: page two repeats site 10 and never returns site 59.
            # Later reads are clean.
            off = params["offset"]
            first = reads["n"] < 2
            reads["n"] += 1
            page = ids[off:off + 50]
            if first and off == 50:
                page = ids[50:59] + ["10"]
            return {"RECDATA": [{"CampsiteID": i} for i in page],
                    "METADATA": {"RESULTS": {"TOTAL_COUNT": 60}}}

        real = R._get_paced
        R._get_paced = fake_get
        try:
            got = R.fetch_campsites("1")
        finally:
            R._get_paced = real
        self.assertEqual(sorted(str(s["CampsiteID"]) for s in got), sorted(ids))


class TestPlan(unittest.TestCase):
    """Held values are never overwritten, and a person's reading is never touched."""

    def rows(self, **entry):
        base = {"id": 1, "name": "X", "kind": "campground",
                "website": "https://www.recreation.gov/camping/campgrounds/999"}
        base.update(entry)
        return [base]

    CACHE = {"999": {"fetched": "2026-09-18",
                     "sites": [site("STANDARD NONELECTRIC")]}}

    def test_fills_an_absent_key(self):
        fills, conflicts, _ = R.plan(self.rows(), self.CACHE)
        self.assertEqual(fills, {1: {"electric": 0}})
        self.assertEqual(conflicts, [])

    def test_a_disagreement_is_reported_not_written(self):
        fills, conflicts, _ = R.plan(self.rows(hookups={"electric": 30}), self.CACHE)
        self.assertEqual(fills, {})
        self.assertEqual([(k, h, r) for _, k, h, r in conflicts], [("electric", 30, 0)])

    def test_a_person_outranks_the_catalog(self):
        rows = self.rows(provenance={"hookups": {"method": "manual",
                                                 "source": "x", "checked": "2026"}})
        fills, conflicts, skipped = R.plan(rows, self.CACHE)
        self.assertEqual(fills, {})
        self.assertEqual(skipped["hookups verified by a person"], 1)

    def test_a_facility_two_entries_share_is_left_alone(self):
        rows = self.rows() + [dict(self.rows()[0], id=2, name="Y")]
        fills, _, skipped = R.plan(rows, self.CACHE)
        self.assertEqual(fills, {})
        self.assertEqual(skipped["facility shared by several entries"], 2)


if __name__ == "__main__":
    unittest.main()
