"""The campground map's rating filter, and the one rule it exists to obey.

Doc §2.2 inverts the waterfront rule on purpose: an unknown value may never be
what removes an entry from a search. A wrong `waterfront` is visible on arrival;
a campground missing from a result list is invisible forever, and the searcher
concludes it does not exist.

That rule is cheap to state and easy to lose, because the natural way to write
`stars >= 4` drops every entry without a rating and looks like it works. On this
database that is **3,006 campgrounds, 24% of the file** — concentrated in the
public land RV Life never rated, which is most of what the map is for. So the
filter shows them, faded, and hiding them is an explicit click.

The predicates are lifted VERBATIM out of `templates/campground_map.html` and
run in a real JS engine against the real `campgrounds.json`. A Python
reimplementation would be a paraphrase, and a paraphrase of the rule under test
can agree with the doc while the shipped code disagrees. Needs `quickjs`
(`pip install quickjs`) — the dev box has no node; see the repo's
"testing JS with no node" note. Skipped, loudly, when it is absent.

Run from the project root:

    python -m unittest tests.test_rating_filter -v
"""

import json
import os
import unittest

try:
    import quickjs
except ImportError:                                  # pragma: no cover
    quickjs = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "templates", "campground_map.html")
CAMPGROUNDS = os.path.join(ROOT, "campgrounds.json")


def _predicate_source():
    """The four rating predicates, exactly as the template ships them."""
    with open(TEMPLATE, encoding="utf-8") as fh:
        tpl = fh.read()
    start = tpl.index("function ratingFilterActive()")
    tail = tpl.index("function ratingFaded(cg)")
    end = tpl.index("\n", tpl.index("}", tail))
    src = tpl[start:end]
    for name in ("ratingFilterActive", "ratingUnknown", "ratingPasses",
                 "ratingVisible", "ratingFaded"):
        assert f"function {name}(" in src, f"{name} missing — template moved?"
    return src


def _markers():
    """The two rating fields exactly as `_map_marker_rows` puts them on a marker.

    Absent stays absent (doc §2.1): an unrated entry carries no key, which is
    the whole distinction the filter turns on.
    """
    with open(CAMPGROUNDS, encoding="utf-8") as fh:
        rows = [r for r in json.load(fh)
                if r.get("kind", "campground") == "campground"]
    out = []
    for r in rows:
        d = {}
        rating = r.get("rating") or {}
        for k in ("stars", "price_tier"):
            if rating.get(k) is not None:
                d[k] = rating[k]
        out.append(d)
    return out


@unittest.skipIf(quickjs is None, "quickjs not installed (pip install quickjs)")
class TestRatingFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.markers = _markers()
        cls.pairs = [(m.get("stars"), m.get("price_tier")) for m in cls.markers]
        cls.ctx = quickjs.Context()
        cls.ctx.eval("var ratingMin = 0, priceMax = 0, includeUnrated = true;")
        cls.ctx.eval(_predicate_source())
        cls.ctx.eval("""
            function setFilter(mn, mx, unrated) {
              ratingMin = mn; priceMax = mx; includeUnrated = unrated;
            }
            function classify(rows) {
              var shown = 0, faded = 0, hidden = 0;
              for (var i = 0; i < rows.length; i++) {
                if (ratingVisible(rows[i])) {
                  shown++;
                  if (ratingFaded(rows[i])) faded++;
                } else hidden++;
              }
              return JSON.stringify({shown: shown, faded: faded, hidden: hidden});
            }
        """)
        cls.ctx.eval("var ROWS = " + json.dumps(cls.markers) + ";")

    def run_filter(self, stars=0, price=0, unrated=True):
        self.ctx.get("setFilter")(stars, price, unrated)
        return json.loads(self.ctx.get("classify")(self.ctx.get("ROWS")))

    def test_no_threshold_shows_everything_unfaded(self):
        c = self.run_filter()
        self.assertEqual(c["shown"], len(self.markers))
        self.assertEqual(c["hidden"], 0)
        self.assertEqual(c["faded"], 0, "an unfiltered map must not flag anything")

    def test_unknown_never_excludes(self):
        """§2.2. Every star-less entry survives a star threshold, flagged."""
        c = self.run_filter(stars=4)
        starless = sum(1 for s, _ in self.pairs if s is None)
        self.assertGreater(starless, 0, "fixture no longer exercises the rule")
        self.assertEqual(c["faded"], starless)

    def test_what_the_naive_filter_would_have_cost(self):
        """The number that makes the rule worth the code."""
        kept = self.run_filter(stars=4, unrated=True)["shown"]
        naive = self.run_filter(stars=4, unrated=False)["shown"]
        self.assertGreater(kept - naive, 0.15 * len(self.markers))

    def test_a_measured_failure_is_still_hidden(self):
        """Shown-when-unknown must not decay into shown-always."""
        c = self.run_filter(stars=4)
        self.assertEqual(c["hidden"],
                         sum(1 for s, _ in self.pairs if s is not None and s < 4))

    def test_unknown_is_scoped_to_the_active_thresholds(self):
        """With only a price filter set, a star-less campground is not unrated."""
        c = self.run_filter(price=2)
        self.assertEqual(c["faded"],
                         sum(1 for _, p in self.pairs if p is None))

    def test_unknown_on_one_field_does_not_rescue_a_failure_on_the_other(self):
        """$$$$ with no stars, under "4+ and $$ or less", is excluded.

        It fails on a value somebody measured, so hiding it is not the §2.2
        failure — being unknown elsewhere must not launder that into a pass.
        """
        c = self.run_filter(stars=4, price=2)
        self.assertEqual(
            c["hidden"],
            sum(1 for s, p in self.pairs
                if (s is not None and s < 4) or (p is not None and p > 2)))

    def test_opting_out_hides_exactly_the_unknowns(self):
        """Clearing "Include unrated" is allowed — it just has to be precise."""
        on = self.run_filter(stars=4, price=2, unrated=True)
        off = self.run_filter(stars=4, price=2, unrated=False)
        self.assertEqual(on["shown"] - off["shown"], on["faded"])
        self.assertEqual(off["faded"], 0)

    def test_counts_always_partition(self):
        for stars, price, unrated in [(0, 0, True), (4, 0, True), (4, 0, False),
                                      (4.5, 2, True), (5, 1, False), (3, 4, True)]:
            with self.subTest(stars=stars, price=price, unrated=unrated):
                c = self.run_filter(stars, price, unrated)
                self.assertEqual(c["shown"] + c["hidden"], len(self.markers))
                self.assertLessEqual(c["faded"], c["shown"])


class TestMarkerPayload(unittest.TestCase):
    """The filter can only run on what rides inline (doc §8.4)."""

    def test_the_two_rating_fields_are_flattened_onto_the_marker(self):
        import sys
        sys.path.insert(0, ROOT)
        import ekko_trips_app as A
        row = {"id": 1, "name": "X", "location": "1,2",
               "rating": {"stars": 4.5, "price_tier": 2, "note": "keep me off"}}
        out = A._map_marker_rows([row])[0]
        self.assertEqual(out["stars"], 4.5)
        self.assertEqual(out["price_tier"], 2)
        self.assertNotIn("note", out, "only the filterable scalars may ride inline")
        self.assertNotIn("rating", out)

    def test_an_unrated_entry_carries_no_key_at_all(self):
        import sys
        sys.path.insert(0, ROOT)
        import ekko_trips_app as A
        out = A._map_marker_rows([{"id": 1, "name": "X", "location": "1,2"}])[0]
        self.assertNotIn("stars", out)
        self.assertNotIn("price_tier", out)
        out = A._map_marker_rows([{"id": 1, "name": "X", "location": "1,2",
                                   "rating": {"stars": None}}])[0]
        self.assertNotIn("stars", out, "null is not a rating (doc §2.1)")


if __name__ == "__main__":
    unittest.main()
