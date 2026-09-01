"""Tests for repair_photo_metadata.py — the re-linker for per-photo metadata
that drifted away from its photo (see that script's module docstring).

It rewrites hand-written captions in place, so the cases that matter most are
the ones where it must REFUSE: an ambiguous filename, a destination that
already holds its own record, and an order group whose files have scattered.
Guessing there would silently attach someone's caption to the wrong photo.

Run from the project root:

    python -m unittest tests.test_repair_photo_metadata -v
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class RepairScriptTest(unittest.TestCase):
    """Each test builds a throwaway copy of the script beside a synthetic photo
    library, so the script's own _DIR-relative paths point at the fixture."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        for f in ("repair_photo_metadata.py", "trips.py"):
            shutil.copy2(os.path.join(ROOT, f), os.path.join(self.tmp, f))
        os.makedirs(os.path.join(self.tmp, "trip_data"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ── fixture helpers ──────────────────────────────────────────────────
    def photo(self, rel):
        p = os.path.join(self.tmp, "photo_uploads", rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write("x")

    def store(self, name, data):
        _write(os.path.join(self.tmp, "trip_data", name), data)

    def load(self, name):
        return _read(os.path.join(self.tmp, "trip_data", name))

    def run_script(self, *args):
        r = subprocess.run(
            [sys.executable, "repair_photo_metadata.py", "--force", *args],
            cwd=self.tmp, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    # ── the happy path ───────────────────────────────────────────────────
    def test_drifted_keys_are_relinked(self):
        for i, n in ((0, "A"), (1, "B"), (2, "C")):
            self.photo(f"7/{i}/IMG_{n}.jpg")
        self.photo("7/events/0/IMG_E.jpg")
        self.store("captions.json", {
            "7/1/IMG_A.jpg": "A", "7/2/IMG_B.jpg": "B", "7/3/IMG_C.jpg": "C",
            "7/events/1/IMG_E.jpg": "E",
        })
        self.run_script("--apply")
        self.assertEqual(self.load("captions.json"), {
            "7/0/IMG_A.jpg": "A", "7/1/IMG_B.jpg": "B", "7/2/IMG_C.jpg": "C",
            "7/events/0/IMG_E.jpg": "E",
        })

    def test_dry_run_writes_nothing(self):
        self.photo("7/0/IMG_A.jpg")
        before = {"7/1/IMG_A.jpg": "A"}
        self.store("captions.json", before)
        out = self.run_script()
        self.assertIn("DRY RUN", out)
        self.assertEqual(self.load("captions.json"), before)

    def test_apply_is_idempotent_and_backs_up(self):
        self.photo("7/0/IMG_A.jpg")
        self.store("captions.json", {"7/1/IMG_A.jpg": "A"})
        self.run_script("--apply")
        baks = [f for f in os.listdir(os.path.join(self.tmp, "trip_data"))
                if ".bak-" in f]
        self.assertEqual(len(baks), 1)
        self.assertIn("Nothing to change", self.run_script())

    def test_cascading_conflict_settles_in_one_invocation(self):
        """Each record wants the slot the next one still occupies. Resolving
        that needs more than one planning pass; the script must not leave the
        tail of the chain for a second run."""
        for i, n in ((0, "P"), (1, "Q"), (2, "S")):
            self.photo(f"5/{i}/IMG_{n}.jpg")
        self.store("captions.json", {"5/1/IMG_P.jpg": "P",
                                     "5/2/IMG_Q.jpg": "Q",
                                     "5/3/IMG_S.jpg": "S"})
        self.run_script("--apply")
        self.assertEqual(self.load("captions.json"),
                         {"5/0/IMG_P.jpg": "P", "5/1/IMG_Q.jpg": "Q",
                          "5/2/IMG_S.jpg": "S"})
        self.assertIn("Nothing to change", self.run_script())

    # ── the refusals ─────────────────────────────────────────────────────
    def test_ambiguous_filename_is_left_alone(self):
        self.photo("7/0/DUP.jpg")
        self.photo("7/1/DUP.jpg")
        before = {"7/5/DUP.jpg": "which one?"}
        self.store("captions.json", before)
        out = self.run_script("--apply")
        self.assertIn("ambiguous", out)
        self.assertEqual(self.load("captions.json"), before)

    def test_occupied_destination_is_left_alone(self):
        self.photo("7/3/HELD.jpg")
        before = {"7/9/HELD.jpg": "claimant", "7/3/HELD.jpg": "incumbent"}
        self.store("captions.json", before)
        out = self.run_script("--apply")
        self.assertIn("already has a record", out)
        self.assertEqual(self.load("captions.json"), before)

    def test_filename_uniqueness_is_scoped_per_trip(self):
        """The same filename in a different trip is not an ambiguity."""
        self.photo("7/0/DUP.jpg")
        self.photo("7/1/DUP.jpg")      # ambiguous within trip 7 only
        self.photo("9/0/DUP.jpg")
        self.store("captions.json", {"9/1/DUP.jpg": "trip nine"})
        self.run_script("--apply")
        self.assertEqual(self.load("captions.json"), {"9/0/DUP.jpg": "trip nine"})

    # ── trash and dead records ───────────────────────────────────────────
    def test_trashed_photo_keeps_its_metadata(self):
        self.photo("7/1/.trash/IMG_T.jpg")
        before = {"7/1/IMG_T.jpg": "deleted but restorable"}
        self.store("captions.json", before)
        self.run_script("--apply")
        self.assertEqual(self.load("captions.json"), before)

    def test_trashed_photo_at_a_drifted_index_follows_the_trash(self):
        """So a later restore still reunites photo and caption."""
        self.photo("7/4/.trash/IMG_T.jpg")
        self.store("captions.json", {"7/2/IMG_T.jpg": "restorable"})
        self.run_script("--apply")
        self.assertEqual(self.load("captions.json"), {"7/4/IMG_T.jpg": "restorable"})

    def test_dead_records_survive_by_default_and_go_with_drop_dead(self):
        self.photo("7/0/IMG_A.jpg")
        self.store("captions.json", {"7/0/IMG_A.jpg": "live",
                                     "7/0/IMG_GONE.jpg": "purged"})
        self.run_script("--apply")
        self.assertIn("7/0/IMG_GONE.jpg", self.load("captions.json"))
        self.run_script("--apply", "--drop-dead")
        self.assertEqual(self.load("captions.json"), {"7/0/IMG_A.jpg": "live"})

    # ── photo_order, whose values are filename lists ─────────────────────
    def test_order_group_moves_whole(self):
        self.photo("7/0/IMG_A.jpg")
        self.store("photo_order.json", {"7/1": ["IMG_A.jpg"]})
        self.run_script("--apply")
        self.assertEqual(self.load("photo_order.json"), {"7/0": ["IMG_A.jpg"]})

    def test_order_group_split_across_indices_is_left_alone(self):
        self.photo("7/0/IMG_A.jpg")
        self.photo("7/1/IMG_B.jpg")
        before = {"7/5": ["IMG_A.jpg", "IMG_B.jpg"]}
        self.store("photo_order.json", before)
        out = self.run_script("--apply")
        self.assertIn("different indices", out)
        self.assertEqual(self.load("photo_order.json"), before)

    # ── operational safety ───────────────────────────────────────────────
    def test_refuses_a_partial_mirror_without_force(self):
        self.photo("7/0/IMG_A.jpg")
        self.store("captions.json", {"7/1/IMG_A.jpg": "A"})
        r = subprocess.run([sys.executable, "repair_photo_metadata.py", "--apply"],
                           cwd=self.tmp, capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("REFUSING TO RUN", r.stderr)
        self.assertEqual(self.load("captions.json"), {"7/1/IMG_A.jpg": "A"})

    def test_unicode_captions_are_not_re_escaped(self):
        self.photo("7/0/IMG_A.jpg")
        self.store("captions.json", {"7/1/IMG_A.jpg": "an em-dash — and café"})
        self.run_script("--apply")
        with open(os.path.join(self.tmp, "trip_data", "captions.json"),
                  encoding="utf-8") as f:
            raw = f.read()
        self.assertIn("—", raw)
        self.assertIn("café", raw)
        self.assertNotIn("\\u", raw)


if __name__ == "__main__":
    unittest.main()
