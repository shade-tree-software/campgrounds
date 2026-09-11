"""The day's own note: where it lives, and that it beats a drafted write-up.

A day divider has one write-up slot. Two things can fill it — a note somebody
typed, and a rollup drafted from the day's facts — and the typed one always
wins. The drafted ones were measured against a real trip and mostly restated
the cards printed directly below them, which is the whole reason the note
exists: the person who was there knows the part the facts cannot supply, and a
sentence of theirs costs nothing.

The storage split is the load-bearing half. A draft is regenerable and lives in
the gitignored, sync-excluded, per-host `day_rollups.json`; a typed note exists
nowhere else, so it goes on the trip record and travels home from the live host
by the same path as every other thing written about a trip.

    python -m unittest tests.test_day_notes -v
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import trips  # noqa: E402
import ekko_trips_app as A  # noqa: E402

DAY = "2026-08-27"


class TestStorage(unittest.TestCase):
    """set_day_note writes to trips.json, and an emptied note leaves no trace."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._saved = (trips._DIR, trips.TRIPS_JSON)
        trips._DIR = self.tmp
        trips.TRIPS_JSON = os.path.join(self.tmp, "trip_data", "trips.json")
        os.makedirs(os.path.join(self.tmp, "trip_data"), exist_ok=True)
        with open(trips.TRIPS_JSON, "w") as f:
            json.dump([{"id": 1, "trip_note": "", "stays": [], "events": []}],
                      f, indent=2)

    def tearDown(self):
        trips._DIR, trips.TRIPS_JSON = self._saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _record(self):
        with open(trips.TRIPS_JSON) as f:
            return json.load(f)[0]

    def test_a_note_is_stored_on_the_trip(self):
        trips.set_day_note(1, DAY, "Grand Lake, and dinner outdoors.")
        self.assertEqual(self._record()["day_notes"][DAY],
                         "Grand Lake, and dinner outdoors.")
        self.assertEqual(trips.get_day_notes(1)[DAY],
                         "Grand Lake, and dinner outdoors.")

    def test_whitespace_is_trimmed(self):
        trips.set_day_note(1, DAY, "  a long day  \n")
        self.assertEqual(trips.get_day_notes(1)[DAY], "a long day")

    def test_an_emptied_note_removes_the_key_and_the_dict(self):
        trips.set_day_note(1, DAY, "something")
        trips.set_day_note(1, DAY, "   ")
        self.assertNotIn("day_notes", self._record())
        self.assertEqual(trips.get_day_notes(1), {})

    def test_other_days_survive_one_being_cleared(self):
        trips.set_day_note(1, DAY, "kept")
        trips.set_day_note(1, "2026-08-28", "cleared")
        trips.set_day_note(1, "2026-08-28", "")
        self.assertEqual(trips.get_day_notes(1), {DAY: "kept"})

    def test_a_missing_trip_reports_itself(self):
        self.assertIsNone(trips.set_day_note(999, DAY, "x"))


class TestPrecedence(unittest.TestCase):
    """Which of the two sources reaches the template, and how it is labelled."""

    def setUp(self):
        self._rollups = A._trip_day_rollups
        self._notes = A.get_day_notes

    def tearDown(self):
        A._trip_day_rollups = self._rollups
        A.get_day_notes = self._notes

    def _writeups(self, rollups, notes):
        A._trip_day_rollups = lambda trip_id: dict(rollups)
        A.get_day_notes = lambda trip_id: dict(notes)
        return A._trip_day_writeups(1)

    def test_a_note_beats_a_draft_for_the_same_day(self):
        got = self._writeups({DAY: {"text": "drafted", "model": "claude-opus-5"}},
                             {DAY: "typed"})
        self.assertEqual(got[DAY]["text"], "typed")

    def test_a_note_carries_no_model_so_the_attribution_line_goes(self):
        got = self._writeups({DAY: {"text": "drafted", "model": "claude-opus-5"}},
                             {DAY: "typed"})
        self.assertTrue(got[DAY]["by_hand"])
        self.assertNotIn("model", got[DAY])

    def test_a_draft_survives_on_a_day_with_no_note(self):
        got = self._writeups({DAY: {"text": "drafted", "model": "claude-opus-5"}},
                             {"2026-08-28": "typed"})
        self.assertEqual(got[DAY]["text"], "drafted")
        self.assertEqual(got[DAY]["model"], "claude-opus-5")

    def test_a_note_stands_alone_where_there_is_no_draft(self):
        got = self._writeups({}, {DAY: "typed"})
        self.assertEqual(got[DAY]["text"], "typed")

    def test_a_blank_note_hides_the_slot_entirely(self):
        """Belt and braces: set_day_note deletes rather than blanks, but a
        blank that reached the file must not print an empty gold rule."""
        got = self._writeups({DAY: {"text": "drafted", "model": "m"}}, {DAY: "  "})
        self.assertNotIn(DAY, got)


if __name__ == "__main__":
    unittest.main()
