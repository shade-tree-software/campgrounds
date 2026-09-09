"""Transcribing memos must not lose a correction, and must not lose a race.

`process_memos.py` is an offline batch tool, but the web app triggers it on
upload, so it runs *concurrently with the app editing the same file*. Two rules
carry that weight:

  * **A hand-edited transcript survives --force.** The app sets
    `transcript_edited` when someone corrects the text, and only the explicit
    --force-edited overrides it. The transcript is what the rollup will be
    built from, so a correction is worth more than anything a re-run produces.
  * **Deltas are merged into the file on disk at write time**, never dumped
    from the dict loaded at startup. While a batch runs, the app may file a
    memo to a different trip or delete one outright; both must survive.

These import `process_memos` without faster_whisper installed — the model
import lives inside main() precisely so --help, --dry-run and this file work
on a machine that will never transcribe anything.

Run from the project root with the venv active:

    python -m unittest tests.test_transcribe_rules -v
"""

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import process_memos as P  # noqa: E402


class TestNeedsTranscript(unittest.TestCase):
    def test_untranscribed_memo_is_picked_up(self):
        self.assertTrue(P._needs_transcript({}, False, False))

    def test_transcribed_memo_is_skipped(self):
        rec = {"transcript": "we saw elk"}
        self.assertFalse(P._needs_transcript(rec, False, False))

    def test_blank_transcript_counts_as_untranscribed(self):
        # A memo of pure silence records "" — re-running should retry it rather
        # than treat the empty string as a finished answer.
        self.assertTrue(P._needs_transcript({"transcript": "   "}, False, False))

    def test_force_redoes_a_machine_transcript(self):
        rec = {"transcript": "we saw elk", "transcript_edited": False}
        self.assertTrue(P._needs_transcript(rec, True, False))

    def test_force_does_NOT_touch_a_hand_edited_transcript(self):
        # The whole point: --force is for "the model did badly, try again",
        # and a transcript a human already fixed is not that.
        rec = {"transcript": "We saw elk.", "transcript_edited": True}
        self.assertFalse(P._needs_transcript(rec, True, False))

    def test_force_edited_is_the_explicit_override(self):
        rec = {"transcript": "We saw elk.", "transcript_edited": True}
        self.assertTrue(P._needs_transcript(rec, False, True))


class TestMergeAndWrite(unittest.TestCase):
    """The app edits memos.json while a batch is running. Every case here is
    something it really does."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "memos.json")
        patch = mock.patch.object(P, "MEMOS_FILE", self.path)
        patch.start()
        self.addCleanup(patch.stop)

    def write(self, data):
        with open(self.path, "w") as f:
            json.dump(data, f)

    def read(self):
        with open(self.path) as f:
            return json.load(f)

    def test_transcript_lands_on_the_record(self):
        self.write({"m1": {"trip_id": 95, "filename": "a.wav"}})
        P._merge_and_write({"m1": {"transcript": "we saw elk"}})
        self.assertEqual(self.read()["m1"]["transcript"], "we saw elk")
        self.assertEqual(self.read()["m1"]["filename"], "a.wav")   # untouched

    def test_a_memo_refiled_mid_run_keeps_its_new_trip(self):
        # Started the batch when m1 was unfiled; the admin filed it by hand
        # while Whisper was working. The transcript must land WITHOUT reverting
        # the filing — which is why deltas are merged per-record against the
        # file on disk rather than dumped from the startup snapshot.
        self.write({"m1": {"trip_id": None}})
        self.write({"m1": {"trip_id": 42, "date": "2025-06-10"}})
        P._merge_and_write({"m1": {"transcript": "text"}})
        rec = self.read()["m1"]
        self.assertEqual(rec["trip_id"], 42)
        self.assertEqual(rec["date"], "2025-06-10")
        self.assertEqual(rec["transcript"], "text")

    def test_a_memo_deleted_mid_run_is_not_resurrected(self):
        # Deleting a memo removes its record and its audio. Writing a
        # transcript back for it would leave a record pointing at no file.
        self.write({"m2": {"trip_id": 1}})
        P._merge_and_write({"m1": {"transcript": "gone"}})
        self.assertNotIn("m1", self.read())

    def test_other_records_are_left_alone(self):
        self.write({"m1": {"trip_id": 1}, "m2": {"trip_id": 2, "note": "keep"}})
        P._merge_and_write({"m1": {"transcript": "x"}})
        self.assertEqual(self.read()["m2"], {"trip_id": 2, "note": "keep"})

    def test_write_is_atomic(self):
        # Written via a temp file and os.replace, so a reader never sees a
        # half-written file — the app reads this on every /api/memos request.
        self.write({"m1": {}})
        P._merge_and_write({"m1": {"transcript": "x"}})
        leftovers = [f for f in os.listdir(self.tmp) if f.endswith(".tmp")]
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
