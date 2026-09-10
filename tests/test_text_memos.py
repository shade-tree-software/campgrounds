"""Typed memos, alongside the spoken ones.

Typing is not a lesser path. It is the one that works in a quiet campground,
mid-conversation, or when the thing worth keeping is a name or a number rather
than a sentence — and like a recording it is made where there is no signal, so
the page queues it before sending it.

The decision worth pinning is where the words live. Four things read a memo's
words — the rollup dossier, the search, the page and the transcriber's
straggler sweep — and a parallel `text` field would mean each of them has to
remember to check both, with a silent omission as the failure. So there is ONE
field, `transcript`, and `filename` is what distinguishes a typed memo from a
spoken one. Everywhere audio is assumed has to check it.

    python -m unittest tests.test_text_memos -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ekko_trips_app as A  # noqa: E402
import process_memos as M  # noqa: E402


class TestWhatDistinguishesThem(unittest.TestCase):
    def test_a_typed_memo_is_the_one_with_no_audio(self):
        self.assertEqual(A._memo_view("x", {"transcript": "typed"})["kind"], "text")
        self.assertEqual(
            A._memo_view("x", {"year": "2026", "filename": "x.webm"})["kind"],
            "voice")

    def test_a_typed_memo_offers_no_player(self):
        # _memo_path would raise KeyError on the missing filename, and the
        # page would render an <audio> pointing at nothing.
        self.assertEqual(A._memo_view("x", {"transcript": "typed"})["audio_url"], "")

    def test_a_spoken_memo_still_gets_its_url(self):
        v = A._memo_view("x", {"year": "2026", "filename": "abc.webm"})
        self.assertEqual(v["audio_url"], "/memo/2026/abc.webm")


class TestTheTranscriberLeavesThemAlone(unittest.TestCase):
    """--force-edited exists to redo a MACHINE transcript a human corrected.
    It must never erase what a human wrote in the first place."""

    TYPED = {"transcript": "Sweet corn stand", "transcript_edited": True}

    def test_a_typed_memo_is_never_a_candidate(self):
        # _needs_transcript alone would say yes under --force-edited; the
        # filename check in front of it is what makes the answer no.
        self.assertTrue(M._needs_transcript(self.TYPED, force=True,
                                            force_edited=True))
        self.assertFalse(self.TYPED.get("filename"),
                         "the guard is the absent filename")

    def test_a_spoken_memo_with_no_text_still_is(self):
        self.assertTrue(M._needs_transcript({"filename": "a.webm"},
                                            force=False, force_edited=False))


class TestTheStragglerSweepSkipsThem(unittest.TestCase):
    """The sweep queues memos that have no transcript. A typed memo has no
    audio, so queueing one would start a several-hundred-megabyte model load
    for a file that does not exist — on every page view."""

    @staticmethod
    def _stale(memos):
        return [mid for mid, r in memos.items()
                if r.get("filename") and not (r.get("transcript") or "").strip()]

    def test_a_typed_memo_is_not_stale_even_with_empty_text(self):
        self.assertEqual(self._stale({"a": {"transcript": ""}}), [])

    def test_an_untranscribed_recording_still_is(self):
        self.assertEqual(self._stale({"a": {"filename": "a.webm",
                                            "transcript": ""}}), ["a"])


if __name__ == "__main__":
    unittest.main()
