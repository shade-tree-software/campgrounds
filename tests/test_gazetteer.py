"""The committed place gazetteer, and the rule that reads it.

`places.tsv.gz` is tracked rather than downloaded because every host needs it
and no host can be handed a generated file: trip_data/ is gitignored, sync runs
PA -> local only, PA has an outbound whitelist, and the USB build has no
network. So the property worth pinning hardest is that this module makes no
network calls at all — see test_no_network_is_needed.

    python -m unittest tests.test_gazetteer -v
"""

import gzip
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nearest_town as N  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _fresh(rows):
    """A module-level reload against a throwaway extract."""
    fd, path = tempfile.mkstemp(suffix=".tsv.gz")
    os.close(fd)
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    N._places = N._grid = None
    N.load(path)
    return path


class TestTheExtractShips(unittest.TestCase):
    def test_it_is_in_the_repo(self):
        self.assertTrue(os.path.exists(N.GAZETTEER_FILE),
                        "places.tsv.gz is missing — run build_gazetteer.py --apply")

    def test_no_network_is_needed(self):
        # The whole reason the extract is committed. urllib must not even be
        # imported by this module, so a host behind a whitelist (PA) or with no
        # network at all (the USB build) resolves places normally.
        with open(os.path.join(REPO, "nearest_town.py")) as fh:
            src = fh.read()
        for forbidden in ("urllib", "requests", "socket", "http"):
            self.assertNotIn(forbidden, src,
                             f"nearest_town.py refers to {forbidden}")

    def test_a_missing_extract_is_not_an_error(self):
        # trips.where_label falls back to the stored locale for every
        # coordinate, so a tree without the file renders as it did before.
        N._places = N._grid = None
        try:
            self.assertEqual(N.load("/nonexistent/places.tsv.gz"), 0)
            self.assertEqual(N.describe(38.79, -80.57), "")
        finally:
            N._places = N._grid = None


class TestTheRule(unittest.TestCase):
    def tearDown(self):
        N._places = N._grid = None

    def test_a_town_you_are_in_is_named_plainly(self):
        _fresh([(40.076, -102.223, "Wray", "CO", 2378)])
        self.assertEqual(N.describe(40.076, -102.223), "Wray, CO")

    def test_a_town_you_are_near_gets_distance_and_bearing(self):
        # The bearing runs FROM the town TO the point: the lake is north of
        # Shelbina, and the town is the anchor a reader orients by.
        _fresh([(39.694, -92.045, "Shelbina", "MO", 1639)])
        self.assertEqual(N.describe(39.717, -92.043), "2 miles north of Shelbina, MO")

    def test_a_real_town_beats_a_closer_crossroads(self):
        # The suburban regime. "Lindberg Heights" is 0.2 mi from the Wawa in
        # Limerick Township and Limerick is 0.5 — barely further, and the only
        # one anybody has heard of.
        _fresh([(40.2265, -75.5320, "Lindberg Heights", "PA", 0),
                (40.2340, -75.5285, "Limerick", "PA", 18074)])
        self.assertEqual(N.describe(40.2265, -75.5285), "Limerick, PA")

    def test_a_crossroads_wins_when_it_is_overwhelmingly_closer(self):
        # The rural regime, and the case that named this rule: Napier is 0.7 mi
        # from Bulltown Campground, Burnsville 5.8 — eight times further.
        _fresh([(38.7900, -80.5880, "Napier", "WV", 0),
                (38.8560, -80.6560, "Burnsville", "WV", 498)])
        self.assertEqual(N.describe(38.796898, -80.577679),
                         "just outside Napier, WV")

    def test_nothing_close_enough_is_named_at_all(self):
        # Silence is a real answer. Forest Canyon Overlook sits high on Trail
        # Ridge Road, and naming a town eleven miles away would be worse than
        # saying nothing.
        _fresh([(40.3772, -105.5217, "Estes Park", "CO", 6257)])
        self.assertEqual(N.describe(40.383, -105.727), "")

    def test_a_big_city_reaches_further_than_a_village(self):
        # Population buys distance: a city of 60,000 is worth naming at 20
        # miles, a village of 300 is not.
        _fresh([(40.0, -75.0, "Bigtown", "PA", 60000)])
        self.assertNotEqual(N.describe(40.28, -75.0), "")
        N._places = N._grid = None
        _fresh([(40.0, -75.0, "Smallville", "PA", 300)])
        self.assertEqual(N.describe(40.28, -75.0), "")




class TestTheLastResortRadius(unittest.TestCase):
    """A road card has no name of its own; a stop does.

    The tiered radii exist because naming Grand Lake ten miles from Forest
    Canyon Overlook was worse than silence — the overlook already names itself.
    But a stretch of US-36 does not, and out on the eastern Colorado plains the
    nearest place with any recorded population is sixteen miles away. Saying so
    is more use than a blank: the distance is the information.

    So the coordinate carries both answers and the CALLER chooses, since the
    coordinate cannot know which kind of thing is being placed.
    """

    def tearDown(self):
        N._places = N._grid = None

    def test_nothing_qualifies_under_the_strict_rule(self):
        _fresh([(39.90, -104.05, "Deer Trail", "CO", 612)])   # ~16 mi away
        self.assertEqual(N.describe(39.74, -103.787), "")

    def test_the_wider_radius_names_it_with_the_distance(self):
        _fresh([(39.90, -104.05, "Deer Trail", "CO", 612)])
        got = N.describe(39.74, -103.787, N.FAR_MILES)
        self.assertIn("Deer Trail", got)
        self.assertRegex(got, r"^\d+ miles \w+ of ")

    def test_it_never_reaches_for_an_unpopulated_crossroads(self):
        # At sixteen miles a name nobody could place is worse than a blank.
        _fresh([(39.90, -104.05, "Shamrock", "CO", 0)])
        self.assertEqual(N.describe(39.74, -103.787, N.FAR_MILES), "")

    def test_beyond_the_wider_radius_is_still_silence(self):
        _fresh([(41.00, -104.05, "Faraway", "CO", 5000)])     # ~87 mi
        self.assertEqual(N.describe(39.74, -103.787, N.FAR_MILES), "")

    def test_a_place_that_already_qualifies_is_unaffected(self):
        # Two miles out, comfortably inside a pop-150 place's five-mile tier,
        # so the wider radius has nothing left to add.
        _fresh([(39.8279, -100.2450, "Norcatur", "KS", 150)])
        strict = N.describe(39.8279, -100.2802)
        self.assertIn("Norcatur", strict)
        self.assertEqual(strict, N.describe(39.8279, -100.2802, N.FAR_MILES))


if __name__ == "__main__":
    unittest.main()
