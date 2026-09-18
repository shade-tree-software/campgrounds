#!/usr/bin/env python3
"""Fill `hookups` for recreation.gov campgrounds from RIDB's per-campsite catalog.

docs/campground-schema.md §7. After phase 3 read hookups out of note prose, 41%
of federal entries still had no `electric` — and the map's Hookups filter fades
every one of them (§8.5). RIDB answers that per CAMPSITE, which is better
evidence than any note: every site carries a `CampsiteType` that says ELECTRIC
or NONELECTRIC, and electric sites carry `Electricity Hookup` ("20/30/50"),
`Water Hookup` and `Sewer Hookup` values.

Two steps, like `recgov_calendar.py`, and for the same reason — the network half
is slow and the reasoning half should be re-runnable for free:

    python recgov_hookups.py --fetch [--limit N]   # RIDB -> trip_data cache
    python recgov_hookups.py --report              # free: cache coverage + yield
    python recgov_hookups.py                       # dry run: what would change
    python recgov_hookups.py --apply               # write campgrounds.json

`--fetch` needs `RIDB_API_KEY` (from `.env`). The cache
(`trip_data/ridb_campsites.json`, gitignored, regenerable) is written after
EVERY facility, a re-run skips what it holds, and Ctrl-C finishes the facility
in flight — so stopping costs nothing and resuming is running it again.
"""

import argparse
import datetime
import json
import os
import re
import signal
import sys
import time
import urllib.error
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import campground_schema as cs
from recgov_calendar import facility_ids
from ridb.fetch_facility import _get

CAMPGROUNDS_JSON = "campgrounds.json"
CACHE_JSON = os.path.join("trip_data", "ridb_campsites.json")

# The only attributes kept. Everything else a campsite carries (tent pad width,
# shade, check-in time) is dropped before caching, which keeps the cache a few
# MB instead of a few hundred. The three length/entry fields are not read here
# yet: fetching is the slow half, so they ride along for a later `sites` pass
# (max_rig_ft, pull_through) instead of costing a second walk of every facility.
KEEP_ATTRS = ("Electricity Hookup", "Water Hookup", "Sewer Hookup",
              "Driveway Length", "Driveway Entry", "Max Vehicle Length")

# RIDB answers 50 requests a minute on a key; stay well under it so a long run
# never trips the limit, since a burst is held against you long afterwards
# (the calendar endpoint taught that — reference_recgov_calendar_limits).
PAUSE_S = 1.5
BACKOFF_S = (60, 180, 420)


# ── Fetch ───────────────────────────────────────────────────────────────────

def load_cache():
    try:
        with open(CACHE_JSON, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}


def save_cache(cache):
    tmp = CACHE_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(cache, fh, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, CACHE_JSON)


def compact_site(site):
    """The part of one RIDB campsite the derivation reads."""
    attrs = {}
    for a in site.get("ATTRIBUTES") or []:
        name = a.get("AttributeName", "")
        if name in KEEP_ATTRS:
            attrs[name] = (a.get("AttributeValue") or "").strip()
    return {
        "type": (site.get("CampsiteType") or "").strip().upper(),
        "equip": sorted({(e.get("EquipmentName") or "").strip().upper()
                         for e in site.get("PERMITTEDEQUIPMENT") or []} - {""}),
        "attrs": attrs,
    }


def _get_paced(path, params):
    """One RIDB request, paced, backing off in MINUTES on a rate limit."""
    for wait in BACKOFF_S + (None,):
        time.sleep(PAUSE_S)
        try:
            return _get(path, params)
        except urllib.error.HTTPError as e:
            if e.code != 429 or wait is None:
                raise
            print(f"  429 — backing off {wait}s", flush=True)
            time.sleep(wait)


def fetch_campsites(fid):
    sites, offset = [], 0
    while True:
        data = _get_paced(f"facilities/{fid}/campsites",
                          {"limit": 50, "offset": offset}) or {}
        rec = data.get("RECDATA") or []
        sites.extend(rec)
        total = (data.get("METADATA") or {}).get("RESULTS", {}).get(
            "TOTAL_COUNT", len(sites))
        offset += len(rec)
        if not rec or offset >= total:
            return sites


def run_fetch(limit, max_age_days):
    with open(CAMPGROUNDS_JSON, encoding="utf-8") as fh:
        rows = json.load(fh)
    fids = sorted(set(facility_ids(rows).values()), key=int)
    cache = load_cache()
    today = datetime.date.today()

    def stale(fid):
        held = cache.get(fid)
        if not held:
            return True
        if max_age_days is None:
            return False
        age = today - datetime.date.fromisoformat(held["fetched"])
        return age.days > max_age_days

    todo = [f for f in fids if stale(f)]
    held = len(fids) - len(todo)
    if limit:
        todo = todo[:limit]
    print(f"{len(fids):,} facilities, {held:,} cached, fetching {len(todo):,}",
          flush=True)

    stop = {"now": False}

    def on_sigint(signum, frame):
        print("\nstopping after this facility…", flush=True)
        stop["now"] = True
    signal.signal(signal.SIGINT, on_sigint)

    done = 0
    for fid in todo:
        if stop["now"]:
            break
        try:
            sites = fetch_campsites(fid)
        except Exception as e:                       # noqa: BLE001
            # A facility RIDB can't answer is skipped, not cached: absent means
            # "not fetched", and a failure must never be stored as a result.
            print(f"  {fid}: {e}", flush=True)
            continue
        cache[fid] = {"fetched": today.isoformat(),
                      "sites": [compact_site(s) for s in sites]}
        save_cache(cache)
        done += 1
        if done % 25 == 0:
            print(f"  {done:,}/{len(todo):,}", flush=True)
    print(f"fetched {done:,}; cache holds {len(cache):,}", flush=True)


# ── Derive ──────────────────────────────────────────────────────────────────

# Equipment that makes a site usable by an RV (upper-cased RIDB names), the same
# set `ridb.fetch_facility` judges fit with.
from ridb.fetch_facility import RV_EQUIPMENT

YES = {"yes", "y"}
NO = {"no", "n"}


def rv_sites(sites):
    """The sites an RV family could book: individual drive-in sites.

    Hookups at a group area, a tent-only loop, a walk-to site or the host's
    MANAGEMENT pad are real but answer a different question from the one the
    map's filter asks — whether EKKO can plug in — so they are left out.
    A STANDARD site whose permitted equipment is listed and names no RV is
    tent-only in practice (Moraine Park has 143 of those), so it is out too;
    one with NO list is kept, as `ridb.fetch_facility` does, because the list
    is simply missing on many facilities.
    """
    out = []
    for site in sites:
        t = site["type"]
        if not (t.startswith("STANDARD") or t.startswith("RV")):
            continue
        equip = set(site.get("equip") or [])
        if equip and not equip & RV_EQUIPMENT:
            continue
        out.append(site)
    return out


def electric_kind(site_type):
    """'yes' / 'no' / None from the CampsiteType wording alone."""
    if "NONELECTRIC" in site_type:
        return "no"
    if "ELECTRIC" in site_type:
        return "yes"
    return None


def _flag(value):
    v = (value or "").strip().lower()
    return True if v in YES else False if v in NO else None


def _amps(value):
    """Highest amperage named in an Electricity Hookup value ("20/30/50")."""
    nums = [int(n) for n in re.findall(r"\d+", value or "")]
    nums = [n for n in nums if 10 <= n <= 100]
    return max(nums) if nums else None


def snap_amps(amps):
    """RIDB amperage onto the schema's 0 | 20 | 30 | 50.

    Snapped DOWN, never up: a 15-amp outlet is not a 20-amp one, so anything
    under 20 is not representable and the caller writes nothing rather than
    promote it.
    """
    for step in (50, 30, 20):
        if amps >= step:
            return step
    return None


def derive(sites):
    """{electric, water, sewer} this facility's RV sites establish, or {}.

    Every key is written only when the catalog SAYS it (doc §2.1):

    - electric: an ELECTRIC site with an amperage gives the highest amperage.
      `0` only when EVERY RV site is typed NONELECTRIC — the site type is the
      booking system's own classification, so a whole campground of them is a
      measured no. One site whose type says neither leaves it unknown.
    - water / sewer: true when any RV site says yes; false only when EVERY RV
      site carries an explicit no. A blank or missing attribute is silence, and
      most non-electric sites carry none at all.
    """
    rv = rv_sites(sites)
    if not rv:
        return {}
    out = {}

    kinds = [electric_kind(s["type"]) for s in rv]
    powered = [s for s, k in zip(rv, kinds) if k == "yes"]
    if powered:
        amps = [a for a in (_amps(s["attrs"].get("Electricity Hookup"))
                            for s in powered) if a]
        snapped = snap_amps(max(amps)) if amps else None
        if snapped:
            out["electric"] = snapped
    elif all(k == "no" for k in kinds):
        out["electric"] = 0

    for key, attr in (("water", "Water Hookup"), ("sewer", "Sewer Hookup")):
        flags = [_flag(s["attrs"].get(attr)) for s in rv]
        if any(f is True for f in flags):
            out[key] = True
        elif all(f is False for f in flags):
            out[key] = False
    return out


# ── Apply ───────────────────────────────────────────────────────────────────

SOURCE = "recreation.gov campsite catalog (RIDB)"
HUMAN_METHODS = {"manual", "reported"}


def human_verified(entry):
    prov = (entry.get(cs.PROVENANCE) or {}).get("hookups") or {}
    return prov.get("method") in HUMAN_METHODS


def plan(rows, cache):
    """What an apply would do, per entry — computed, never written.

    Returns (fills, conflicts, skipped): fills maps entry id -> {key: value} for
    keys the entry does not hold; conflicts lists (entry, key, held, ridb) where
    the entry already says something else. Conflicts are reported, NEVER
    overwritten: the note that produced the held value may know about a
    campground the catalog is stale on, and deciding that is a reading job.
    """
    links = facility_ids(rows)
    shared = Counter(links.values())
    by_id = {r["id"]: r for r in rows}
    fills, conflicts, skipped = {}, [], Counter()
    for cid, fid in links.items():
        entry = by_id[cid]
        if shared[fid] > 1:
            # Two entries on one facility is either a duplicate or a wrong link
            # (Opossum Creek and "Old Hwy 41 #3" share one); either way the
            # facility's hookups can't be pinned on one of them unread.
            skipped["facility shared by several entries"] += 1
            continue
        if fid not in cache:
            skipped["not fetched yet"] += 1
            continue
        if human_verified(entry):
            skipped["hookups verified by a person"] += 1
            continue
        found = derive(cache[fid]["sites"])
        if not found:
            skipped["catalog says nothing"] += 1
            continue
        held = entry.get("hookups") or {}
        new = {}
        for key, value in found.items():
            if key not in held:
                new[key] = value
            elif held[key] != value:
                conflicts.append((entry, key, held[key], value))
        if new:
            fills[cid] = new
        else:
            skipped["already agrees"] += 1
    return fills, conflicts, skipped


def apply(fills, today):
    """Write the fills, re-reading campgrounds.json first (a live edit wins)."""
    with open(CAMPGROUNDS_JSON, encoding="utf-8") as fh:
        rows = json.load(fh)
    by_id = {r["id"]: r for r in rows}
    written = 0
    for cid, new in fills.items():
        entry = by_id.get(cid)
        if entry is None or human_verified(entry):
            continue
        held = entry.get("hookups") or {}
        new = {k: v for k, v in new.items() if k not in held}
        if not new:
            continue
        prov = dict(entry.get(cs.PROVENANCE) or {})
        before = (prov.get("hookups") or {}).get("source")
        source = SOURCE if not before or before == SOURCE else f"{before}; {SOURCE}"
        prov["hookups"] = {"source": source, "checked": today, "method": "derived"}
        cs.apply_update(entry, {"hookups": new, cs.PROVENANCE: prov})
        written += 1
    tmp = CAMPGROUNDS_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, CAMPGROUNDS_JSON)
    return written


def describe(rows, cache, fills, conflicts, skipped, verbose):
    links = facility_ids(rows)
    print(f"{len(set(links.values())):,} linked facilities, {len(cache):,} cached")
    print(f"{len(fills):,} entries gain hookup keys")
    keys = Counter()
    for new in fills.values():
        for k, v in new.items():
            keys[(k, v)] += 1
    for (k, v), n in sorted(keys.items(), key=lambda kv: (kv[0][0], str(kv[0][1]))):
        print(f"  {k:9} {str(v):6} {n:6,}")
    for why, n in skipped.most_common():
        print(f"  skipped — {why}: {n:,}")
    print(f"{len(conflicts):,} conflicts with a value already held (never overwritten)")
    by_key = Counter((k, str(h), str(r)) for _, k, h, r in conflicts)
    for (k, h, r), n in by_key.most_common(12):
        print(f"  {k:9} held {h:6} catalog {r:6} {n:5,}")
    if verbose:
        for e, k, h, r in conflicts:
            print(f"    {e['id']:6} {e.get('state')} {e['name'][:44]:44} {k} held={h} ridb={r}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--max-age-days", type=int)
    ap.add_argument("--report", action="store_true",
                    help="alias for the dry run; free, reads only the cache")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--conflicts", action="store_true",
                    help="list every conflicting entry")
    args = ap.parse_args()
    if args.fetch:
        run_fetch(args.limit, args.max_age_days)
        return
    with open(CAMPGROUNDS_JSON, encoding="utf-8") as fh:
        rows = json.load(fh)
    cache = load_cache()
    fills, conflicts, skipped = plan(rows, cache)
    describe(rows, cache, fills, conflicts, skipped, args.conflicts)
    if args.apply:
        n = apply(fills, datetime.date.today().isoformat())
        print(f"wrote {n:,} entries")
    else:
        print("(dry run — --apply writes)")


if __name__ == "__main__":
    main()
