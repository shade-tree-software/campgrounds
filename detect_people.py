#!/usr/bin/env python3
"""Scan the photo library for photos with people in them.

Writes trip_data/photo_people.json — {photo_key: face_count} with one entry
per SCANNED photo (0 means "looked, found nobody"), keyed exactly like
captions/favorites ("{trip_id}/{idx}/{file}" or "{trip_id}/events/{idx}/{file}").
The app reads it in _collect_photo_pool() as a boolean `people` flag, which the
poster's hero deck ranks just below hand-starred favorites.

This is an OFFLINE batch tool, not part of the web app — the app itself never
imports cv2. Run it wherever the full photo library lives (the PythonAnywhere
host, or locally after ./sync-from-pa.sh --photos):

    python detect_people.py              # scan photos not yet in the JSON
    python detect_people.py --force      # rescan everything
    python detect_people.py --prune      # ALSO drop entries whose file is gone
    python detect_people.py --only K [K] # scan just these photo keys

Incremental by design: a photo already recorded (even as 0) is skipped, so
re-running after new uploads only scans the new files. --prune is OFF by
default because a machine holding a partial photo mirror (this repo synced
without --photos) would otherwise delete the records for every photo it
doesn't have.

--only is how the web app triggers a scan of just-uploaded photos (see
_queue_people_scan in ekko_trips_app.py): it skips the directory walk and
scans exactly the keys given, so the run costs one process start plus ~0.2 s
per new photo instead of a stat of the whole library. Results are merged into
the file at write time (re-read, then apply just this run's deltas), so a scan
racing the app's own edits to photo_people.json — a delete scrubbing a record,
a move renaming a key — can't clobber them.

Detector: OpenCV's YuNet face detector (tiny ONNX model, auto-downloaded once
to trip_data/models/ with a pinned sha256). Faces are the signal — a person
photographed from behind or at great distance won't register. That's fine for
the poster: a false negative just leaves a photo in the general pool, and a
false positive merely promotes a photo that would otherwise be a coin flip.

Needs: pip install opencv-python-headless (pillow + numpy already app deps).
Optional: pillow-heif, only if the library contains .heic uploads.
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.request

import numpy as np
from PIL import Image, ImageOps

try:  # .heic support if available; otherwise those files are skipped
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pillow_heif = None

_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(_DIR, "photo_uploads")
OUT_FILE = os.path.join(_DIR, "trip_data", "photo_people.json")

# Same set as the app's _allowed_file — keep in step with ekko_trips_app.py.
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "heic"}

MODEL_URL = ("https://github.com/opencv/opencv_zoo/raw/main/models/"
             "face_detection_yunet/face_detection_yunet_2023mar.onnx")
MODEL_SHA256 = "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4"
MODEL_FILE = os.path.join(_DIR, "trip_data", "models",
                          "face_detection_yunet_2023mar.onnx")

# Longest image side handed to the detector. 1280 resolves faces down to a
# person standing ~10 m away in a phone photo; larger buys little and costs
# quadratic time.
DETECT_MAX_SIDE = 1280
# YuNet's default is 0.9, which drops small/oblique faces; 0.7 trades a few
# false positives (acceptable here — see module docstring) for real recall.
SCORE_THRESHOLD = 0.7


def _ensure_model():
    if os.path.exists(MODEL_FILE):
        return
    os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)
    print(f"Downloading YuNet model to {MODEL_FILE} ...")
    with urllib.request.urlopen(MODEL_URL) as resp:
        blob = resp.read()
    digest = hashlib.sha256(blob).hexdigest()
    if digest != MODEL_SHA256:
        sys.exit(f"Model download hash mismatch ({digest}) — refusing to use it.")
    with open(MODEL_FILE, "wb") as f:
        f.write(blob)


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _iter_photo_keys():
    """Every original photo under photo_uploads/, as (key, abs_path).

    Filesystem-driven rather than trips.json-driven so it also covers photos
    orphaned by a deleted campspot; dot-dirs (.thumbs/.views/.trash) are
    skipped the same way the photo routes refuse them.
    """
    for root, dirs, files in os.walk(UPLOAD_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in sorted(files):
            if not _allowed_file(fname):
                continue
            path = os.path.join(root, fname)
            key = os.path.relpath(path, UPLOAD_DIR).replace(os.sep, "/")
            yield key, path


def _path_for_key(key):
    """Absolute path for one photo key, or None if it isn't a scannable file.

    Same three gates the app's photo routes apply (no dot-prefixed component,
    so .thumbs/.views/.trash stay out; allowed extension; stays under
    UPLOAD_DIR), because these keys arrive from the app rather than from a
    walk of the directory we control.
    """
    parts = key.split("/")
    if any(p in ("", ".", "..") or p.startswith(".") for p in parts):
        return None
    if not _allowed_file(parts[-1]):
        return None
    path = os.path.abspath(os.path.join(UPLOAD_DIR, *parts))
    if not path.startswith(os.path.abspath(UPLOAD_DIR) + os.sep):
        return None
    return path if os.path.isfile(path) else None


def _merge_and_write(updates, removed=()):
    """Apply this run's deltas to the file on disk and return the result.

    Re-reads at write time rather than dumping the dict loaded at startup:
    the web app edits the same file (scrubbing a deleted photo's record,
    renaming a moved photo's key), and since it now also *triggers* this
    script on upload, the two really can overlap.
    """
    current = {}
    if os.path.exists(OUT_FILE):
        with open(OUT_FILE) as f:
            current = json.load(f)
    for key in removed:
        current.pop(key, None)
    current.update(updates)
    tmp = OUT_FILE + f".{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)
    os.replace(tmp, OUT_FILE)
    return current


def _count_faces(detector, path):
    """Face count in one photo, or None if the image can't be read."""
    try:
        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            scale = DETECT_MAX_SIDE / max(im.size)
            if scale < 1:
                im = im.resize((max(1, round(im.width * scale)),
                                max(1, round(im.height * scale))))
            bgr = np.asarray(im)[:, :, ::-1]
    except Exception as e:
        print(f"  unreadable, skipping: {path} ({e})", file=sys.stderr)
        return None
    bgr = np.ascontiguousarray(bgr)
    h, w = bgr.shape[:2]
    detector.setInputSize((w, h))
    _, faces = detector.detect(bgr)
    return 0 if faces is None else len(faces)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--force", action="store_true",
                    help="rescan photos already recorded")
    ap.add_argument("--prune", action="store_true",
                    help="drop records whose photo no longer exists on THIS "
                         "machine (don't use on a partial photo mirror)")
    ap.add_argument("--limit", type=int, default=0,
                    help="stop after scanning N new photos (smoke tests)")
    ap.add_argument("--only", nargs="+", metavar="KEY", default=None,
                    help="scan only these photo keys (e.g. 92/0/IMG_1.jpg); "
                         "skips the directory walk. Used by the app on upload")
    args = ap.parse_args()
    if args.only and args.prune:
        ap.error("--prune scans the whole library; it can't be combined with --only")

    import cv2  # after argparse so --help works without opencv installed
    _ensure_model()
    detector = cv2.FaceDetectorYN.create(
        MODEL_FILE, "", (320, 320), score_threshold=SCORE_THRESHOLD)

    data = {}
    if os.path.exists(OUT_FILE):
        with open(OUT_FILE) as f:
            data = json.load(f)

    gone = []
    if args.only:
        on_disk = {}
        for key in args.only:
            path = _path_for_key(key)
            if path is None:
                print(f"  no such photo, skipping: {key}", file=sys.stderr)
                continue
            on_disk[key] = path
    else:
        on_disk = dict(_iter_photo_keys())
        if args.prune:
            gone = [k for k in data if k not in on_disk]
            for k in gone:
                del data[k]
            if gone:
                print(f"Pruned {len(gone)} records with no file on disk.")

    todo = [(k, p) for k, p in on_disk.items()
            if args.force or k not in data]
    if args.limit:
        todo = todo[:args.limit]
    print(f"{len(on_disk)} photos {'named' if args.only else 'on disk'}, "
          f"{len(todo)} to scan.")

    results = {}
    scanned = with_people = 0
    for key, path in todo:
        n = _count_faces(detector, path)
        if n is None:
            continue
        results[key] = n
        scanned += 1
        with_people += bool(n)
        if scanned % 25 == 0:
            print(f"  {scanned}/{len(todo)} scanned ({with_people} with people)")

    if results or gone:
        data = _merge_and_write(results, gone)

    total_people = sum(1 for v in data.values() if v)
    print(f"Done: scanned {scanned} new photo(s), {with_people} with people. "
          f"{OUT_FILE} now records {len(data)} photos, "
          f"{total_people} with people.")


if __name__ == "__main__":
    main()
