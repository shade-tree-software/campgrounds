#!/usr/bin/env python3
"""Fetch what recreation.gov says about the hookups of the entries in ids.json (2026-10-12).

    set -a; source .env; set +a
    python3 audit/hookups_recheck/scan.py [--limit N]

For each entry: the RIDB facility its website links (`/camping/campgrounds/<id>`), or failing that
the RIDB campground nearest its pin whose name matches; then that facility's record (description,
type, reservable), its campsite catalog run through recgov_hookups.derive (the same rules as the
2026-09-18 fill: site TYPE for electric, explicit per-site Water/Sewer Hookup values, host pads set
aside), and the amenity list recreation.gov shows on the campground page. Written per entry to
scan_2026-10-12.json, so a rerun skips what it holds. Reading the descriptions is done by hand from
that file; nothing here writes campgrounds.json.
"""
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
import recgov_hookups as rh  # noqa: E402

OUT = os.path.join(HERE, "scan_2026-10-12.json")
FAC = re.compile(r"recreation\.gov/camping/campgrounds/(\d+)")
GENERIC = {"campground", "camp", "cg", "the", "recreation", "area", "site", "park", "and", "of",
           "rv", "campgrounds", "family", "national", "forest", "lake", "creek", "river"}


def words(name):
    return set(re.findall(r"[a-z0-9]+", name.lower().replace("'", ""))) - GENERIC


def text(desc):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", desc or ""))).strip()


def nearest(entry):
    """RIDB campgrounds within 3 miles of the pin, best name match first."""
    lat, lng = (float(x) for x in entry["location"].split(","))
    data = rh._get_paced("facilities", {"latitude": lat, "longitude": lng, "radius": 3,
                                        "limit": 50}) or {}
    want = words(entry["name"])
    out = []
    for f in data.get("RECDATA") or []:
        if (f.get("FacilityTypeDescription") or "") != "Campground":
            continue
        have = words(f.get("FacilityName") or "")
        score = len(want & have) / max(1, len(want))
        out.append((score, f["FacilityID"], f.get("FacilityName")))
    out.sort(reverse=True)
    return out


def recgov_amenities(fid):
    """The amenity list on the recreation.gov campground page (keyless; paced, backs off)."""
    req = urllib.request.Request(f"https://www.recreation.gov/api/camps/campgrounds/{fid}",
                                 headers={"User-Agent": "Mozilla/5.0", "accept": "application/json"})
    for wait in (60, 180, None):
        time.sleep(3)
        try:
            cg = json.load(urllib.request.urlopen(req, timeout=30)).get("campground") or {}
            return sorted((cg.get("amenities") or {}).keys())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code != 429 or wait is None:
                raise
            print(f"  429, backing off {wait}s", flush=True)
            time.sleep(wait)


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    ids = json.load(open(os.path.join(HERE, "ids.json"), encoding="utf-8"))["entries"]
    rows = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
    try:
        out = json.load(open(OUT, encoding="utf-8"))
    except FileNotFoundError:
        out = {}
    todo = [i for i in ids if str(i["id"]) not in out][:limit]
    print(len(ids), "entries,", len(out), "scanned, scanning", len(todo), flush=True)
    for n, item in enumerate(todo, 1):
        e = rows[item["id"]]
        rec = {"name": e["name"], "state": e["state"], "held": e.get("hookups"),
               "unsupported": item["unsupported"]}
        m = FAC.search(e.get("website") or "")
        if m:
            fid, how = m.group(1), "linked"
        else:
            cands = nearest(e)
            rec["candidates"] = cands[:5]
            fid, how = (str(cands[0][1]), f"nearest, name score {cands[0][0]:.2f}") if cands and cands[0][0] >= 0.5 else (None, "no RIDB match")
        rec["fid"], rec["match"] = fid, how
        if fid:
            f = rh._get_paced(f"facilities/{fid}", {}) or {}
            rec["facility_name"] = f.get("FacilityName")
            rec["type"] = f.get("FacilityTypeDescription")
            rec["reservable"] = f.get("Reservable")
            rec["description"] = text(f.get("FacilityDescription"))
            sites = [rh.compact_site(s) for s in rh.fetch_campsites(fid)]
            rv = rh.rv_sites(sites)
            rec["sites"] = len(sites)
            rec["rv_site_types"] = sorted({s["type"] for s in rv})
            rec["rv_attrs"] = {a: sorted({s["attrs"].get(a, "") for s in rv})
                               for a in ("Electricity Hookup", "Water Hookup", "Sewer Hookup")}
            rec["catalog"] = rh.derive(sites)
            try:
                rec["amenities"] = recgov_amenities(fid)
            except Exception as ex:  # noqa: BLE001 - recorded, not fatal
                rec["amenities_error"] = str(ex)
        out[str(item["id"])] = rec
        tmp = OUT + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, OUT)
        print(f"  {n}/{len(todo)} {item['id']} {e['name'][:40]} -> {fid} ({how}) {rec.get('catalog')}", flush=True)


if __name__ == "__main__":
    main()
