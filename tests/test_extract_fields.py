"""The rules that keep the note-extraction pass from doing damage.

`extract_fields.py` reads 12,689 hand-written notes through a model and writes
what they say into structured fields. Three of its rules are the difference
between a useful index and a quietly corrupted database, and none of them are
visible in the output when they break:

1. **A human's reading is never overwritten.** Doc §3 ranks verified above
   derived. A pass that ignored that would erase the exact entries somebody
   cared enough to check by hand, and leave them looking machine-confident.

2. **Absent is unknown, in both directions** (doc §2.1). The model omitting a
   key must not become a stored `false`, and a `null` coming back from the model
   must not reach `apply_update`, which reads null as "clear this field" — on an
   entry a person had filled, that is a silent deletion.

3. **"We looked and found nothing" is recorded.** Without it the ~30% of notes
   that hold no structured fact are re-sent to the model on every run, forever.
   `note_scan` is that record, and it is keyed to the note's text so that
   editing a note re-queues exactly that entry and nothing else.

The model call itself is not tested here — it costs money and it is judgement,
not logic. What is tested is everything around it, which is where a silent
regression would live.

Run from the project root:

    python -m unittest tests.test_extract_fields -v
"""

import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import campground_schema as cs  # noqa: E402
import extract_fields as ef  # noqa: E402


class TestNeedsScan(unittest.TestCase):
    """What makes an entry queued, done, or out of scope."""

    def test_an_unscanned_note_is_queued(self):
        self.assertTrue(ef.needs_scan({"note": "23 sites, vault toilets."}))

    def test_an_entry_with_no_note_is_never_queued(self):
        self.assertFalse(ef.needs_scan({}))
        self.assertFalse(ef.needs_scan({"note": "   "}))

    def test_a_scanned_note_is_done(self):
        note = "23 sites, vault toilets."
        entry = {"note": note,
                 cs.NOTE_SCAN: {"sig": ef.note_sig(note), "checked": "2026-09-15"}}
        self.assertFalse(ef.needs_scan(entry))

    def test_editing_the_note_requeues_that_entry(self):
        """The signature is the whole incremental story."""
        entry = {"note": "23 sites.",
                 cs.NOTE_SCAN: {"sig": ef.note_sig("23 sites."),
                                "checked": "2026-09-15"}}
        self.assertFalse(ef.needs_scan(entry))
        entry["note"] = "23 sites, showers."
        self.assertTrue(ef.needs_scan(entry))

    def test_a_fully_human_verified_entry_is_skipped(self):
        """Nothing to gain, and the model's answer could only lose to theirs."""
        entry = {"note": "anything at all",
                 cs.PROVENANCE: {g: {"method": "manual"} for g in ef.TARGET_GROUPS}}
        self.assertFalse(ef.needs_scan(entry))

    def test_a_partly_verified_entry_is_still_queued(self):
        entry = {"note": "anything at all",
                 cs.PROVENANCE: {"fees": {"method": "manual"},
                                 "hookups": {"method": "manual"}}}
        self.assertTrue(ef.needs_scan(entry))


class TestCleanProposal(unittest.TestCase):
    """Nothing the vocabulary refuses is allowed through."""

    def test_a_valid_proposal_survives_intact(self):
        kept, rejected = ef.clean_proposal(
            {"id": 7, "hookups": {"electric": 50, "water": True},
             "sites": {"count": 23}})
        self.assertEqual(kept, {"hookups": {"electric": 50, "water": True},
                                "sites": {"count": 23}})
        self.assertEqual(rejected, [])

    def test_an_out_of_vocabulary_value_is_dropped_not_fatal(self):
        """One bad field must not cost the other eleven entries in the batch."""
        kept, rejected = ef.clean_proposal(
            {"id": 7, "hookups": {"electric": 37, "water": True}})
        self.assertEqual(kept, {"hookups": {"water": True}})
        self.assertEqual(len(rejected), 1)
        self.assertIn("electric", rejected[0])

    def test_an_unknown_key_is_dropped(self):
        kept, rejected = ef.clean_proposal(
            {"id": 7, "facilities": {"showers": True, "swimming_pool": True}})
        self.assertEqual(kept, {"facilities": {"showers": True}})
        self.assertEqual(len(rejected), 1)

    def test_a_group_outside_the_pass_is_refused(self):
        """`fees` and `rating` are other passes' business (doc §7)."""
        kept, rejected = ef.clean_proposal(
            {"id": 7, "fees": {"nightly_low": 20}, "rating": {"stars": 5}})
        self.assertEqual(kept, {})
        self.assertEqual(len(rejected), 2)

    def test_null_is_unknown_and_never_a_clear(self):
        """A null reaching apply_update would DELETE the field, not skip it."""
        kept, _ = ef.clean_proposal(
            {"id": 7, "hookups": {"electric": None, "sewer": "", "water": True}})
        self.assertEqual(kept, {"hookups": {"water": True}})

    def test_false_and_zero_are_real_claims_and_survive(self):
        """"no hookups" is a measurement; only silence is unknown."""
        kept, _ = ef.clean_proposal(
            {"id": 7, "hookups": {"electric": 0, "water": False, "sewer": False}})
        self.assertEqual(kept,
                         {"hookups": {"electric": 0, "water": False, "sewer": False}})

    def test_an_empty_group_yields_nothing(self):
        self.assertEqual(ef.clean_proposal({"id": 7, "hookups": {}})[0], {})


class TestWriteDeltas(unittest.TestCase):
    """The write path, against a real file."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8")
        self.rows = [
            {"id": 1, "kind": "campground", "name": "A", "note": "23 sites."},
            {"id": 2, "kind": "campground", "name": "B", "note": "Nothing useful.",
             "hookups": {"electric": 30},
             cs.PROVENANCE: {"hookups": {"method": "manual",
                                         "source": "the operator, by phone"}}},
        ]
        # Trailing newline included: the real campgrounds.json has one, and
        # write_deltas writes one, so a fixture without it would make every
        # write look like it changed the last line.
        json.dump(self.rows, self.tmp, indent=2, ensure_ascii=False)
        self.tmp.write("\n")
        self.tmp.close()
        self._real = ef.CAMPGROUNDS_JSON
        ef.CAMPGROUNDS_JSON = self.tmp.name

    def tearDown(self):
        ef.CAMPGROUNDS_JSON = self._real
        os.unlink(self.tmp.name)

    def written(self):
        with open(self.tmp.name, encoding="utf-8") as fh:
            return {r["id"]: r for r in json.load(fh)}

    def test_values_and_provenance_are_both_written(self):
        ef.write_deltas({1: ({"sites": {"count": 23}}, "sig1")},
                        "claude-opus-5", "2026-09-15")
        row = self.written()[1]
        self.assertEqual(row["sites"], {"count": 23})
        self.assertEqual(row[cs.PROVENANCE]["sites"],
                         {"source": "note prose", "checked": "2026-09-15",
                          "method": "derived"})

    def test_an_empty_result_still_records_the_scan(self):
        """Otherwise this note is re-sent to the model on every future run."""
        ef.write_deltas({1: ({}, "sig1")}, "claude-opus-5", "2026-09-15")
        row = self.written()[1]
        self.assertEqual(row[cs.NOTE_SCAN]["sig"], "sig1")
        self.assertNotIn(cs.PROVENANCE, row, "nothing was derived, so no provenance")
        for group in ef.TARGET_GROUPS:
            self.assertNotIn(group, row, "an empty result must write no values")

    def test_a_human_verified_group_is_not_overwritten(self):
        ef.write_deltas({2: ({"hookups": {"electric": 50, "water": True}}, "sig2")},
                        "claude-opus-5", "2026-09-15")
        row = self.written()[2]
        self.assertEqual(row["hookups"], {"electric": 30}, "the human's value stands")
        self.assertEqual(row[cs.PROVENANCE]["hookups"]["method"], "manual")

    def test_the_scan_is_still_recorded_on_a_protected_entry(self):
        """Or it is re-read every run to be refused every run."""
        ef.write_deltas({2: ({"hookups": {"electric": 50}}, "sig2")},
                        "claude-opus-5", "2026-09-15")
        self.assertEqual(self.written()[2][cs.NOTE_SCAN]["sig"], "sig2")

    def test_untouched_entries_are_left_byte_for_byte_alone(self):
        before = open(self.tmp.name, encoding="utf-8").read()
        ef.write_deltas({}, "claude-opus-5", "2026-09-15")
        self.assertEqual(open(self.tmp.name, encoding="utf-8").read(), before)

    def test_a_scanned_entry_is_not_queued_again(self):
        """End to end: write, then re-select."""
        ef.write_deltas({1: ({}, ef.note_sig("23 sites."))},
                        "claude-opus-5", "2026-09-15")
        rows = list(self.written().values())
        self.assertEqual([r["id"] for r in ef.candidates(rows)], [2])


class TestParseReply(unittest.TestCase):
    """The model's envelope, which is not always bare JSON."""

    def test_a_bare_array(self):
        self.assertEqual(ef.parse_reply('[{"id": 1}]'), [{"id": 1}])

    def test_a_fenced_array(self):
        self.assertEqual(ef.parse_reply('```json\n[{"id": 1}]\n```'), [{"id": 1}])

    def test_prose_around_the_array(self):
        self.assertEqual(
            ef.parse_reply('Here you go:\n[{"id": 1}]\nHope that helps.'),
            [{"id": 1}])

    def test_no_array_raises_rather_than_returning_empty(self):
        """An empty list would be recorded as "scanned, found nothing"."""
        with self.assertRaises(ValueError):
            ef.parse_reply("I could not do that.")


class TestTargetGroups(unittest.TestCase):

    def test_every_target_group_is_real(self):
        for group in ef.TARGET_GROUPS:
            self.assertIn(group, cs.SCHEMA)

    def test_fees_and_rating_are_out_of_scope(self):
        """doc §7: fees are 0.1-1.2% of notes; rating was phase 2, mechanical."""
        self.assertNotIn("fees", ef.TARGET_GROUPS)
        self.assertNotIn("rating", ef.TARGET_GROUPS)


if __name__ == "__main__":
    unittest.main()
