"""The campground map's rating and hookup filters, and the one rule they obey.

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
    """The structured-filter predicates, exactly as the template ships them.

    From the shared unknown switch through `schemaFaded`, which spans the
    hookup levels, the rating pair, the hookup pair and the combined answer
    every caller uses.
    """
    with open(TEMPLATE, encoding="utf-8") as fh:
        tpl = fh.read()
    start = tpl.index("let includeUnknown")
    tail = tpl.index("function schemaFaded(cg)")
    end = tpl.index("\n", tpl.index("}", tail))
    src = tpl[start:end]
    for name in ("ratingFilterActive", "ratingUnknown", "ratingPasses",
                 "hookupUnknown", "hookupPasses",
                 "schemaVisible", "schemaFaded"):
        assert f"function {name}(" in src, f"{name} missing — template moved?"
    return src


def _markers():
    """Every campground exactly as `_map_marker_rows` puts it on the page.

    Built by the app's own projection rather than a copy of it, so a change to
    what rides inline (doc §8.4) is tested as shipped. Absent stays absent (doc
    §2.1): an unrated entry carries no `stars`, an unrecorded hookup no key.
    """
    import sys
    sys.path.insert(0, ROOT)
    import ekko_trips_app as A
    with open(CAMPGROUNDS, encoding="utf-8") as fh:
        rows = [r for r in json.load(fh)
                if r.get("kind", "campground") == "campground"]
    keep = ("stars", "price_tier", "electric", "water", "sewer")
    return [{k: m[k] for k in keep if k in m} for m in A._map_marker_rows(rows)]


@unittest.skipIf(quickjs is None, "quickjs not installed (pip install quickjs)")
class TestRatingFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.markers = _markers()
        cls.pairs = [(m.get("stars"), m.get("price_tier")) for m in cls.markers]
        cls.ctx = quickjs.Context()
        # The lifted block reads its saved state through STORE; a stub that
        # always answers the fallback starts every test from the page default.
        cls.ctx.eval("var STORE = {get: function (k, f) { return f; }};"
                     "var ratingMin = 0, priceMax = 0;")
        cls.ctx.eval(_predicate_source())
        cls.ctx.eval("""
            function setFilter(mn, mx, unknown, hk) {
              ratingMin = mn; priceMax = mx; includeUnknown = unknown;
              hookupMin = hk;
            }
            function classify(rows) {
              var shown = 0, faded = 0, hidden = 0;
              for (var i = 0; i < rows.length; i++) {
                if (schemaVisible(rows[i])) {
                  shown++;
                  if (schemaFaded(rows[i])) faded++;
                } else hidden++;
              }
              return JSON.stringify({shown: shown, faded: faded, hidden: hidden});
            }
        """)
        cls.ctx.eval("var ROWS = " + json.dumps(cls.markers) + ";")

    def run_filter(self, stars=0, price=0, unrated=True, hookups=""):
        self.ctx.get("setFilter")(stars, price, unrated, hookups)
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


class TestHookupFilter(TestRatingFilter):
    """The same §2.2 rule, applied to the hookups phase 3 read out of the notes.

    Inherits the harness (and so re-runs the rating cases, cheaply) because the
    two filters share one predicate block and one unknown switch — a hookup
    change that broke the rating half should fail here too.
    """

    NEEDS = {"electric": ("electric",), "ew": ("electric", "water"),
             "full": ("electric", "water", "sewer")}

    def expected(self, level):
        need = self.NEEDS[level]
        fail = unknown = 0
        for m in self.markers:
            if any(m.get(k) is False for k in need):
                fail += 1
            elif any(k not in m for k in need):
                unknown += 1
        return fail, unknown

    def test_each_level_hides_measured_failures_and_fades_unknowns(self):
        for level in self.NEEDS:
            with self.subTest(level=level):
                fail, unknown = self.expected(level)
                self.assertGreater(unknown, 0, "fixture no longer exercises §2.2")
                c = self.run_filter(hookups=level)
                self.assertEqual(c["hidden"], fail)
                self.assertEqual(c["faded"], unknown)

    def test_what_a_naive_hookup_filter_would_have_cost(self):
        """Full hookups is where silence is loudest: sewer is the least known."""
        kept = self.run_filter(hookups="full")["shown"]
        naive = self.run_filter(hookups="full", unrated=False)["shown"]
        self.assertGreater(kept - naive, 0.15 * len(self.markers))

    def test_no_power_fails_every_level_whatever_else_is_unknown(self):
        self.ctx.eval("hookupMin = 'full'; includeUnknown = true;")
        visible = self.ctx.get("schemaVisible")
        row = self.ctx.eval("({electric: false})")
        self.assertFalse(visible(row))
        row = self.ctx.eval("({electric: true})")
        self.assertTrue(visible(row), "water/sewer unknown is not a failure")
        self.assertTrue(self.ctx.get("schemaFaded")(row))

    def test_a_rating_unknown_does_not_rescue_a_hookup_failure(self):
        """Unknown on one filter must not launder a measured failure on another."""
        c = self.run_filter(stars=4, hookups="electric")
        self.assertEqual(
            c["hidden"],
            sum(1 for m in self.markers
                if m.get("electric") is False
                or (m.get("stars") is not None and m["stars"] < 4)))

    def test_unknown_is_scoped_to_the_active_filters(self):
        """With only a hookup level set, an unrated campground is not unknown."""
        c = self.run_filter(hookups="electric")
        self.assertEqual(c["faded"], sum(1 for m in self.markers
                                         if "electric" not in m))


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

    def test_hookups_ride_inline_as_three_booleans(self):
        import sys
        sys.path.insert(0, ROOT)
        import ekko_trips_app as A
        out = A._map_marker_rows([{"id": 1, "name": "X", "location": "1,2",
                                   "hookups": {"electric": 30, "water": True,
                                               "dump": True}}])[0]
        self.assertIs(out["electric"], True)
        self.assertIs(out["water"], True)
        self.assertNotIn("sewer", out, "unrecorded stays absent (doc §2.1)")
        self.assertNotIn("dump", out, "only what the filter reads rides inline")
        out = A._map_marker_rows([{"id": 1, "name": "X", "location": "1,2",
                                   "hookups": {"electric": 0, "sewer": False}}])[0]
        self.assertIs(out["electric"], False, "0 amps is a measured no")
        self.assertIs(out["sewer"], False)


if __name__ == "__main__":
    unittest.main()
