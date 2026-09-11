"""Salvaging a torn JSON store: what is recovered, and what is set aside.

A store written by two requests at once used to end up as a complete document
followed by the tail of a longer one, and every page that read it 500'd.
`_save_json`'s temp-file-and-rename made new writes atomic, but files torn
before that fix still exist, so `_load_json` salvages the leading document,
repairs the file, and keeps a copy of the damaged bytes.

The copy is the point: the tail is the update that lost the race, and it is the
only remaining record of it. (The real one this pinned was
`photo_order.json`'s `95/events/67` on 2026-09-10, restored by hand from the
kept copy.) So the rule for how many copies to keep has to cut between two
failures — 35 identical copies from a file nobody repaired, and throwing away
a second, different tear because a copy of the first still sits there.

    python -m unittest tests.test_json_salvage -v
"""

import glob
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ekko_trips_app as A  # noqa: E402


def _dump(data):
    return json.dumps(data, indent=2, ensure_ascii=False)


class TestTornStoreSalvage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "store.json")
        # The app logs each salvage at ERROR; the test provokes several.
        self._level = A.app.logger.level
        A.app.logger.setLevel(60)

    def tearDown(self):
        A.app.logger.setLevel(self._level)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _tear(self, winner, loser):
        """Write `winner` over `loser`, leaving `loser`'s tail behind it.

        Exactly what two non-atomic writes produced: the shorter document, then
        the bytes of the longer one that reached past its end.
        """
        won, lost = _dump(winner), _dump(loser)
        self.assertGreater(len(lost), len(won), "loser must be the longer write")
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(won + lost[len(won):])

    def _copies(self):
        return sorted(glob.glob(self.path + ".corrupt-*"))

    def test_the_leading_document_is_salvaged_and_the_file_repaired(self):
        self._tear({"a": [1]}, {"a": [1], "b": [2]})
        self.assertEqual(A._load_json(self.path), {"a": [1]})
        # Repaired in place, so the next reader pays nothing and the log stops.
        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(json.load(f), {"a": [1]})

    def test_the_losing_writers_bytes_are_kept(self):
        self._tear({"a": [1]}, {"a": [1], "b": [2]})
        A._load_json(self.path)
        kept = self._copies()
        self.assertEqual(len(kept), 1)
        # The tail is the only record of the update that lost the race, so it
        # must still be readable out of the copy.
        with open(kept[0], encoding="utf-8") as f:
            raw = f.read()
        _, end = json.JSONDecoder().raw_decode(raw.lstrip())
        self.assertEqual(json.loads("{" + raw[end:].strip()), {"b": [2]})

    def test_the_same_damage_twice_keeps_one_copy(self):
        """A file nobody repairs is re-salvaged on every page load; 35 copies
        of identical bytes accumulated on the live host in an afternoon."""
        for _ in range(3):
            self._tear({"a": [1]}, {"a": [1], "b": [2]})
            A._load_json(self.path)
        self.assertEqual(len(self._copies()), 1)

    def test_a_second_different_tear_is_kept_too(self):
        """The one that matters: once the file is repaired, the next tear is
        NEW damage. Reusing the existing copy because one merely exists would
        discard the only record of it."""
        self._tear({"a": [1]}, {"a": [1], "b": [2]})
        A._load_json(self.path)
        self._tear({"a": [1], "b": [2]}, {"a": [1], "b": [2], "c": [3]})
        A._load_json(self.path)

        tails = []
        for name in self._copies():
            with open(name, encoding="utf-8") as f:
                raw = f.read()
            _, end = json.JSONDecoder().raw_decode(raw.lstrip())
            tails.append(json.loads("{" + raw[end:].strip()))
        self.assertEqual(tails, [{"b": [2]}, {"c": [3]}])

    def test_an_unsalvageable_file_raises_rather_than_emptying_the_store(self):
        """Half a document is not a document. Returning {} would look like an
        empty store and let the next write persist the loss."""
        with open(self.path, "w", encoding="utf-8") as f:
            f.write('{"a": [1], "b"')
        with self.assertRaises(ValueError):
            A._load_json(self.path)


if __name__ == "__main__":
    unittest.main()
