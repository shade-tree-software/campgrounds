"""The campground database is two tracked files: `campgrounds.json` and the audit
sidecar `campgrounds_audit.json` (see campground_store.py). The split exists to keep
the main file under GitHub's 50 MB warning, so the property worth pinning is that the
main file carries none of the audit fields — an old script writing one straight into
it would quietly regrow the file — and that load/save round-trips without loss.
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import campground_store as store  # noqa: E402


class RealFiles(unittest.TestCase):

    def test_main_file_carries_no_audit_field(self):
        with open(store.CAMPGROUNDS_JSON, encoding="utf-8") as fh:
            rows = json.load(fh)
        stray = [(e["id"], k) for e in rows for k in store.AUDIT_FIELDS if k in e]
        self.assertEqual(stray[:10], [], "move them with campground_store.save(campground_store.load())")

    def test_both_files_are_canonical(self):
        for path in (store.CAMPGROUNDS_JSON, store.audit_path()):
            with self.subTest(path=os.path.basename(path)):
                with open(path, encoding="utf-8") as fh:
                    raw = fh.read()
                # Modulo the final newline: the app's _save_json (a UI save on PA)
                # writes none, and capture-pa-edits.sh brings that file down as is.
                self.assertEqual(store.dumps(json.loads(raw)).rstrip("\n"), raw.rstrip("\n"))


class LoadSave(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "campgrounds.json")
        self.rows = [
            {"id": 1, "name": "A", "note": "x", "waterfront_evidence": "sat 1", "note_scan": {"sig": "s"}},
            {"id": 2, "name": "B"},
            {"id": 3, "name": "C", "verify_scan": {"checked": "2026-11-21"}},
        ]
        with open(self.path, "w", encoding="utf-8") as fh:
            fh.write(store.dumps(self.rows))
        os.chmod(self.path, 0o664)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def raw(self, path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    def test_save_splits_and_load_merges(self):
        store.save(store.load(self.path), self.path)
        self.assertEqual(self.raw(self.path), [{"id": 1, "name": "A", "note": "x"},
                                               {"id": 2, "name": "B"}, {"id": 3, "name": "C"}])
        self.assertEqual(self.raw(store.audit_path(self.path)),
                         {"1": {"waterfront_evidence": "sat 1", "note_scan": {"sig": "s"}},
                          "3": {"verify_scan": {"checked": "2026-11-21"}}})
        self.assertEqual(store.load(self.path), self.rows)
        self.assertEqual(os.stat(self.path).st_mode & 0o777, 0o664)

    def test_a_raw_load_saved_back_keeps_the_audit_record(self):
        store.save(store.load(self.path), self.path)
        rows = self.raw(self.path)              # what an old script sees
        rows[1]["note"] = "edited"
        store.save(rows, self.path)
        merged = {e["id"]: e for e in store.load(self.path)}
        self.assertEqual(merged[1]["waterfront_evidence"], "sat 1")
        self.assertEqual(merged[2]["note"], "edited")

    def test_a_field_written_to_the_main_file_wins_and_moves(self):
        store.save(store.load(self.path), self.path)
        rows = self.raw(self.path)
        rows[0]["waterfront_evidence"] = "sat 2"
        with open(self.path, "w", encoding="utf-8") as fh:
            fh.write(store.dumps(rows))
        self.assertEqual(store.load(self.path)[0]["waterfront_evidence"], "sat 2")
        store.save(store.load(self.path), self.path)
        self.assertNotIn("waterfront_evidence", self.raw(self.path)[0])
        self.assertEqual(self.raw(store.audit_path(self.path))["1"]["waterfront_evidence"], "sat 2")

    def test_a_dropped_entry_takes_its_audit_row(self):
        store.save(store.load(self.path), self.path)
        store.save([e for e in store.load(self.path) if e["id"] != 3], self.path)
        self.assertNotIn("3", self.raw(store.audit_path(self.path)))

    def test_deleting_a_field_needs_authoritative(self):
        store.save(store.load(self.path), self.path)
        rows = store.load(self.path)
        del rows[0]["note_scan"]
        store.save(rows, self.path)
        self.assertIn("note_scan", store.load(self.path)[0])
        store.save(rows, self.path, authoritative=True)
        self.assertNotIn("note_scan", store.load(self.path)[0])


if __name__ == "__main__":
    unittest.main()
