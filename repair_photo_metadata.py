#!/usr/bin/env python3
"""Re-link per-photo metadata that drifted away from its photo.

WHY THIS EXISTS
---------------
Photo storage is keyed by POSITION — `photo_uploads/{trip}/{idx}/file` for
campspots, `photo_uploads/{trip}/events/{idx}/file` for events — and the five
metadata stores under `trip_data/` use the same key shape. When a campspot or
event is inserted, deleted, or has its date edited so the list re-sorts,
`trips.py` is supposed to move BOTH the photo directories and the metadata keys
so they stay together.

For as long as the photo library had been out of `static/`, only half of that
ran. `trips.py` still built photo paths from `static/uploads/`, which no longer
existed, so every directory rename silently no-op'd (`os.path.isdir()` on a
dead path just returns False) while the metadata remap — which reads live paths
under `trip_data/` — went ahead. The files stood still and the keys walked.

The renumbering bug itself is fixed (see `tests/test_photo_index_remap.py`);
this script repairs the records that drifted before the fix landed.

HOW IT REPAIRS
--------------
By filename. A photo's basename is unique within its trip — the camera stamps
it with a timestamp to the millisecond — so an orphaned key can be matched back
to exactly one photo. The script verifies that uniqueness itself rather than
assuming it, and refuses to touch anything ambiguous.

Four outcomes per record:
  linked       key already points at a live photo — untouched
  relink       exactly one live photo in that trip has this filename — moved
  trashed      the photo is in a `.trash/` dir, i.e. deleted but restorable.
               Metadata is deliberately KEPT for those (it goes inert until the
               photo is restored or `_purge_old_trash` ages it out), so a record
               already sitting at the right index is left alone; one whose index
               drifted is re-linked to where the trashed copy actually lives, so
               a restore reunites them.
  dead         no live and no trashed photo anywhere has that filename. Left in
               place by default (harmless, and filenames are timestamped so a
               future upload will not collide); `--drop-dead` removes them.

`photo_order.json` is different — its keys are `{trip}/{idx}` GROUPS whose
values are filename lists. A group is moved only when every one of its
surviving files lives at one single other index. A group split across indices
is reported, never guessed at.

USAGE
-----
Run on the host that holds the photos (that is PythonAnywhere, not a laptop
with a partial mirror — a photo this machine simply lacks looks identical to a
deleted one, and would be reported "dead"). It refuses to run if the photo
library looks too small to be the real one, unless --force is given.

    python3 repair_photo_metadata.py                 # dry run (default)
    python3 repair_photo_metadata.py --verbose       # ...listing every change
    python3 repair_photo_metadata.py --trip 95       # one trip only
    python3 repair_photo_metadata.py --apply         # write, after a backup
    python3 repair_photo_metadata.py --apply --drop-dead

Applying writes a timestamped `.bak-<stamp>` beside each file it changes, and
is idempotent: a second run finds nothing to do.
"""

import argparse
import collections
import json
import os
import shutil
import sys
from datetime import datetime

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)

# Import rather than restate, so this script cannot drift from the app's idea
# of where photos live or which stores are keyed by photo.
from trips import UPLOAD_DIR, _PHOTO_METADATA_FILES  # noqa: E402

TRIP_DATA = os.path.join(_DIR, "trip_data")
ORDER_STORE = "photo_order.json"
# Regenerable/derivative dirs that hold no originals. `.trash` is handled
# separately — it holds real photos pending purge.
SKIP_DIRS = {".thumbs", ".views", "__pycache__"}
# Below this many photos the library is almost certainly a partial mirror.
MIN_EXPECTED_PHOTOS = 200
# Safety stop for the settle loop; two or three passes is the realistic ceiling.
MAX_PASSES = 8


# ── scanning ──────────────────────────────────────────────────────────────

def scan_photos():
    """Walk the photo library once.

    Returns (live, trashed) where each maps a metadata key
    "{trip}/{idx}/file" or "{trip}/events/{idx}/file" to the directory that
    holds it. A trashed photo is keyed as if it were restored (its `.trash`
    component dropped), because that is the key its metadata carries.
    """
    live, trashed = {}, {}
    if not os.path.isdir(UPLOAD_DIR):
        return live, trashed
    for dirpath, dirnames, filenames in os.walk(UPLOAD_DIR):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel = os.path.relpath(dirpath, UPLOAD_DIR).replace(os.sep, "/")
        if rel == ".":
            continue
        parts = rel.split("/")
        in_trash = parts and parts[-1] == ".trash"
        if any(p.startswith(".") for p in parts[:-1]) or \
           (parts[-1].startswith(".") and not in_trash):
            continue
        group = "/".join(parts[:-1]) if in_trash else rel
        target = trashed if in_trash else live
        for f in filenames:
            if f.startswith("."):
                continue
            target[f"{group}/{f}"] = group
    return live, trashed


def index_by_trip_and_name(keys):
    """(trip, filename) -> [key, ...]. Scoped per trip because that is the
    scope in which a filename is actually unique; two trips can hold photos
    with the same name without either being ambiguous."""
    out = collections.defaultdict(list)
    for k in keys:
        parts = k.split("/")
        out[(parts[0], parts[-1])].append(k)
    return out


# ── planning ──────────────────────────────────────────────────────────────

class Plan:
    def __init__(self):
        self.relink = {}       # store -> {old_key: new_key}
        self.drop = {}         # store -> [key, ...]
        self.counts = collections.Counter()
        self.problems = []     # (store, key, reason)

    def note(self, kind, n=1):
        self.counts[kind] += n


def plan_keyed_store(name, data, live, trashed, live_idx, trash_idx,
                     only_trip, plan):
    """Plan repairs for a store keyed directly by photo ({trip}/{idx}/file)."""
    relink, drop = {}, []
    claimed = {}
    for key in data:
        parts = key.split("/")
        if len(parts) < 3:
            plan.problems.append((name, key, "unrecognised key shape"))
            plan.note("malformed")
            continue
        trip, fname = parts[0], parts[-1]
        if only_trip and trip != only_trip:
            continue
        if key in live:
            plan.note("linked")
            continue
        if key in trashed:
            plan.note("trashed-ok")           # right index already; leave it
            continue

        cands = live_idx.get((trip, fname), [])
        if len(cands) == 1:
            target = cands[0]
        elif len(cands) > 1:
            plan.problems.append((name, key,
                                  "ambiguous: %d live photos share this name"
                                  % len(cands)))
            plan.note("ambiguous")
            continue
        else:
            tc = trash_idx.get((trip, fname), [])
            if len(tc) == 1:
                target = tc[0]
                plan.note("trashed-moved")
            elif len(tc) > 1:
                plan.problems.append((name, key, "ambiguous among trashed"))
                plan.note("ambiguous")
                continue
            else:
                drop.append(key)
                plan.note("dead")
                continue

        if target == key:
            plan.note("linked")
            continue
        if target in data and target not in relink:
            # The destination already holds its own record. Overwriting would
            # silently discard one of them, so leave both for a human.
            plan.problems.append((name, key,
                                  "destination %s already has a record" % target))
            plan.note("conflict")
            continue
        if target in claimed:
            plan.problems.append((name, key,
                                  "two records both want %s (other: %s)"
                                  % (target, claimed[target])))
            plan.note("conflict")
            continue
        claimed[target] = key
        relink[key] = target
        plan.note("relink")
    plan.relink[name] = relink
    plan.drop[name] = drop


def plan_order_store(data, live_idx, only_trip, plan):
    """Plan repairs for photo_order.json, whose keys are `{trip}/{idx}` groups
    and whose values are filename lists."""
    relink, drop = {}, []
    claimed = {}
    for group, files in data.items():
        trip = group.split("/")[0]
        if only_trip and trip != only_trip:
            continue
        if not isinstance(files, list):
            plan.problems.append((ORDER_STORE, group, "value is not a list"))
            plan.note("malformed")
            continue
        homes = set()
        for f in files:
            cands = live_idx.get((trip, f), [])
            if len(cands) == 1:
                homes.add(cands[0].rsplit("/", 1)[0])
            elif len(cands) > 1:
                homes.add("<ambiguous>")
        if not homes:
            drop.append(group)
            plan.note("order-dead")
            continue
        if homes == {group}:
            plan.note("order-ok")
            continue
        if len(homes) > 1 or "<ambiguous>" in homes:
            plan.problems.append(
                (ORDER_STORE, group,
                 "files now live at %d different indices (%s) — needs a human"
                 % (len(homes), ", ".join(sorted(homes)[:4]))))
            plan.note("order-split")
            continue
        target = homes.pop()
        if target in data:
            plan.problems.append((ORDER_STORE, group,
                                  "destination group %s already exists" % target))
            plan.note("conflict")
            continue
        if target in claimed:
            plan.problems.append((ORDER_STORE, group,
                                  "two groups both want %s" % target))
            plan.note("conflict")
            continue
        claimed[target] = group
        relink[group] = target
        plan.note("order-relink")
    plan.relink[ORDER_STORE] = relink
    plan.drop[ORDER_STORE] = drop


# ── applying ──────────────────────────────────────────────────────────────

def load_store(name):
    path = os.path.join(TRIP_DATA, name)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_store(name, data, stamp):
    """Back up, then write in the app's own JSON dialect (indent=2,
    ensure_ascii=False, utf-8) so a repair does not reformat every caption."""
    path = os.path.join(TRIP_DATA, name)
    shutil.copy2(path, f"{path}.bak-{stamp}")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def apply_store(name, data, relink, drop, drop_dead):
    """Rebuild the store with the planned moves. Order is preserved for
    untouched entries; a relinked entry keeps its value and takes a new key."""
    dropping = set(drop) if drop_dead else set()
    out = {}
    for key, value in data.items():
        if key in dropping:
            continue
        out[relink.get(key, key)] = value
    return out


# ── reporting ─────────────────────────────────────────────────────────────

LABELS = [
    ("linked",        "already correct"),
    ("relink",        "re-linked to their photo"),
    ("trashed-ok",    "photo in .trash, key correct (kept)"),
    ("trashed-moved", "photo in .trash, key re-linked"),
    ("dead",          "photo gone entirely"),
    ("ambiguous",     "ambiguous — skipped"),
    ("conflict",      "destination occupied — skipped"),
    ("malformed",     "unrecognised key — skipped"),
    ("order-ok",      "order groups already correct"),
    ("order-relink",  "order groups re-linked"),
    ("order-split",   "order groups split across indices — skipped"),
    ("order-dead",    "order groups whose files are all gone"),
]


def main():
    ap = argparse.ArgumentParser(
        description="Re-link per-photo metadata that drifted from its photo.")
    ap.add_argument("--apply", action="store_true",
                    help="write the changes (default is a dry run)")
    ap.add_argument("--drop-dead", action="store_true",
                    help="also remove records whose photo no longer exists")
    ap.add_argument("--trip", type=str, default=None,
                    help="limit to one trip id")
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="list every individual change")
    ap.add_argument("--force", action="store_true",
                    help="run even if the photo library looks like a partial mirror")
    args = ap.parse_args()

    live, trashed = scan_photos()
    print("photo library: %s" % UPLOAD_DIR)
    print("  live photos: %d   in .trash: %d" % (len(live), len(trashed)))
    if len(live) < MIN_EXPECTED_PHOTOS and not args.force:
        print("\nREFUSING TO RUN: only %d photos found, which looks like a partial\n"
              "mirror rather than the full library. On a partial mirror a photo\n"
              "that is merely absent is indistinguishable from a deleted one, so\n"
              "this would report live records as dead. Run it on the host that\n"
              "holds the photos, or pass --force if you are certain."
              % len(live), file=sys.stderr)
        return 2

    live_idx = index_by_trip_and_name(live)
    trash_idx = index_by_trip_and_name(trashed)
    dupes = {k: v for k, v in live_idx.items() if len(v) > 1}
    print("  ambiguous (trip, filename) pairs: %d%s"
          % (len(dupes), "" if not dupes else "  — those records are skipped"))

    stores = {}
    for name in _PHOTO_METADATA_FILES:
        data = load_store(name)
        if data is None:
            print("  (%s absent — skipped)" % name)
            continue
        stores[name] = data

    def build_plan(current):
        p = Plan()
        for nm, data in current.items():
            if nm == ORDER_STORE:
                plan_order_store(data, live_idx, args.trip, p)
            else:
                plan_keyed_store(nm, data, live, trashed, live_idx, trash_idx,
                                 args.trip, p)
        return p

    def changes_in(p):
        return sum(len(p.relink.get(n, {})) +
                   (len(p.drop.get(n, [])) if args.drop_dead else 0)
                   for n in stores)

    # Settle rather than single-pass. A refusal can be ordering-dependent: a
    # record won't move onto an occupied destination, but the record occupying
    # it may itself move away in the same pass, freeing it for the next one.
    # Planning once left work on the table and made the real fix "run it
    # twice", which is the kind of instruction that gets lost. So iterate on an
    # in-memory copy until nothing more moves; `plan` then describes the
    # settled state and `moves` the cumulative old->new key per store.
    work = {n: dict(d) for n, d in stores.items()}
    moves = {n: {k: k for k in d} for n, d in stores.items()}
    dropped = {n: [] for n in stores}
    passes = 0
    while passes < MAX_PASSES:
        step = build_plan(work)
        if not changes_in(step):
            break
        for n in work:
            rl, dd = step.relink.get(n, {}), step.drop.get(n, [])
            work[n] = apply_store(n, work[n], rl, dd, args.drop_dead)
            if rl or (args.drop_dead and dd):
                gone = set(dd) if args.drop_dead else set()
                for orig, cur in list(moves[n].items()):
                    if cur in gone:
                        dropped[n].append(orig)
                        del moves[n][orig]
                    elif cur in rl:
                        moves[n][orig] = rl[cur]
        passes += 1
    plan = build_plan(work)          # what remains once everything has settled
    for n in stores:
        plan.relink[n] = {o: c for o, c in moves[n].items() if o != c}
        plan.drop[n] = dropped[n] if args.drop_dead else plan.drop.get(n, [])
    if passes > 1:
        print("  (settled after %d passes — a refusal can free up once the "
              "record blocking it moves)" % passes)

    print("\n%-38s %s" % ("outcome", "records"))
    print("-" * 50)
    for key, label in LABELS:
        if plan.counts.get(key):
            print("%-38s %6d" % (label, plan.counts[key]))

    changed_total = 0
    print("\nper store:")
    for name in stores:
        rl = plan.relink.get(name, {})
        dd = plan.drop.get(name, [])
        n = len(rl) + (len(dd) if args.drop_dead else 0)
        changed_total += n
        print("  %-24s %4d to re-link, %4d dead%s"
              % (name, len(rl), len(dd),
                 " (will be removed)" if args.drop_dead and dd else ""))
        if args.verbose:
            for old, new in list(rl.items()):
                print("      %s\n        -> %s" % (old, new))
            if args.drop_dead:
                for k in dd:
                    print("      drop %s" % k)

    if plan.problems:
        print("\nneeds a human (%d):" % len(plan.problems))
        for store, key, why in plan.problems[:40]:
            print("  [%s] %s\n      %s" % (store, key, why))
        if len(plan.problems) > 40:
            print("  ... and %d more" % (len(plan.problems) - 40))

    if not changed_total:
        print("\nNothing to change.")
        return 0

    if not args.apply:
        print("\nDRY RUN — nothing written. Re-run with --apply to make these "
              "%d change(s)." % changed_total)
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for name, data in stores.items():
        rl = plan.relink.get(name, {})
        dd = plan.drop.get(name, [])
        if not rl and not (args.drop_dead and dd):
            continue
        new = apply_store(name, data, rl, dd, args.drop_dead)
        # A dict rebuild would silently swallow a record if two keys ever
        # landed on the same target. The planner's `claimed`/occupied checks
        # should make that impossible; verify rather than trust, because the
        # failure mode is losing a caption without saying so.
        expected = len(data) - (len(dd) if args.drop_dead else 0)
        if len(new) != expected:
            print("  ABORTING %s: rebuild has %d records, expected %d — "
                  "two keys collided. Nothing written for this store."
                  % (name, len(new), expected), file=sys.stderr)
            continue
        write_store(name, new, stamp)
        print("  wrote %s (backup: %s.bak-%s)" % (name, name, stamp))
    print("\nApplied %d change(s). Re-run without --apply to confirm it is clean."
          % changed_total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
