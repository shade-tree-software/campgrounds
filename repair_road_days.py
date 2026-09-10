#!/usr/bin/env python3
"""Move road photos onto the day their EXIF says they were taken.

A road card is keyed by DATE, and during a drag every day of the trip shows a
placeholder — fourteen of them on trip 95 — so a photo dropped on the wrong one
was filed under the wrong day and nothing said so. The app now takes the day
from the photograph at both upload and move time; this repairs the ones filed
before it did.

The photo already knows the answer: the EXIF timestamp is the same field that
orders a road card and places its photos on the map. A photo with no EXIF date
is left exactly where it is — nothing better is known about it.

The five metadata stores are keyed by the same path, so a caption, a favorite,
an uploader record and a people record all follow the photo to its new day.

    python repair_road_days.py             # report
    python repair_road_days.py --apply
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true", help="actually move them")
    ap.add_argument("--trip", type=int, help="only this trip")
    args = ap.parse_args()

    import ekko_trips_app as A

    trips = [t for t in A.parse_trips()
             if args.trip is None or t["id"] == args.trip]
    moves = []
    for trip in trips:
        tid = trip["id"]
        for day in A._road_days(tid):
            src_dir = A._road_photo_dir(tid, day)
            for fname in sorted(os.listdir(src_dir)):
                if not A._allowed_file(fname):
                    continue
                path = os.path.join(src_dir, fname)
                real = A._road_day_for_photo(path, day)
                if real != day:
                    moves.append((tid, day, real, fname))

    if not moves:
        print("Every road photo is already on the day it was taken.")
        return 0
    for tid, day, real, fname in moves:
        print(f"  trip {tid}: {fname}  {day} -> {real}")
    print(f"\n{len(moves)} photo(s) on the wrong day.")
    if not args.apply:
        print("(dry run — pass --apply to move them)")
        return 0

    for tid, day, real, fname in moves:
        src = os.path.join(A._road_photo_dir(tid, day), fname)
        dest_dir = A._road_photo_dir(tid, real)
        os.makedirs(dest_dir, exist_ok=True)
        dest_name = fname
        if os.path.exists(os.path.join(dest_dir, dest_name)):
            base, ext = os.path.splitext(fname)
            dest_name = f"{base}_moved{ext}"
        os.replace(src, os.path.join(dest_dir, dest_name))
        old_key = f"{tid}/{A.ROAD_DIRNAME}/{day}/{fname}"
        new_key = f"{tid}/{A.ROAD_DIRNAME}/{real}/{dest_name}"
        # Same helpers the move-photo route uses, so a caption, a star, an
        # uploader record and a face count all follow the photo.
        with A.json_store_lock(A.CAPTIONS_FILE):
            caps = A._load_json(A.CAPTIONS_FILE)
            if old_key in caps:
                caps[new_key] = caps.pop(old_key)
                A._save_json(A.CAPTIONS_FILE, caps)
        A._rename_uploader_key(old_key, new_key)
        A._rename_favorite_key(old_key, new_key)
        A._rename_people_key(old_key, new_key)
        with A.json_store_lock(A.PHOTO_ORDER_FILE):
            order = A._load_json(A.PHOTO_ORDER_FILE)
            ok_old = f"{tid}/{A.ROAD_DIRNAME}/{day}"
            ok_new = f"{tid}/{A.ROAD_DIRNAME}/{real}"
            if ok_old in order:
                order[ok_old] = [f for f in order[ok_old] if f != fname]
                if not order[ok_old]:
                    del order[ok_old]
            order.setdefault(ok_new, []).append(dest_name)
            A._save_json(A.PHOTO_ORDER_FILE, order)

    # Empty day directories are what make a card disappear; leave none behind.
    for tid in {m[0] for m in moves}:
        root = os.path.join(A.UPLOAD_DIR, str(tid), A.ROAD_DIRNAME)
        for name in os.listdir(root):
            d = os.path.join(root, name)
            if os.path.isdir(d) and not os.listdir(d):
                os.rmdir(d)
    A._invalidate_photo_pool()
    print(f"Moved {len(moves)} photo(s). Run backfill_place_context.py "
          f"--only <trip> to name the new days.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
