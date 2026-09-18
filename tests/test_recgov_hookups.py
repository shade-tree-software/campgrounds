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


def pad(*sites, n=3, plain="STANDARD NONELECTRIC"):
    """`sites` plus `n` plain bookable RV sites: a catalog, not a placeholder."""
    return list(sites) + [site(plain) for _ in range(n)]


class TestDerive(unittest.TestCase):

    def test_highest_amperage_wins(self):
        got = R.derive(pad(site("STANDARD ELECTRIC", elec="30"),
                           site("RV ELECTRIC", elec="20/30/50"),
                           site("RV ELECTRIC", elec="30")))
        self.assertEqual(got["electric"], 50)

    def test_all_nonelectric_is_a_measured_zero(self):
        self.assertEqual(R.derive(pad(site("RV NONELECTRIC"))), {"electric": 0})

    def test_one_untyped_site_keeps_electric_unknown(self):
        """A type saying neither is silence, so 0 would be a guess."""
        self.assertNotIn("electric", R.derive(pad(site("STANDARD"))))

    def test_electric_site_without_amperage_writes_nothing(self):
        """The schema holds amps, and inventing 30 is a placeholder."""
        got = R.derive(pad(site("STANDARD ELECTRIC", elec=""), n=4))
        self.assertNotIn("electric", got)

    def test_amperage_snaps_down_never_up(self):
        got = R.derive([site("RV ELECTRIC", elec="40") for _ in range(3)])
        self.assertEqual(got["electric"], 30)
        got = R.derive([site("RV ELECTRIC", elec="15") for _ in range(3)])
        self.assertNotIn("electric", got)

    def test_missing_water_attribute_is_not_a_no(self):
        got = R.derive(pad(site("STANDARD ELECTRIC", elec="30", water="No")))
        self.assertNotIn("water", got, "the padding sites said nothing")

    def test_every_site_saying_no_is_a_no(self):
        sites = [site("STANDARD ELECTRIC", elec="30", water="No", sewer="N")
                 for _ in range(3)]
        got = R.derive(sites)
        self.assertIs(got["water"], False)
        self.assertIs(got["sewer"], False)

    def test_a_hookup_loop_is_a_yes(self):
        sites = [site("RV ELECTRIC", elec="50", water="Yes", sewer="Y")
                 for _ in range(3)]
        got = R.derive(pad(*sites, n=6))
        self.assertIs(got["water"], True)
        self.assertIs(got["sewer"], True)

    def test_one_or_two_stray_water_yeses_are_noise(self):
        """Emery Bay, Wheeler Peak: a no-hookup campground, two odd attributes."""
        got = R.derive(pad(site("STANDARD NONELECTRIC", water="Yes"),
                           site("STANDARD NONELECTRIC", water="Yes"), n=20))
        self.assertNotIn("water", got)

    def test_only_sites_an_rv_can_book_count(self):
        """Group, tent-only, walk-to and host sites answer a different question."""
        got = R.derive(pad(site("GROUP STANDARD ELECTRIC", elec="50"),
                           site("TENT ONLY ELECTRIC", elec="30"),
                           site("MANAGEMENT", elec="50")))
        self.assertEqual(got, {"electric": 0})

    def test_a_standard_site_listing_only_tents_is_not_an_rv_site(self):
        got = R.derive(pad(site("STANDARD ELECTRIC", equip=["TENT"], elec="50"),
                           site("STANDARD NONELECTRIC", equip=["RV", "TENT"])))
        self.assertEqual(got, {"electric": 0})

    def test_a_site_named_host_is_not_a_public_site(self):
        """Boise Creek's "Host", Mount Rose's "1Host", Lottis Creek's "Host 1A"."""
        for name in ("Host", "1Host", "Host 1A", "Host Site 15"):
            with self.subTest(name=name):
                got = R.derive(pad(site("STANDARD ELECTRIC", name=name,
                                        elec="50", water="Yes")))
                self.assertEqual(got, {"electric": 0})

    def test_ghost_is_not_host(self):
        got = R.derive(pad(site("STANDARD ELECTRIC", name="Ghost Ranch 1",
                                elec="30")))
        self.assertEqual(got["electric"], 30)

    def test_a_lone_unbookable_electric_site_may_be_the_hosts(self):
        """AWH: it may never be available to the public. Unknown, never 0."""
        got = R.derive(pad(site("RV ELECTRIC", reservable=False, elec="50",
                                water="Yes", sewer="Yes")))
        self.assertNotIn("electric", got)

    def test_a_lone_bookable_electric_site_is_public(self):
        """Reservable on recreation.gov means anyone can book it."""
        got = R.derive(pad(site("STANDARD ELECTRIC", elec="30")))
        self.assertEqual(got["electric"], 30)

    def test_unbookable_hookup_sites_at_a_bookable_campground_are_staff(self):
        """Los Alamos: 90 bookable no-hookup sites, 3 unbookable with water+sewer."""
        staff = [site("STANDARD NONELECTRIC", reservable=False, water="Yes",
                      sewer="Y") for _ in range(3)]
        got = R.derive(pad(*staff, n=40))
        self.assertNotIn("water", got)
        self.assertNotIn("sewer", got)

    def test_a_few_unbookable_50_amp_pads_are_staff(self):
        """Mott Park: 28 bookable 30-amp sites, 3 unbookable 50-amp pads + 1 spare."""
        pads = [site("STANDARD ELECTRIC", reservable=False, elec="50")
                for _ in range(3)]
        spare = [site("STANDARD ELECTRIC", reservable=False, elec="30")]
        loop = [site("STANDARD ELECTRIC", elec="30") for _ in range(28)]
        self.assertEqual(R.derive(pads + spare + loop)["electric"], 30)

    def test_amperage_comes_from_the_bookable_sites(self):
        """Whiteface: a real walk-up loop, but its one 50-amp pad isn't public."""
        booked = [site("STANDARD ELECTRIC", elec="30") for _ in range(16)]
        walkup = ([site("STANDARD ELECTRIC", reservable=False) for _ in range(9)]
                  + [site("STANDARD ELECTRIC", reservable=False, elec="50")])
        self.assertEqual(R.derive(booked + walkup)["electric"], 30)

    def test_a_walkup_loop_at_a_bookable_campground_counts(self):
        """South Rim: Loop B is 22 unbookable electric sites, a real loop."""
        loop_b = [site("STANDARD ELECTRIC", reservable=False, elec="30")
                  for _ in range(22)]
        got = R.derive(pad(*loop_b, n=25))
        self.assertEqual(got["electric"], 30)

    def test_an_all_walkup_campground_counts_every_site(self):
        """No site is bookable, so bookability can't single out the host."""
        sites = [site("STANDARD ELECTRIC", reservable=False, elec="50")
                 for _ in range(20)]
        self.assertEqual(R.derive(sites)["electric"], 50)

    def test_a_placeholder_catalog_says_nothing(self):
        """Long Pool: one dummy site stands in for a 38-site campground."""
        self.assertEqual(R.derive([site("STANDARD NONELECTRIC", reservable=False)]), {})
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
                     "sites": pad()}}

    def test_fills_an_absent_key(self):
        fills, conflicts, _ = R.plan(self.rows(), self.CACHE)
        self.assertEqual(fills, {1: {"electric": 0}})
        self.assertEqual(conflicts, [])

    def test_the_catalog_replaces_a_note_derived_value(self):
        """AWH: trust current rec.gov over older auto-generated notes."""
        rows = self.rows(hookups={"electric": 30},
                         provenance={"hookups": {"method": "derived",
                                                 "source": "note prose",
                                                 "checked": "2026"}})
        fills, conflicts, _ = R.plan(rows, self.CACHE)
        self.assertEqual(fills, {1: {"electric": 0}})
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
