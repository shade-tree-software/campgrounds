#!/usr/bin/env python3
"""List one state's private campgrounds that have no entry in the database.

Two directories are diffed against campgrounds.json:

  * RV Life (Algolia index `park`, the same source every private sweep used),
    `park_type == commercial`, pulled by bounding box and tiled so no tile hits
    Algolia's 1,000-hit cap. Cached to trip_data/rvlife_<ST>.json.
  * The Good Sam directory (trip_data/goodsam_parks.json, from
    `goodsam_discounts.py --fetch`), its private types only.

A directory row counts as HELD when an entry sits within 3 km with a matching
name (goodsam_discounts' own name matcher) or within 250 m whatever its name.
Everything else is printed with the RV Life columns (stars / $ tier / avg rate
/ sites). The price gate is RV Life's own $ tag (docs/campground-curation.md, AWH
2026-10-01): price_level $ or $$ passes with no price check, $$$+ fails
(barring a special exception), no tier -> avg_rate <= NO_TIER_RATE, and
neither -> passes the screen and needs a published base rate <= $50 read
during vetting.
Unrated rows and Good-Sam-only parks are eligible too, on a quality signal
from elsewhere.

The output is CANDIDATES, not misses. Membership, condo, MHP and seasonal
parks come through; judge each by hand and record it in
audit/private_gap_decisions.json.

    python3 audit/private_gap_list.py --state MI            # summary + gate-passers
    python3 audit/private_gap_list.py --state MI --all      # every unmatched row
    python3 audit/private_gap_list.py --state MI --json out.json
"""
import argparse
import json
import math
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import goodsam_discounts as gs  # noqa: E402

RV_APP = "H0LPZK92QJ"
RV_KEY = "88da91e06e8ee5ec4aba26675ac26b99"  # public search key, inline in every rvlife.com page
RV_URL = f"https://{RV_APP.lower()}-dsn.algolia.net/1/indexes/park/query"
RV_ATTRS = ["cg_name", "city_name", "region_abbvr", "park_type", "price_level",
            "star_rating", "avg_rate", "cg_site_count", "cg_rating_count", "_geoloc",
            "url", "closed", "temp_closed", "affiliations"]

GS_PRIVATE = {"CAMPGROUND", "RV_PARK", "RV_RESORT", "RV_SPACES", "UNKNOWN"}
HELD_NAME_M = 3000
HELD_ANY_M = 250
NO_TIER_RATE = 40


def rv_query(params):
    body = json.dumps({"params": params}).encode()
    req = urllib.request.Request(RV_URL, data=body, method="POST")
    req.add_header("X-Algolia-Application-Id", RV_APP)
    req.add_header("X-Algolia-API-Key", RV_KEY)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)


def rv_box(box, depth=0):
    """Every RV Life hit inside box=(s, w, n, e), splitting past the 1,000 cap."""
    s, w, n, e = box
    from urllib.parse import quote
    params = (f"query=&hitsPerPage=1000&attributesToRetrieve={quote(','.join(RV_ATTRS))}"
              f"&attributesToHighlight=&insideBoundingBox={quote(json.dumps([[s, w, n, e]]))}")
    data = rv_query(params)
    if data["nbHits"] < 1000 or depth > 6:
        return data["hits"]
    mlat, mlng = (s + n) / 2, (w + e) / 2
    out = []
    for sub in ((s, w, mlat, mlng), (s, mlng, mlat, e), (mlat, w, n, mlng), (mlat, mlng, n, e)):
        out.extend(rv_box(sub, depth + 1))
        time.sleep(0.2)
    return out


def rvlife_state(state, bbox, refresh=False):
    path = os.path.join(ROOT, "trip_data", f"rvlife_{state}.json")
    if not refresh and os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)["parks"]
    hits = rv_box(bbox)
    seen, parks = set(), []
    for h in hits:
        if h.get("region_abbvr") != state or h["objectID"] in seen:
            continue
        seen.add(h["objectID"])
        g = h.get("_geoloc") or {}
        parks.append({"rv_id": h["objectID"], "name": h.get("cg_name"),
                      "city": h.get("city_name"), "type": h.get("park_type"),
                      "price": h.get("price_level"), "stars": h.get("star_rating"),
                      "rate": h.get("avg_rate"), "sites": h.get("cg_site_count"),
                      "reviews": h.get("cg_rating_count"),
                      "closed": h.get("closed") or h.get("temp_closed"),
                      "lat": g.get("lat"), "lng": g.get("lng"),
                      "url": "https://campgrounds.rvlife.com" + (h.get("url") or "")})
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"fetched": time.strftime("%Y-%m-%d"), "parks": parks}, fh,
                  ensure_ascii=False, indent=0)
    return parks


def entries():
    with open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8") as fh:
        rows = json.load(fh)
    out = []
    for r in rows:
        try:
            lat, lng = (float(x) for x in r["location"].split(","))
        except (KeyError, ValueError):
            continue
        out.append((r, lat, lng))
    return out


def held(name, lat, lng, db):
    """(True, why) when an entry answers for this directory row."""
    best = None
    for r, elat, elng in db:
        if abs(elat - lat) > 0.04 or abs(elng - lng) > 0.06:
            continue
        m = gs.haversine_m(lat, lng, elat, elng)
        if m <= HELD_ANY_M:
            return True, f"{r['id']} {r['name']} @{m:.0f}m"
        if m <= HELD_NAME_M:
            score, whole = gs.similarity(name, r["name"])
            if gs.accepts(score, whole, m) or (score >= 0.75 and m <= 1500):
                return True, f"{r['id']} {r['name']} @{m:.0f}m"
        if best is None or m < best[0]:
            best = (m, r)
    near = f"nearest {best[1]['id']} {best[1]['name'][:30]} @{best[0]/1000:.1f}km" if best else "nothing within ~5km"
    return False, near


def cheap(p):
    """The AWH 2026-10-01 price gate; see the module docstring."""
    if p.get("price"):
        return p["price"] <= 2
    return not p.get("rate") or p["rate"] <= NO_TIER_RATE


def gate(p):
    return cheap(p) and (p.get("stars") or 0) >= 4


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state", required=True)
    ap.add_argument("--all", action="store_true", help="print every unmatched row")
    ap.add_argument("--refresh", action="store_true", help="re-pull RV Life")
    ap.add_argument("--json", metavar="PATH")
    args = ap.parse_args()
    st = args.state.upper()

    gsp = [p for p in gs.load_cache().values() if p.get("state") == st and p.get("lat")]
    if not gsp:
        raise SystemExit("no Good Sam rows for that state - run goodsam_discounts.py --fetch")
    lats = [p["lat"] for p in gsp]
    lngs = [p["lng"] for p in gsp]
    bbox = (min(lats) - 0.3, min(lngs) - 0.3, max(lats) + 0.3, max(lngs) + 0.3)
    rv = rvlife_state(st, bbox, args.refresh)
    db = entries()

    # RV Life commercial rows not held.
    rv_c = [p for p in rv if p["type"] == "commercial" and p.get("lat")]
    rv_miss = []
    for p in rv_c:
        ok, why = held(p["name"], p["lat"], p["lng"], db)
        if not ok:
            rv_miss.append(dict(p, near=why))

    # Good Sam private rows not held and not the same park as an RV Life row.
    gs_miss = []
    for p in gsp:
        if p["type"] not in GS_PRIVATE:
            continue
        ok, why = held(p["name"], p["lat"], p["lng"], db)
        if ok:
            continue
        twin = None
        for r in rv:
            if not r.get("lat"):
                continue
            m = gs.haversine_m(p["lat"], p["lng"], r["lat"], r["lng"])
            if m <= 3000:
                score, whole = gs.similarity(p["name"], r["name"])
                if gs.accepts(score, whole, m) or (score >= 0.75 and m <= 1500):
                    twin = r
                    break
        if twin is None:
            gs_miss.append(dict(p, near=why))

    passing = [p for p in rv_miss if gate(p)]
    price_only = [p for p in rv_miss if (p.get("stars") or 0) >= 4 and not gate(p)]
    unrated = [p for p in rv_miss if not p.get("stars") and cheap(p)]
    print(f"{st}: RV Life {len(rv)} parks, {len(rv_c)} commercial, {len(rv_miss)} not held")
    print(f"    price-passing ($/$$, or no tier and avg_rate <= ${NO_TIER_RATE} or none; >=4*): {len(passing)}")
    print(f"    >=4* but $$$+ (or no tier and avg_rate over ${NO_TIER_RATE}): {len(price_only)}")
    print(f"    unrated, screen price ok (need a quality signal elsewhere): {len(unrated)}")
    print(f"  Good Sam private rows not held and absent from RV Life: {len(gs_miss)}")

    def line(p):
        return (f"  {p['stars'] or 0:>3}* {'$' * (p['price'] or 0):<4} ${p['rate'] or '?':<4} "
                f"{p['sites'] or '?':>4}s {p['reviews'] or 0:>4}r  {p['name'][:42]:<42} "
                f"{(p['city'] or '')[:16]:<16} {p['near']}")

    print("\nPRICE-PASSING (research these; a no-tier, no-avg row needs a published rate):")
    for p in sorted(passing, key=lambda p: -(p["stars"] or 0)):
        print(line(p))
    if args.all:
        print("\nPRICE-ONLY FAILS:")
        for p in sorted(price_only, key=lambda p: -(p["stars"] or 0)):
            print(line(p))
        print("\nUNRATED:")
        for p in unrated:
            print(line(p))
        print("\nGOOD SAM ONLY:")
        for p in gs_miss:
            print(f"  {p['type']:<12} gs={p['gs']!s:<5} {p['name'][:44]:<44} {p['city'] or '':<16} {p['near']}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"state": st, "passing": passing, "price_only": price_only,
                       "unrated": unrated, "rv_other": [p for p in rv_miss if p not in passing
                                                        and p not in price_only and p not in unrated],
                       "goodsam_only": gs_miss}, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
