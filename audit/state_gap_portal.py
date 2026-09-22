#!/usr/bin/env python3
"""Measure one state's campground gap against the STATE AGENCY'S OWN booking portal.

Every per-state sweep is complete against RV Life, whose index silently omits
real campgrounds (`reference_rvlife_index_has_gaps`). `ridb_gap_triage.py` is
the federal cross-check. This is the equivalent for state agencies, for the
states whose portal runs on US eDirect and therefore publishes a machine
readable park list.

    python3 audit/state_gap_portal.py --portal oh
    python3 audit/state_gap_portal.py --portal mn --out audit/state_gap_mn.json

Two endpoints do the work, both keyless:

    <base>/rdr/fd/citypark    every park, with Name/Latitude/Longitude/PlaceId
    <base>/rdr/fd/facilities  every bookable facility, with its PlaceId

**The facility NAMES are the classifier, not `FacilityType`** — that field is
uniformly 2 in both OH and FL and says nothing. "Independence Dam Campground"
vs "Adams Lake Day Use Area" vs "MILTON MARINA A DOCK" is the whole signal, and
it is what keeps a day-use park out of the work list.

**A park with no campground facility is not a miss**, which is most of them:
Florida's portal lists 161 parks and 102 had no entry of ours, but they are
museums, springs, preserves and fishing piers — only 2 had any camping at all.
Report the camping ones and judge those by hand.

**Known blind spots, which is why a 0 here is not a clean bill of health:**

- The portal only sees what the agency takes RESERVATIONS for. A first-come
  campground outside the system is invisible. Ohio's six state-forest
  campgrounds are FCFS and absent from ReserveOhio entirely; they were checked
  by hand (all horse or hunter camps bar the two already held).
- Some agencies run a second portal for a second division. Florida's state
  FOREST campgrounds are not in ReserveFlorida.
- Coordinates are sometimes 0,0 — MN's state forests all are — so those rows
  can never match on distance and always surface as unmatched. That is a
  feature here (it forces a look) but means the match rate understates.
- Most states are not on US eDirect at all: ReserveAmerica/Aspira portals
  publish no clean park list, and California has left the platform (its old
  `calirdr` host no longer resolves).
"""
import argparse, collections, json, math, re, urllib.request

PORTALS = {
    "oh": ("OH", "https://ohiordr.usedirect.com/Ohiordr"),
    "fl": ("FL", "https://floridardr.usedirect.com/FloridaRDR"),
    "mn": ("MN", "https://mnrdr.usedirect.com/MinnesotaRDR"),
}
UA = {"User-Agent": "Mozilla/5.0 (campground coverage audit)"}
STOP = {"state", "park", "campground", "campgrounds", "recreation", "area", "sp",
        "the", "and", "of", "lake", "camping", "resort", "nature", "preserve"}


def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90))


def toks(name):
    n = (name or "").lower().replace("&", " and ").replace("'", "")
    n = re.sub(r"\bmt\b", "mount", n)
    return {w for w in re.sub(r"[^a-z0-9 ]", " ", n).split() if w and w not in STOP}


def haversine(a, b, c, d):
    R = 6371.0
    p1, p2 = math.radians(a), math.radians(c)
    dp, dl = math.radians(c - a), math.radians(d - b)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def kind(name):
    """What a facility IS, read off its name. See the module docstring."""
    n = (name or "").lower()
    if any(w in n for w in ("cabin", "cottage", "lodge", "yurt", "bunk")):
        return "lodging"
    if "campground" in n or "campsite" in n or re.search(r"\bcamps?\b", n) or "rv " in n:
        return "CAMP"
    if any(w in n for w in ("day use", "picnic", "shelter", "pavilion", "beach")):
        return "day-use"
    if any(w in n for w in ("marina", "dock", "slip", "mooring", "ramp", "harbor")):
        return "marina"
    return "other"


def ours_for(state, path="campgrounds.json"):
    out = []
    for e in json.load(open(path, encoding="utf-8")):
        if e.get("state") != state or e.get("ownership") != "state":
            continue
        try:
            la, lo = (float(x) for x in e["location"].split(","))
        except Exception:
            continue
        out.append({"id": e["id"], "name": e["name"], "lat": la, "lng": lo, "t": toks(e["name"])})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--portal", required=True, choices=sorted(PORTALS))
    ap.add_argument("--radius-km", type=float, default=12.0)
    ap.add_argument("--out")
    args = ap.parse_args()

    state, base = PORTALS[args.portal]
    raw = get(f"{base}/rdr/fd/citypark")
    vals = list(raw.values()) if isinstance(raw, dict) else raw
    parks = [v for v in vals if isinstance(v, dict) and v.get("PlaceId", 0) > 0]
    facilities = get(f"{base}/rdr/fd/facilities")

    by_place = collections.defaultdict(list)
    for f in facilities:
        by_place[f.get("PlaceId")].append(f.get("Name") or "")

    ours = ours_for(state)
    matched, unmatched = [], []
    for p in parks:
        la, lo = p.get("Latitude"), p.get("Longitude")
        best = None
        if la not in (None, 0) and lo not in (None, 0):
            pt = toks(p.get("Name"))
            for o in ours:
                d = haversine(la, lo, o["lat"], o["lng"])
                if d > args.radius_km:
                    continue
                score = (len(pt & o["t"]) > 0, -d)
                if best is None or score > best[0]:
                    best = (score, o, d, len(pt & o["t"]))
        if best and (best[3] > 0 or best[2] <= 3.0):
            matched.append(p)
        else:
            unmatched.append(p)

    candidates = []
    for p in unmatched:
        fs = by_place.get(p["PlaceId"], [])
        if any(kind(n) == "CAMP" for n in fs):
            candidates.append({"place_id": p["PlaceId"], "name": p.get("Name"),
                               "lat": p.get("Latitude"), "lng": p.get("Longitude"),
                               "facilities": fs})

    print(f"{state}: portal lists {len(parks)} parks; we hold {len(ours)} state-ownership entries")
    print(f"  matched          : {len(matched)}")
    print(f"  unmatched        : {len(unmatched)}")
    print(f"  WITH A CAMPGROUND: {len(candidates)}  <- judge these by hand\n")
    for c in candidates:
        print(f"  [{c['place_id']}] {c['name']}")
        for n in c["facilities"][:8]:
            print(f"        {kind(n):8} {n}")
    if args.out:
        json.dump({"state": state, "portal": base, "parks": len(parks),
                   "ours": len(ours), "matched": len(matched),
                   "unmatched": len(unmatched), "candidates": candidates},
                  open(args.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
