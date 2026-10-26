"""Popup link labels, run through the real `static/campground-schema.js`.

A link used to be labelled by its domain alone, so two links on one site read
identically: Mower Tract's Forest Service recreation page and its trail-map PDF
were both "fs.usda.gov". Needs `quickjs` (see tests/test_schema_chips.py).

Run from the project root:

    python -m unittest tests.test_link_labels -v
"""

import json
import os
import unittest

try:
    import quickjs
except ImportError:                                  # pragma: no cover
    quickjs = None

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@unittest.skipIf(quickjs is None, "quickjs not installed (pip install quickjs)")
class LinkLabels(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ctx = quickjs.Context()
        with open(os.path.join(REPO, "static", "campground-schema.js"),
                  encoding="utf-8") as fh:
            cls.ctx.eval(fh.read())
        cls.ctx.eval("function run(j) { return JSON.stringify(sfLinkLabels(JSON.parse(j))); }")

    def labels(self, urls):
        return json.loads(self.ctx.get("run")(json.dumps(urls)))

    def test_mower_tract_links_say_what_they_are(self):
        self.assertEqual(self.labels([
            "https://www.fs.usda.gov/r09/monongahela/recreation",
            "https://www.fs.usda.gov/sites/nfs/files/publication/MowerBasinTrailMap_0.pdf",
        ]), ["fs.usda.gov · Recreation",
             "fs.usda.gov · Mower Basin Trail Map (PDF)"])

    def test_distinct_domains_keep_the_bare_domain(self):
        self.assertEqual(self.labels([
            "https://gastateparks.org/CrookedRiver",
            "https://koa.com/campgrounds/mercer/",
        ]), ["gastateparks.org", "koa.com"])

    def test_booking_page_and_home_page(self):
        self.assertEqual(self.labels([
            "https://gastateparks.reserveamerica.com/campgroundDetails.do?contractCode=GA&parkId=530149",
            "https://gastateparks.reserveamerica.com",
        ]), ["gastateparks.reserveamerica.com · reservations",
             "gastateparks.reserveamerica.com · home page"])

    def test_a_lone_pdf_says_so(self):
        self.assertEqual(self.labels(["https://wvdnr.gov/maps/NathanielMtnWMA_11x17.pdf"]),
                         ["wvdnr.gov (PDF)"])

    def test_acronyms_and_slugs(self):
        self.assertEqual(self.labels([
            "https://wvdnr.gov/lands-waters/",
            "https://wvdnr.gov/wp-content/uploads/2022/11/NathanielMtnWMA_11x17.pdf",
        ])[1], "wvdnr.gov · Nathaniel Mtn WMA (PDF)")

    def test_unparseable_link_is_website(self):
        self.assertEqual(self.labels(["not a url"]), ["website"])

    def test_repeats_are_numbered_in_order(self):
        base = ("https://www.reserveamerica.com/explore/moshannon-state-forest/"
                "PA/880255/%d/campsite-booking")
        self.assertEqual(self.labels([base % 23816, base % 23817]),
                         ["reserveamerica.com \u00b7 reservations 1",
                          "reserveamerica.com \u00b7 reservations 2"])

    def test_index_page_and_civicplus_document(self):
        self.assertEqual(self.labels([
            "https://www.sepaq.com/pq/bou/index.dot?language_id=1",
            "https://www.sepaq.com/en/reservation/camping/x/molson-espace-vr",
        ]), ["sepaq.com \u00b7 home page", "sepaq.com \u00b7 reservations"])
        self.assertEqual(self.labels([
            "https://www.bayfieldcounty.wi.gov/238/Twin-Bear-Campground",
            "https://www.bayfieldcounty.wi.gov/DocumentCenter/View/10512/Twin-Bear-Campground-2019",
        ]), ["bayfieldcounty.wi.gov \u00b7 Twin Bear Campground",
             "bayfieldcounty.wi.gov \u00b7 Twin Bear Campground (document)"])

    def test_no_entry_in_the_file_shows_two_identical_links(self):
        with open(os.path.join(REPO, "campgrounds.json"), encoding="utf-8") as fh:
            entries = json.load(fh)
        clashes = []
        for e in entries:
            urls = [u.strip() for u in (e.get("website") or "").split("\n") if u.strip()]
            if len(urls) > 1:
                labels = self.labels(urls)
                if len(set(labels)) < len(labels):
                    clashes.append((e["id"], labels))
        self.assertEqual(clashes, [])

if __name__ == "__main__":
    unittest.main()
