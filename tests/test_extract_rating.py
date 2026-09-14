"""Reading the RV Life rating out of note prose, without mangling the prose.

`extract_rating.py` is a one-shot migration, but its parsing rules are subtle
and every one of them corrects something found in the real data across 595
distinct shapes of the clause. These pin the traps so a re-run (or a second
extractor written later against the same notes) cannot quietly reintroduce one.

The governing asymmetry: reading is tolerant, REMOVING is strict. A duplicated
fact is untidy; a mangled note is unrecoverable, and the note is the source of
truth for everything the schema cannot hold.

    python -m unittest tests.test_extract_rating -v
"""

import unittest

import extract_rating as ex


class TestParsing(unittest.TestCase):

    def parse(self, note):
        rating, _ = ex.parse_rating(note)
        return rating

    def test_the_canonical_tail(self):
        self.assertEqual(
            self.parse("Nice spot. RV Life 4.5*/$$ (auto 6/2026). --Claude"),
            {"stars": 4.5, "price_tier": 2, "checked": "2026-06",
             "source": "rvlife"})

    def test_the_variant_notations(self):
        for note, stars in [
                ("RV Life 4★, price $$$ (3/4). --Claude", 4.0),
                ("RV Life 5 stars, $$. --Claude", 5.0),
                ("RV Life 5-star, $. --Claude", 5.0),      # hyphenated
                ("RV Life 4/5, $. --Claude", 4.0),         # out-of-five
                ("RV Life: 3.5* / $$ --Claude", 3.5),
        ]:
            with self.subTest(note=note):
                self.assertEqual(self.parse(note)["stars"], stars)

    def test_a_dollar_sign_before_a_digit_is_money_not_a_tier(self):
        # "CAD ~$40/night" and "$50/night" are amounts. An earlier version read
        # them as price tiers.
        got = self.parse("RV Life 4*/$$ CAD ~$40/night (auto 6/2026). --Claude")
        self.assertEqual(got["price_tier"], 2)

    def test_a_tier_at_the_end_of_a_sentence_still_parses(self):
        # The regression this pinned: excluding a following "." as well as a
        # digit rejected "RV Life 4*/$. --Claude" and silently lost the tier on
        # ~700 entries while the stars parsed fine.
        self.assertEqual(self.parse("RV Life 4*/$. --Claude")["price_tier"], 1)

    def test_the_last_mention_wins_when_a_note_mentions_it_twice(self):
        # Ouabache Trails Park: prose about a mis-tag, THEN the real tail.
        note = ("35 RV sites. (RV Life mis-tagged commercial; it is county-run.) "
                "RV Life 4*/$$. --Claude")
        self.assertEqual(self.parse(note), {"stars": 4.0, "price_tier": 2,
                                            "source": "rvlife"})

    def test_zero_stars_means_unrated_and_is_not_stored(self):
        # RV Life publishes 0 for "no rating yet". Storing 0.0 would claim the
        # campground was rated and rated worst.
        got = self.parse("RV Life 0*/$. --Claude")
        self.assertNotIn("stars", got)
        self.assertEqual(got["price_tier"], 1)

    def test_listed_but_unrated_yields_no_stars(self):
        self.assertIsNone(self.parse("RV Life unrated. --Claude"))

    def test_prose_about_rv_life_yields_nothing(self):
        for note in ("RV Life mislabels commercial; it is county FP. --Claude",
                     "not on RV Life. --Claude",
                     "Coordinate approximate (RV Life geoloc). --Claude"):
            with self.subTest(note=note):
                self.assertIsNone(self.parse(note))

    def test_the_ten_scale_is_recognised_so_it_can_be_skipped(self):
        # AWH's older notation, a different scale by a different author.
        for note in ("RVLife 9.5/10", "RV Life ~9.9/10. --Claude"):
            with self.subTest(note=note):
                self.assertTrue(ex.TEN_SCALE.search(note))


class TestExcision(unittest.TestCase):
    """Only a complete clause at the END of a note may be cut."""

    def cut(self, note):
        rating, match = ex.parse_rating(note)
        self.assertIsNotNone(rating, note)
        return ex.excise(note, match)

    def test_a_clean_tail_is_removed(self):
        new, cut = self.cut("On a bluff. RV Life 4*/$$ (auto 6/2026). --Claude")
        self.assertTrue(cut)
        self.assertEqual(new, "On a bluff. --Claude")

    def test_text_after_the_clause_blocks_removal(self):
        note = ("Near the river. RV Life 3.5*/$$ (auto 6/2026). "
                "First-come, first-served. --Claude")
        new, cut = self.cut(note)
        self.assertFalse(cut)
        self.assertEqual(new, note)

    def test_a_bracketed_clause_takes_its_bracket_with_it(self):
        new, cut = self.cut("$65/night. --AWH  [RV Life: 4★, price $$$ (3/4). --Claude]")
        self.assertTrue(cut)
        self.assertEqual(new, "$65/night. --AWH")

    def test_attribution_leaves_with_the_clause_it_belonged_to(self):
        # Prose already signed --AWH: the clause's --Claude was the clause's
        # alone. Keeping it leaves "--AWH --Claude", two authors with nothing
        # between them.
        new, _ = self.cut("Lakefront sites.  --AWH  RV Life 4.5*/$$ (auto 6/2026). --Claude")
        self.assertEqual(new, "Lakefront sites.  --AWH")

    def test_attribution_is_kept_when_the_remaining_prose_is_unsigned(self):
        new, _ = self.cut("44 sites, full hookups. RV Life 4*/$$ (auto 6/2026). --Claude")
        self.assertEqual(new, "44 sites, full hookups. --Claude")

    def test_a_note_that_was_only_the_clause_becomes_empty(self):
        new, cut = self.cut("RV Life 4.5*/$$ (auto 6/2026). --Claude")
        self.assertTrue(cut)
        self.assertEqual(new, "")

    def test_removal_never_takes_a_non_rating_word(self):
        import re
        allowed = {'rv', 'life', 'unrated', 'star', 'stars', 'auto', 'cad',
                   'night', 'reviews', 'review', 'price', 'claude', 'listed',
                   'but', 'awh'}
        notes = [
            "Riverside loop, 30A. RV Life 4*/$$ (auto 6/2026). --Claude",
            "Quiet. --AWH  [RV Life: 4★, price $$$ (3/4). --Claude]",
            "Big rigs OK. RV Life 4.5*/$$ CAD ~$40/night (auto 6/2026). --Claude",
            "Wooded. RV Life 4★/$$, 27 reviews. --Claude",
        ]
        for note in notes:
            with self.subTest(note=note):
                rating, match = ex.parse_rating(note)
                new, cut = ex.excise(note, match)
                self.assertTrue(cut)
                # The removed span is everything from the clause onward. It is
                # NOT `note[len(new):]` — excise may re-append an attribution,
                # so the surviving text is not always a prefix of the original.
                removed = note[match.start():]
                for word in re.findall(r"[A-Za-z]+", removed):
                    self.assertIn(word.lower(), allowed,
                                  f"{word!r} would be lost from {note!r}")


class TestWrittenShapeIsValid(unittest.TestCase):
    def test_every_parsed_rating_satisfies_the_schema(self):
        import campground_schema as cs
        for note in ("RV Life 4.5*/$$ (auto 6/2026). --Claude",
                     "RV Life 5-star, free/$. --Claude",
                     "RV Life 4/5, $. --Claude",
                     "RV Life 0*/$. --Claude"):
            rating, _ = ex.parse_rating(note)
            if rating is None:
                continue
            with self.subTest(note=note):
                staged = {}
                cs.apply_update(staged, {"rating": rating})
                self.assertEqual(staged["rating"], rating)


if __name__ == "__main__":
    unittest.main()
