#!/usr/bin/env python3
"""List EVERY named OSM campsite in a state that has no entry nearby, for reading by hand.

    python3 audit/local_gap_unmatched.py --state PA            # fetch (cached) + list
    python3 audit/local_gap_unmatched.py --state PA | grep -iE "county|city|town"

local_gap_osm.py keeps only campsites whose tags READ as local government, and in
the eastern pass (2026-09-25) most real finds had no such tag: Green Lane's Deep
Creek, Tohickon Valley, Melville Ponds, Virginia Point, the NWFWMD landings. So
this prints all of them (minus access=private/no, group_only, caravans=no,
backcountry) and leaves the judging to the reader. It also surfaces the state,
federal and private gaps as a side effect - NY's missing DEC campgrounds and
Maine's ~150 private campgrounds came out of this listing.

The raw Overpass answer is cached under trip_data/osm_campsites/<ST>.json,
because statewide queries 504 often and a mirror can return a TRUNCATED answer
(PA once came back with 34 elements instead of 1,017): a count far below the
state's size means delete the cache file and fetch again.
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import local_gap_osm as L  # noqa: E402  (toks, km, UA)

ENDPOINTS = ("https://overpass.kumi.systems/api/interpreter",
             "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
             "https://overpass-api.de/api/interpreter",
             "https://overpass.private.coffee/api/interpreter")
CACHE = os.path.join("trip_data", "osm_campsites")


def fetch(st):
    path = os.path.join(CACHE, f"{st}.json")
    if os.path.exists(path):
        return json.load(open(path))
    q = (f'[out:json][timeout:300];area["ISO3166-2"="US-{st}"]->.a;'
         f'(nwr["tourism"~"^(camp_site|caravan_site)$"](area.a););out center tags;')
    for i in range(12):
        ep = ENDPOINTS[i % len(ENDPOINTS)]
        try:
            req = urllib.request.Request(ep, data=urllib.parse.urlencode({"data": q}).encode(),
                                         headers=L.UA)
            els = json.load(urllib.request.urlopen(req, timeout=330))["elements"]
            os.makedirs(CACHE, exist_ok=True)
            json.dump(els, open(path, "w"))
            print(f"{st}: {len(els)} OSM campsites from {ep}", file=sys.stderr)
            return els
        except Exception as e:  # noqa: BLE001 - Overpass 504s under load
            print(f"  {ep}: {e}; retrying", file=sys.stderr)
            time.sleep(10)
    raise SystemExit("overpass unavailable")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    st = ap.parse_args().state.upper()
    els = fetch(st)
    pts = [(*map(float, e["location"].split(",")), e)
           for e in json.load(open("campgrounds.json", encoding="utf-8")) if e.get("location")]
    n = 0
    for el in els:
        t = el.get("tags", {})
        c = el.get("center", el)
        name = t.get("name", "")
        if "lat" not in c or not name:
            continue
        if (t.get("access") in ("private", "no") or t.get("group_only") == "yes"
                or t.get("caravans") == "no" or t.get("backcountry") == "yes"):
            continue
        nt = L.toks(name)
        if any(L.km(c["lat"], c["lon"], la, lo) < 1.5 or
               (L.km(c["lat"], c["lon"], la, lo) < 4 and nt and nt & L.toks(e["name"]))
               for la, lo, e in pts):
            continue
        who = " ".join(t.get(k, "") for k in ("operator", "owner", "operator:type", "ownership")).strip()
        n += 1
        print(f"{el['type'][0]}{el['id']} {c['lat']:.5f},{c['lon']:.5f} {name!r} op={who!r} "
              f"{t.get('website', t.get('contact:website', ''))}")
    print(f"{st}: {len(els)} OSM campsites, {n} named and unmatched", file=sys.stderr)


if __name__ == "__main__":
    main()
