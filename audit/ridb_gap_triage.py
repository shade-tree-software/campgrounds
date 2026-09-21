#!/usr/bin/env python3
"""Triage the RIDB federal gap list against RIDB's own per-campsite catalog.

    python3 audit/ridb_gap_triage.py --fetch [--limit N]   # RIDB -> cache
    python3 audit/ridb_gap_triage.py --report              # free, from cache
    python3 audit/ridb_gap_triage.py --write <out.json>    # the work list

`audit/ridb_gap_2026-09-21.json` is 585 RIDB campgrounds with no entry in
`campgrounds.json`, and its own notes say a sample of 60 split roughly a third
real RV campground / a third tent-cabin-boat-in / a third no catalog at all.
Deciding which is which by hand is the expensive part, and the catalog answers
it mechanically for most of them, so this runs FIRST and hands the sweep a list
already sorted by whether there is anything to sweep.

It reads two endpoints per facility, neither of which is the availability
CALENDAR (that one is rate-limited in minutes and is nobody's business here):

  facilities/<id>?full=true   name, agency, real state, phone, fee, description
  facilities/<id>/campsites   the per-site catalog the RV test reads

**The state in the gap file is inferred from the nearest DB entry and is wrong
wherever RIDB's coordinates are** (the `coord_suspect` rows: Big Reservoir is
Tahoe NF in California and RIDB puts it in the Pacific off Baja). The facility
record's mailing `AddressStateCode` is the real answer, and the campsites carry
their own coordinates, so a suspect pin can be re-derived from the sites.

Chunked and resumable like every other bulk pass here: `--limit` caps a run,
SIGINT finishes the facility in flight, and the cache is written after every
facility, so a kill costs one. Progress lives in the cache keyed by facility
id, not in a cursor file.

**Absent is never "no".** A facility with no catalog is unknown, not a
campground without RV sites — plenty of FCFS federal campgrounds publish no
per-site data at all. Those are held for a human, never dropped.
"""

import argparse
import json
import os
import re
import signal
import sys
import time
import urllib.error
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ridb.fetch_facility import _get, RV_EQUIPMENT, DEFAULT_FIT_FT  # noqa: E402
from recgov_hookups import HOST_NAME, MIN_CATALOG_SITES     # noqa: E402

GAP_JSON = os.path.join("audit", "ridb_gap_2026-09-21.json")
CAMPGROUNDS_JSON = "campgrounds.json"
# Gitignored and regenerable. Deliberately NOT recgov_hookups' own
# `ridb_campsites.json`: that cache is the hookups pass's progress record and
# this run has no business rewriting entries it did not fetch for that purpose.
CACHE_JSON = os.path.join("trip_data", "ridb_gap_cache.json")

# v2 keeps EVERY campsite attribute rather than recgov_hookups' six. That pass
# caches 12k facilities and has to stay small; this one caches 585 and has to
# answer questions not yet asked — the waterfront gate counts a rec.gov
# per-site "SHORELINE SITE" flag as evidence, and a keep-list written before
# meeting one would drop it silently on the facilities that publish it.
CACHE_VERSION = 2

# RIDB answers 50 requests a minute on a key. Same pacing recgov_hookups uses,
# and for the same reason: a burst is held against you long after it ends.
PAUSE_S = 1.5
BACKOFF_S = (60, 180, 420)

_stop = False


def _on_sigint(signum, frame):
    global _stop
    if _stop:
        raise KeyboardInterrupt
    _stop = True
    print("\n  SIGINT — finishing this facility, then writing the cache.", flush=True)


# ── Fetch ───────────────────────────────────────────────────────────────────

def load_cache():
    try:
        with open(CACHE_JSON, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}


def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_JSON), exist_ok=True)
    tmp = CACHE_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(cache, fh, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, CACHE_JSON)


def _get_paced(path, params=None):
    for wait in BACKOFF_S + (None,):
        time.sleep(PAUSE_S)
        try:
            return _get(path, params)
        except urllib.error.HTTPError as e:
            if e.code in (404, 400):
                return None
            if e.code != 429 or wait is None:
                raise
            print(f"  429 — backing off {wait}s", flush=True)
            time.sleep(wait)
    return None


def _strip_html(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def compact_site(site):
    """One RIDB campsite, keeping every attribute it carries.

    Deliberately NOT recgov_hookups.compact_site: that one keeps six
    attributes because it caches the whole federal catalog and has to stay a
    few MB. Here the set is 585 facilities, so the cache can afford to hold
    what a later stage might need — site length, shade, driveway surface, and
    any waterfront flag.
    """
    attrs = {}
    for a in site.get("ATTRIBUTES") or []:
        name = (a.get("AttributeName") or "").strip()
        if name:
            attrs[name] = (a.get("AttributeValue") or "").strip()
    return {
        "id": str(site.get("CampsiteID") or ""),
        "name": (site.get("CampsiteName") or "").strip(),
        "reservable": bool(site.get("CampsiteReservable")),
        "type": (site.get("CampsiteType") or "").strip().upper(),
        "loop": (site.get("Loop") or "").strip(),
        "lat": site.get("CampsiteLatitude"),
        "lng": site.get("CampsiteLongitude"),
        "equip": sorted({(e.get("EquipmentName") or "").strip().upper()
                         for e in site.get("PERMITTEDEQUIPMENT") or []} - {""}),
        "attrs": attrs,
    }


def compact_facility(f):
    """The part of one RIDB facility record this triage and a later add read."""
    addr = (f.get("FACILITYADDRESS") or [{}])[0]
    org = (f.get("ORGANIZATION") or [{}])[0]
    rec = (f.get("RECAREA") or [{}])[0]
    return {
        "name": (f.get("FacilityName") or "").strip(),
        "state": (addr.get("AddressStateCode") or "").strip().upper(),
        "city": (addr.get("City") or "").strip(),
        "lat": f.get("FacilityLatitude"),
        "lng": f.get("FacilityLongitude"),
        "phone": (f.get("FacilityPhone") or "").strip(),
        "email": (f.get("FacilityEmail") or "").strip(),
        "type": (f.get("FacilityTypeDescription") or "").strip(),
        "reservable": bool(f.get("Reservable")),
        "enabled": bool(f.get("Enabled")),
        "org": (org.get("OrgAbbrevName") or "").strip(),
        "org_name": (org.get("OrgName") or "").strip(),
        "recarea": (rec.get("RecAreaName") or "").strip(),
        "map_url": (f.get("FacilityMapURL") or "").strip(),
        "reservation_url": (f.get("FacilityReservationURL") or "").strip(),
        "description": _strip_html(f.get("FacilityDescription"))[:1500],
        "fee": _strip_html(f.get("FacilityUseFeeDescription"))[:600],
        "directions": _strip_html(f.get("FacilityDirections"))[:600],
        "stay_limit": (f.get("StayLimit") or "").strip(),
    }


def fetch_campsites(fid, passes=2):
    """Every campsite of a facility, de-duplicated by CampsiteID.

    RIDB's offset paging is not stable across pages (recgov_hookups documents
    the 43-of-717 case), so a multi-page facility is re-read until the union
    reaches TOTAL_COUNT. Two passes is enough for a count; the hookups pass,
    which needs every individual site, uses four.
    """
    by_id, total = {}, 0
    for _ in range(passes):
        offset = 0
        while True:
            data = _get_paced(f"facilities/{fid}/campsites",
                              {"limit": 50, "offset": offset}) or {}
            rec = data.get("RECDATA") or []
            for site in rec:
                by_id.setdefault(str(site.get("CampsiteID")), site)
            total = (data.get("METADATA") or {}).get("RESULTS", {}).get(
                "TOTAL_COUNT", len(by_id))
            offset += len(rec)
            if not rec or offset >= total:
                break
        if len(by_id) >= total:
            break
    return list(by_id.values()), total


def site_coords(sites):
    """The campsites' own coordinates, which a corrupt facility pin lacks."""
    pts = [(s.get("CampsiteLatitude"), s.get("CampsiteLongitude")) for s in sites]
    pts = [(a, b) for a, b in pts if isinstance(a, (int, float))
           and isinstance(b, (int, float)) and (a or b)]
    if not pts:
        return None
    lat = sorted(p[0] for p in pts)[len(pts) // 2]
    lng = sorted(p[1] for p in pts)[len(pts) // 2]
    return [round(lat, 6), round(lng, 6)]


def run_fetch(rows, limit):
    cache = load_cache()
    todo = [r for r in rows
            if cache.get(r["facility_id"], {}).get("v") != CACHE_VERSION]
    cached = len(rows) - len(todo)
    if limit:
        todo = todo[:limit]
    print(f"{len(todo)} to fetch this run; {cached} already cached, "
          f"{len(rows) - cached - len(todo)} left after it", flush=True)
    signal.signal(signal.SIGINT, _on_sigint)
    done = 0
    for row in todo:
        fid = row["facility_id"]
        try:
            raw = _get_paced(f"facilities/{fid}", {"full": "true"})
            if raw is None:
                cache[fid] = {"v": CACHE_VERSION, "gone": True}
            else:
                sites, total = fetch_campsites(fid)
                cache[fid] = {
                    "v": CACHE_VERSION,
                    "facility": compact_facility(raw),
                    "sites": [compact_site(s) for s in sites],
                    "site_total": total,
                    "site_coord": site_coords(sites),
                }
        except Exception as e:  # noqa: BLE001 — a bad facility must not end the run
            print(f"  {fid} {row['name']}: {e}", flush=True)
            cache[fid] = {"v": CACHE_VERSION, "error": str(e)[:200]}
        save_cache(cache)
        done += 1
        if done % 10 == 0:
            print(f"  {done}/{len(todo)}", flush=True)
        if _stop:
            break
    print(f"fetched {done}", flush=True)


# ── Triage ──────────────────────────────────────────────────────────────────

def rv_sites(sites):
    """The sites an RV family could book — the same test recgov_hookups uses."""
    out = []
    for site in sites:
        t = site.get("type") or ""
        if not (t.startswith("STANDARD") or t.startswith("RV")):
            continue
        if HOST_NAME.search(site.get("name") or ""):
            continue
        equip = set(site.get("equip") or [])
        if equip and not equip & RV_EQUIPMENT:
            continue
        out.append(site)
    return out


def _site_ft(site):
    """The longest rig one catalog site claims to take.

    Two attributes say it and they disagree as often as not, so take the
    larger: Driveway Length is the pad and Max Vehicle Length is the rule,
    and a site is usable if EITHER clears the rig.
    """
    best = 0
    for key in ("Max Vehicle Length", "Driveway Length"):
        raw = (site.get("attrs") or {}).get(key) or ""
        m = re.search(r"\d+", raw)
        if m:
            best = max(best, int(m.group()))
    return best


def fit_summary(rv):
    """How many catalog sites take EKKO, which is the inclusion size gate.

    The gate is "at least some drive-in sites fit a 23-ft rig", and a site
    that publishes no length is unknown rather than too small, so it is
    counted apart and never held against the campground.
    """
    lengths = [_site_ft(s) for s in rv]
    stated = [n for n in lengths if n]
    return {
        "max_ft": max(stated) if stated else None,
        "fit_sites": sum(1 for n in stated if n >= DEFAULT_FIT_FT),
        "stated": len(stated),
        "unstated": len(lengths) - len(stated),
    }


def classify(rec):
    """One facility's verdict, plus the reason a human can check it against.

    Five classes, and only ONE of them is a drop:
      likely_rv   3+ bookable RV-capable sites — the work list
      no_rv       a real PUBLIC catalog with no RV site in it — tent, cabin,
                  equestrian or boat-in, the case the name filter missed
      thin        a catalog too small to mean anything (MIN_CATALOG_SITES);
                  in practice a lone group picnic shelter at a day-use park
      mgmt_only   a catalog that is all MANAGEMENT records — the agency's own
                  internal rows, which say nothing about what the public can
                  book. Houston Recreation Area lists 75 of them and not one
                  public site; reading that as "no RV sites" would drop a
                  campground on the strength of a catalog that never described
                  it. Unknown, like an absent catalog.
      no_catalog  no per-site data at all — unknown, NOT a no
    """
    if rec.get("gone"):
        return "gone", "RIDB 404 — facility withdrawn"
    if rec.get("error"):
        return "error", rec["error"]
    sites = rec.get("sites") or []
    rv = rv_sites(sites)
    if not sites:
        return "no_catalog", "no per-site catalog (FCFS or undocumented)"
    kinds = Counter(s.get("type") or "?" for s in sites)
    breakdown = ", ".join(f"{n}x {k.title()}" for k, n in kinds.most_common(4))
    if len(rv) >= MIN_CATALOG_SITES:
        res = sum(1 for s in rv if s.get("reservable"))
        return "likely_rv", f"{len(rv)} RV sites ({res} bookable) of {len(sites)}: {breakdown}"
    public = [s for s in sites if not (s.get("type") or "").startswith("MANAGEMENT")]
    if len(public) < MIN_CATALOG_SITES and len(sites) >= MIN_CATALOG_SITES:
        return "mgmt_only", f"{len(sites)} sites, {len(public)} public: {breakdown}"
    if len(public) >= MIN_CATALOG_SITES and not rv:
        return "no_rv", f"0 RV sites of {len(sites)}: {breakdown}"
    return "thin", f"{len(rv)} RV sites of {len(sites)}: {breakdown}"


def _haversine_km(a_lat, a_lng, b_lat, b_lng):
    from math import asin, cos, radians, sin, sqrt
    dlat = radians(b_lat - a_lat)
    dlng = radians(b_lng - a_lng)
    h = (sin(dlat / 2) ** 2
         + cos(radians(a_lat)) * cos(radians(b_lat)) * sin(dlng / 2) ** 2)
    return 2 * 6371.0088 * asin(sqrt(h))


def db_points():
    """Every campground entry's coordinate, for the near-duplicate flag."""
    try:
        with open(CAMPGROUNDS_JSON, encoding="utf-8") as fh:
            entries = json.load(fh)
    except FileNotFoundError:
        return []
    pts = []
    for e in entries:
        if e.get("kind") != "campground":
            continue
        try:
            lat, lng = (float(x) for x in (e.get("location") or "").split(","))
        except ValueError:
            continue
        pts.append((lat, lng, e.get("name") or "", e.get("id")))
    return pts


def nearest_db(lat, lng, pts):
    """The closest existing entry, which is how a duplicate shows itself.

    The gap list deduped at 3 km plus a same-name test at 50 km, so what
    survives near an existing entry is either a genuinely separate campground
    on the same lake or the SAME camping under another name — RIDB lists
    Caesar Creek Lake as a USACE facility for a lake whose campground is the
    state park already in the database. Neither this nor the gap file's own
    filter can tell those apart, so it is flagged for a human, never dropped.
    """
    if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
        return None
    best = None
    for p_lat, p_lng, name, cid in pts:
        if abs(p_lat - lat) > 0.25 or abs(p_lng - lng) > 0.35:
            continue
        km = _haversine_km(lat, lng, p_lat, p_lng)
        if best is None or km < best[0]:
            best = (km, name, cid)
    if best is None:
        return None
    return {"km": round(best[0], 2), "name": best[1], "id": best[2]}


def build(rows, cache):
    pts = db_points()
    out = []
    for row in rows:
        rec = cache.get(row["facility_id"])
        if not rec:
            continue
        cls, why = classify(rec)
        fac = rec.get("facility") or {}
        item = {
            "facility_id": row["facility_id"],
            "name": fac.get("name") or row["name"],
            "verdict": cls,
            "why": why,
            "state": fac.get("state") or row.get("state") or "?",
            "gap_state": row.get("state"),
            "agency": fac.get("org"),
            "recarea": fac.get("recarea"),
            "city": fac.get("city"),
            "lat": fac.get("lat"),
            "lng": fac.get("lng"),
            "reservable": fac.get("reservable"),
            "url": row["url"],
        }
        near = nearest_db(fac.get("lat"), fac.get("lng"), pts)
        if near and near["km"] <= 8:
            item["nearest_db"] = near
        if row.get("coord_suspect"):
            item["coord_suspect"] = True
            if rec.get("site_coord"):
                item["site_coord"] = rec["site_coord"]
        if fac.get("phone"):
            item["phone"] = fac["phone"]
        if cls == "likely_rv":
            item["fit"] = fit_summary(rv_sites(rec.get("sites") or []))
            item["site_total"] = rec.get("site_total")
        out.append(item)
    return out


def report(items):
    by = defaultdict(list)
    for it in items:
        by[it["verdict"]].append(it)
    order = ["likely_rv", "no_catalog", "mgmt_only", "thin", "no_rv",
             "gone", "error"]
    print(f"{len(items)} triaged\n")
    for cls in order:
        got = by.get(cls) or []
        if not got:
            continue
        print(f"{cls:<12} {len(got):>4}")
    print("\nlikely_rv by state:")
    st = Counter(i["state"] for i in by.get("likely_rv", []))
    print("  " + "  ".join(f"{k}:{v}" for k, v in st.most_common()))
    print("\nlikely_rv by agency:")
    ag = Counter(i["agency"] or "?" for i in by.get("likely_rv", []))
    print("  " + "  ".join(f"{k}:{v}" for k, v in ag.most_common()))
    moved = [i for i in items if i.get("gap_state") not in (i["state"], None)]
    print(f"\nstate corrected from RIDB on {len(moved)} rows")
    lr = by.get("likely_rv", [])
    no_fit = [i for i in lr if i.get("fit", {}).get("stated")
              and not i["fit"]["fit_sites"]]
    unknown_fit = [i for i in lr if not i.get("fit", {}).get("stated")]
    print(f"{len(no_fit)} likely_rv rows state lengths but none reach "
          f"{DEFAULT_FIT_FT} ft (size gate excludes them); "
          f"{len(unknown_fit)} state no length at all (unknown, check by hand)")
    dup = [i for i in by.get("likely_rv", []) if i.get("nearest_db")]
    print(f"{len(dup)} likely_rv rows sit within 8 km of an existing entry "
          f"(possible duplicate — check by hand)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--write", metavar="OUT")
    args = ap.parse_args()

    with open(GAP_JSON, encoding="utf-8") as fh:
        rows = json.load(fh)["rows"]

    if args.fetch:
        run_fetch(rows, args.limit)

    cache = load_cache()
    items = build(rows, cache)
    if args.report or args.fetch:
        report(items)
    if args.write:
        payload = {
            "generated": time.strftime("%Y-%m-%d"),
            "source": GAP_JSON,
            "method": ("RIDB facility record + per-campsite catalog per gap row; "
                       "verdict from the RV-site test of recgov_hookups.rv_sites"),
            "count": len(items),
            "rows": items,
        }
        with open(args.write, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        print(f"wrote {args.write}")


if __name__ == "__main__":
    main()
