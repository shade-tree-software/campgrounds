#!/usr/bin/env python3
"""Measure one state's LOCAL-government campground gap against OpenStreetMap.

The local face of the non-RV-Life gap (county / city / town / township /
regional-authority campgrounds) cannot borrow the state answer: its detection
was a name-scan of RV Life's own buckets, so it inherits RV Life's omissions
twice, and no state booking portal lists county parks. OpenStreetMap is the
independent instrument: volunteers map campgrounds from the ground and tag an
`operator`, and that is a population RV Life never saw.

    python3 audit/local_gap_osm.py --state OH
    python3 audit/local_gap_osm.py --state TX --out audit/local_gap_tx.json

What it does:
  1. Overpass: every tourism=camp_site / caravan_site inside the state.
  2. Keeps the ones whose operator / owner / name reads as local government
     (county, city, town, township, village, borough, parish, municipal,
     regional, metro, park district, conservancy/watershed district, ...).
  3. Matches each against ALL of our entries (any ownership) by distance, with
     a name-token check for the 1.5-4 km band.
  4. Writes the unmatched ones for judging by hand.

**The unmatched list is candidates, not misses.** OSM maps tent-only group
camps, youth camps, fairgrounds and closed parks too. The rate that matters
is (real misses after judging) / (matched + real misses) - judge before
quoting a number, exactly as the state portal pass did.

Blind spots: a local campground OSM has no operator tag for, and whose name
does not say "County"/"City", is invisible here. So this is a lower bound on
the candidate pool, but an unbiased sample of the population it does see.
"""
import argparse, json, math, re, time, urllib.parse, urllib.request

ENDPOINTS = ("https://overpass-api.de/api/interpreter",
             "https://overpass.private.coffee/api/interpreter")
UA = {"User-Agent": "ekko-trips-audit (local campground coverage)"}
LOCAL_RE = re.compile(
    r"\b(county|counties|city of|town of|township|village of|borough|parish|"
    r"municipal|municipality|regional|metro ?parks?|park district|"
    r"parks? (and|&) rec|recreation district|watershed|conservancy|"
    r"forest preserve|conservation district|city park|town park|county park)\b",
    re.I)
NOT_LOCAL_RE = re.compile(
    r"\b(state park|state forest|national|forest service|usfs|blm|bureau of|"
    r"corps of engineers|usace|koa|scout|ymca|church|bible|christian|4-h|"
    r"private)\b", re.I)
STOP = {"campground", "campgrounds", "camping", "camp", "park", "county", "city",
        "the", "and", "of", "area", "recreation", "rv", "site", "sites", "lake"}


def overpass(state):
    q = (f'[out:json][timeout:240];area["ISO3166-2"="US-{state}"]->.a;'
         f'(nwr["tourism"~"^(camp_site|caravan_site)$"](area.a););out center tags;')
    for attempt in range(6):
        ep = ENDPOINTS[attempt % len(ENDPOINTS)]
        try:
            req = urllib.request.Request(
                ep, data=urllib.parse.urlencode({"data": q}).encode(), headers=UA)
            return json.load(urllib.request.urlopen(req, timeout=300))["elements"]
        except Exception as e:  # noqa: BLE001 - Overpass 504s under load; back off
            print(f"  overpass {ep}: {e}; retrying", flush=True)
            time.sleep(30 * (attempt + 1))
    raise SystemExit("overpass unavailable")


def toks(s):
    return {t for t in re.findall(r"[a-z0-9]+", (s or "").lower()) if t not in STOP and len(t) > 2}


def km(a, b, c, d):
    p = math.radians
    return 2 * 6371 * math.asin(math.sqrt(math.sin(p(c - a) / 2) ** 2 +
                                          math.cos(p(a)) * math.cos(p(c)) * math.sin(p(d - b) / 2) ** 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    st = a.state.upper()
    els = overpass(st)
    db = [e for e in json.load(open("campgrounds.json", encoding="utf-8")) if e.get("location")]
    pts = []
    for e in db:
        la, lo = map(float, e["location"].split(","))
        pts.append((la, lo, e))
    local, matched, unmatched = [], [], []
    for el in els:
        t = el.get("tags", {})
        c = el.get("center", el)
        if "lat" not in c:
            continue
        who = " ".join(t.get(k, "") for k in ("operator", "owner", "operator:type", "ownership", "name"))
        if not LOCAL_RE.search(who) or NOT_LOCAL_RE.search(who):
            continue
        if t.get("access") in ("private", "no") or t.get("group_only") == "yes":
            continue
        row = {"osm": f"{el['type']}/{el['id']}", "name": t.get("name", ""),
               "operator": t.get("operator", t.get("owner", "")),
               "lat": round(c["lat"], 6), "lng": round(c["lon"], 6),
               "caravans": t.get("caravans"), "tents": t.get("tents"),
               "website": t.get("website", t.get("contact:website", ""))}
        local.append(row)
        best = None
        nt = toks(row["name"])
        for la, lo, e in pts:
            d = km(row["lat"], row["lng"], la, lo)
            if d < 1.5 or (d < 4 and nt and nt & toks(e["name"])):
                if best is None or d < best[0]:
                    best = (d, e)
        if best:
            row["match"] = {"id": best[1]["id"], "name": best[1]["name"], "km": round(best[0], 2)}
            matched.append(row)
        else:
            unmatched.append(row)
    print(f"{st}: {len(els)} OSM campsites, {len(local)} read as local government, "
          f"{len(matched)} matched to an entry, {len(unmatched)} unmatched")
    for r in unmatched:
        print(f"  {r['osm']:>18} {r['lat']},{r['lng']}  {r['name']!r} | op={r['operator']!r} "
              f"caravans={r['caravans']} tents={r['tents']} {r['website']}")
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump({"state": st, "osm_campsites": len(els), "local": len(local),
                       "matched": matched, "unmatched": unmatched}, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
