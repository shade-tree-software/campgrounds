"""Photos must stay with the campspot/event/waypoint they were attached to.

Inserting a stay or event in the middle of a trip, deleting one, or editing a
date so the list re-sorts all renumber the positional indices that photo
storage is keyed by (`photo_uploads/{trip}/{idx}/` and
`photo_uploads/{trip}/events/{idx}/`, plus the same `{trip}/{idx}/...` shape in
every per-photo metadata store). `trips.py` is supposed to move the photos and
their metadata to follow — and for a long time it did not, because it still
built photo paths from `static/uploads/`, which stopped existing when the
library moved to `photo_uploads/`. Every `os.path.isdir()` on the dead path
returned False, so the directory renames silently no-op'd while the metadata
remap (which reads live paths under `trip_data/`) went ahead: photos shifted a
slot relative to their item, and their captions/favourites shifted the other
way relative to the photos.

These tests pin the invariant rather than the implementation: after each
mutation, every surviving item owns exactly its own photo file and its own
record in all five metadata stores, and a deleted item leaves nothing behind.

Run from the project root with the venv active:

    python -m unittest tests.test_photo_index_remap -v
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import trips  # noqa: E402

META = trips._PHOTO_METADATA_FILES
# Three items on three dates, one photo each, named after the item so a photo
# that ends up under the wrong one is obvious.
BASE = [("2026-01-01", "ALPHA"), ("2026-01-03", "BRAVO"), ("2026-01-05", "CHARLIE")]


def _read_json(path):
    with open(path) as f:
        return json.load(f)


def _write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


class PhotoIndexRemapTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._saved = (trips._DIR, trips.UPLOAD_DIR, trips.TRIPS_JSON)
        trips._DIR = self.tmp
        trips.UPLOAD_DIR = os.path.join(self.tmp, "photo_uploads")
        trips.TRIPS_JSON = os.path.join(self.tmp, "trip_data", "trips.json")

    def tearDown(self):
        trips._DIR, trips.UPLOAD_DIR, trips.TRIPS_JSON = self._saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ── fixture ──────────────────────────────────────────────────────────
    def _build(self, kind):
        os.makedirs(os.path.join(self.tmp, "trip_data"), exist_ok=True)
        stays, events = [], []
        for d, n in BASE:
            if kind == "stay":
                stays.append({"start": d, "end": d, "nights": 1,
                              "campground_id": None, "custom_place": n,
                              "locale": "", "state": "", "site": "",
                              "campers": "", "notes": ""})
            else:
                events.append({"date": d, "time": "10:00", "name": n,
                               "description": "", "location": "", "locale": "",
                               "state": "", "waypoint": False, "family_id": None,
                               "needs_vetting": False})
        _write_json(trips.TRIPS_JSON,
                    [{"id": 1, "trip_note": "t", "stays": stays, "events": events}])

        sub = "" if kind == "stay" else "events"
        meta = {m: {} for m in META}
        for i, (_d, n) in enumerate(BASE):
            d = self._dir(sub, i)
            os.makedirs(d)
            with open(os.path.join(d, n + ".jpg"), "w") as f:
                f.write(n)
            for m in META:
                meta[m][self._key(sub, i) + n + ".jpg"] = n
        for m in META:
            _write_json(os.path.join(self.tmp, "trip_data", m), meta[m])

    def _dir(self, sub, idx):
        parts = [trips.UPLOAD_DIR, "1"] + ([sub] if sub else []) + [str(idx)]
        return os.path.join(*parts)

    def _key(self, sub, idx):
        return f"1/{sub}/{idx}/" if sub else f"1/{idx}/"

    # ── assertion ────────────────────────────────────────────────────────
    def _assert_intact(self, kind, gone=()):
        raw = _read_json(trips.TRIPS_JSON)
        items = [] if not raw else (raw[0]["stays"] if kind == "stay"
                                    else raw[0]["events"])
        sub = "" if kind == "stay" else "events"
        name_of = (lambda it: it["custom_place"]) if kind == "stay" \
            else (lambda it: it["name"])
        loaded = {m: _read_json(os.path.join(self.tmp, "trip_data", m))
                  for m in META}

        for i, it in enumerate(items):
            n = name_of(it)
            # A freshly inserted item legitimately owns nothing yet.
            want_files = [] if n.startswith("NEW") else [n + ".jpg"]
            want_meta = [] if n.startswith("NEW") else [n]
            d = self._dir(sub, i)
            files = sorted(os.listdir(d)) if os.path.isdir(d) else []
            self.assertEqual(files, want_files,
                             f"{kind} [{i}] {n} has the wrong photos")
            pre = self._key(sub, i)
            for m in META:
                got = sorted(v for k, v in loaded[m].items() if k.startswith(pre))
                self.assertEqual(got, want_meta,
                                 f"{kind} [{i}] {n} has the wrong {m} record")

        for n in gone:
            for m in META:
                self.assertNotIn(n, loaded[m].values(),
                                 f"deleted {n} left a stale record in {m}")
            for dirpath, _dn, filenames in os.walk(trips.UPLOAD_DIR):
                self.assertNotIn(n + ".jpg", filenames,
                                 f"deleted {n} left a photo file behind")

    # ── events ───────────────────────────────────────────────────────────
    def test_event_insert_middle(self):
        self._build("event")
        trips.add_event(1, {"date": "2026-01-02", "time": "10:00", "name": "NEW"})
        self._assert_intact("event")

    def test_event_insert_front(self):
        self._build("event")
        trips.add_event(1, {"date": "2025-12-31", "time": "10:00", "name": "NEW"})
        self._assert_intact("event")

    def test_event_insert_end(self):
        self._build("event")
        trips.add_event(1, {"date": "2026-01-09", "time": "10:00", "name": "NEW"})
        self._assert_intact("event")

    def test_event_delete_middle(self):
        self._build("event")
        trips.delete_event(1, 1)
        self._assert_intact("event", gone=("BRAVO",))

    def test_event_delete_first(self):
        self._build("event")
        trips.delete_event(1, 0)
        self._assert_intact("event", gone=("ALPHA",))

    def test_event_date_edit_reorders(self):
        self._build("event")
        trips.update_event(1, 0, {"date": "2026-01-09"})   # ALPHA moves last
        self._assert_intact("event")

    # ── campspots ────────────────────────────────────────────────────────
    def test_stay_insert_middle(self):
        self._build("stay")
        trips.add_stay(1, {"start": "2026-01-02", "end": "2026-01-03",
                           "custom_place": "NEW"})
        self._assert_intact("stay")

    def test_stay_delete_middle(self):
        self._build("stay")
        trips.delete_stay(1, 1)
        self._assert_intact("stay", gone=("BRAVO",))

    def test_stay_delete_first(self):
        self._build("stay")
        trips.delete_stay(1, 0)
        self._assert_intact("stay", gone=("ALPHA",))

    def test_stay_date_edit_reorders(self):
        self._build("stay")
        trips.update_stay(1, 0, {"start": "2026-01-09", "end": "2026-01-10"})
        self._assert_intact("stay")


if __name__ == "__main__":
    unittest.main()
