"""The examples a day is drafted against — the family's own write-ups.

Four hand-written exemplars used to sit frozen in the system prompt. Freezing
them was wrong twice over: `day_notes` is a far better source (every note is a
day AWH wrote AFTER reading what the model made of it, so it is a correction
with the facts still attached), and one of the four had by then been superseded
by the note on that very day. Selected at run time, the examples cannot go
stale — writing a note is now how you correct the drafter.

What this file pins is the SELECTION, because an example of the wrong shape
teaches the wrong paragraph: a day at one campground is about what happened, a
500-mile haul is about the road.

    python -m unittest tests.test_rollup_examples -v
"""

import json
import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import process_rollups as R  # noqa: E402


def _entry(key, *, round_trip=False, miles=None, first=False, last=False,
           events=0, family=False, text="an entry"):
    return {"key": key, "text": text, "facts": {},
            "shape": {"round_trip": round_trip, "miles": miles, "first": first,
                      "last": last, "events": events, "family": family}}


def _target(**kw):
    shape = {"round_trip": False, "miles": None, "first": False, "last": False,
             "events": 0, "family": False}
    shape.update(kw)
    return shape


class TestChoosingExamples(unittest.TestCase):
    def _pick(self, bank, dossier, key="99/2026-01-01", count=1):
        return [e["key"] for e in R.choose_examples(bank, dossier, key, count)]

    def test_a_day_at_one_campground_is_shown_days_at_one_campground(self):
        bank = [_entry("1/2026-01-01", miles=400),
                _entry("2/2026-01-01", round_trip=True, events=2)]
        self.assertEqual(self._pick(bank, {"round_trip": True}),
                         ["2/2026-01-01"])

    def test_a_haul_is_shown_a_haul_of_similar_length(self):
        """Mileage matters as a ratio: 60 against 120 is a difference in kind,
        400 against 460 is not."""
        bank = [_entry("1/2026-01-01", miles=60),
                _entry("2/2026-01-01", miles=430)]
        self.assertEqual(self._pick(bank, {"miles": 459}), ["2/2026-01-01"])

    def test_the_day_being_written_is_never_its_own_example(self):
        bank = [_entry("95/2026-08-24", round_trip=True)]
        self.assertEqual(R.choose_examples(bank, {"round_trip": True},
                                           "95/2026-08-24"), [])

    def test_no_more_than_two_days_from_any_one_trip(self):
        """Drafting one trip was picking its own two neighbouring days and
        calling it a bank; one trip's voice must not become the only voice."""
        bank = [_entry(f"7/2026-01-0{i}", miles=400) for i in range(1, 5)]
        bank.append(_entry("8/2026-01-01", miles=400))
        picked = self._pick(bank, {"miles": 400}, count=4)
        self.assertEqual(len(picked), 3)
        self.assertEqual(sum(1 for k in picked if k.startswith("7/")), 2)

    def test_an_empty_bank_is_not_an_error(self):
        self.assertEqual(R.choose_examples([], {"miles": 400}, "1/2026-01-01"), [])


class TestTheShapeMatchedOn(unittest.TestCase):
    def test_the_last_day_is_read_off_the_outline(self):
        shape = R.example_shape({"day_of_trip": 3, "trip_days": 3,
                                 "trip_outline": [{"day": 1}, {"day": 2},
                                                  {"day": 3}]})
        self.assertTrue(shape["last"])
        self.assertFalse(shape["first"])

    def test_a_round_trip_scores_against_a_round_trip(self):
        self.assertGreater(
            R.example_score(_target(round_trip=True), _target(round_trip=True)),
            R.example_score(_target(miles=400), _target(round_trip=True)))


class TestTheBankIsBuiltFromTheTripRECORD(unittest.TestCase):
    """`parse_trips()` does NOT carry day_notes.

    `_make_trip` builds a display object and doesn't copy the field, so
    `trip.get("day_notes")` on a parsed trip is ALWAYS empty however many notes
    exist — a mistake that once produced a confident "you have no day notes
    anywhere in the library" while seven sat in the file.
    """

    def _app(self):
        return types.SimpleNamespace(
            enrich_trip_locations=lambda t: None,
            _trip_driving_by_day=lambda t: {"2026-08-23": {"miles": 273}})

    def test_a_note_is_found_even_though_the_parsed_trip_lacks_the_field(self):
        trip = {"id": 95, "stays": [{"start": "2026-08-22", "end": "2026-08-23",
                                     "place": "Moraine Park"}], "events": []}
        self.assertEqual(trip.get("day_notes"), None)
        with mock.patch.object(R, "get_day_notes",
                               return_value={"2026-08-23": "Into Colorado."}), \
             mock.patch.object(R, "_track_by_local_day", return_value={}):
            bank = R.build_example_bank(self._app(), [trip], {}, {}, None,
                                        no_elevation=True)
        self.assertEqual([e["key"] for e in bank], ["95/2026-08-23"])
        self.assertEqual(bank[0]["text"], "Into Colorado.")

    def test_a_blank_note_is_not_an_example(self):
        trip = {"id": 95, "stays": [], "events": [{"date": "2026-08-23"}]}
        with mock.patch.object(R, "get_day_notes",
                               return_value={"2026-08-23": "   "}), \
             mock.patch.object(R, "_track_by_local_day", return_value={}):
            self.assertEqual(
                R.build_example_bank(self._app(), [trip], {}, {}, None, True), [])

    def test_an_example_drops_the_outline_it_was_shaped_from(self):
        """The longest field in a dossier and the least transferable: another
        trip's day-by-day mileage teaches nothing about writing this one."""
        trip = {"id": 95, "stays": [{"start": "2026-08-22", "end": "2026-08-23",
                                     "place": "Moraine Park"}], "events": []}
        with mock.patch.object(R, "get_day_notes",
                               return_value={"2026-08-23": "Into Colorado."}), \
             mock.patch.object(R, "_track_by_local_day", return_value={}):
            bank = R.build_example_bank(self._app(), [trip], {}, {}, None, True)
        self.assertNotIn("trip_outline", bank[0]["facts"])


class TestThePrompt(unittest.TestCase):
    def test_examples_come_before_the_day_and_carry_their_own_facts(self):
        prompt = R._prompt({"date": "2026-08-23"},
                           [{"key": "1/2026-01-01", "facts": {"miles": 400},
                             "text": "A long haul."}])
        self.assertLess(prompt.index("A long haul."), prompt.index("2026-08-23"))
        self.assertIn('"miles": 400', prompt)

    def test_they_ride_in_the_user_message_never_in_the_cached_system_block(self):
        """SYSTEM is cached across the whole run; a per-day example bank in it
        would defeat that on every call."""
        self.assertNotIn("ENTRY:", R.SYSTEM)

    def test_no_examples_still_produces_a_usable_prompt(self):
        self.assertIn("2026-08-23", R._prompt({"date": "2026-08-23"}))


if __name__ == "__main__":
    unittest.main()
