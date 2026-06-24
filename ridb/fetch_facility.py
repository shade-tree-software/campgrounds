#!/usr/bin/env python3
"""Pull full details for one or more recreation.gov (RIDB) campground facilities.

Reusable for any federal campground in the RIDB catalog. Reads RIDB_API_KEY from
the environment (e.g. `set -a; source .env; set +a` first).

Usage:
    python3 ridb/fetch_facility.py 233187 232462 232463          # by FacilityID
    python3 ridb/fetch_facility.py --search "Aspenglen"          # find a FacilityID by name
    python3 ridb/fetch_facility.py 233187 -o ridb/out.json       # custom output path
    python3 ridb/fetch_facility.py 232463 --available 2026-07-10 2026-07-13  # who's open & fits EKKO

Availability (`--available CHECKIN CHECKOUT`) uses recreation.gov's separate,
undocumented, no-auth calendar API (a sibling of RIDB — RIDB itself carries NO
availability). It only considers EKKO-plausible sites (fits/tight/unknown-length)
and reports which are bookable for EVERY night in [CHECKIN, CHECKOUT) — CHECKOUT
is the departure day, not a night. One request per facility per calendar month.

For each facility it fetches the full facility record (activities, address,
links, media) plus every campsite (paginated), then writes a combined JSON file
and prints a human-readable summary.

RV-fit determination (calibrated against RMNP data quirks):
  - `Max Vehicle Length` is UNRELIABLE in RIDB — sparse and contaminated with
    stray vehicle-*count* values (sites reporting a "max length" of 1-2 ft), so
    we do NOT gate on it.
  - `Driveway Length` is the dense, consistent physical spur length and is the
    field we measure fit on. It's conservative (never shorter than a real
    max-vehicle cap where both exist).
  - A site is RV-capable when CampsiteType starts with "STANDARD" AND its
    PERMITTEDEQUIPMENT lists an RV-class item (RV, trailer, fifth wheel, etc.).
  - A site "fits" EKKO when it's RV-capable AND Driveway Length >= --fit-ft
    (default 25 = 23-ft rig + slack). 23-24 ft is "tight"; missing length is
    reported as "unknown — verify", never silently counted as a fit.
  - The per-facility COVERAGE report prints how often each length field is
    populated, so a campground where even Driveway Length is sparse (making the
    fit count unreliable) is visible rather than silently swallowed.
"""
import argparse
import datetime
import json
import os
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://ridb.recreation.gov/api/v1"
# recreation.gov's (undocumented, no-auth) availability calendar — a SIBLING of
# RIDB, not part of it. Returns one campground's per-site, per-night status for a
# whole month. campground id == RIDB FacilityID for these NPS campgrounds.
AVAIL_URL = "https://www.recreation.gov/api/camps/availability/campground/{cg}/month"

# Equipment names (upper-cased) that mark a site as RV-capable rather than tent-only.
RV_EQUIPMENT = {
    "RV", "RV/MOTORHOME", "TRAILER", "FIFTH WHEEL", "PICKUP CAMPER",
    "CARAVAN/CAMPER VAN", "POP UP",
}
DEFAULT_FIT_FT = 25  # 23-ft EKKO + slack for bumper/hitch and back-in maneuvering


def _get(path, params=None):
    key = os.environ.get("RIDB_API_KEY")
    if not key:
        sys.exit("RIDB_API_KEY not set in environment (source your .env first).")
    url = f"{BASE}/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"apikey": key, "accept": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001 - simple retry on transient errors
            if attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))
    return None


def search_facilities(query):
    data = _get("facilities", {"query": query, "limit": 20, "activity": "CAMPING"})
    return data.get("RECDATA", [])


def fetch_all_campsites(facility_id):
    sites, offset, total = [], 0, None
    while True:
        data = _get(f"facilities/{facility_id}/campsites", {"limit": 50, "offset": offset})
        rec = data.get("RECDATA", [])
        sites.extend(rec)
        total = data.get("METADATA", {}).get("RESULTS", {}).get("TOTAL_COUNT", len(sites))
        offset += len(rec)
        if not rec or offset >= total:
            break
    return sites


def fetch_facility(facility_id):
    facility = _get(f"facilities/{facility_id}", {"full": "true"})
    facility["_campsites"] = fetch_all_campsites(facility_id)
    return facility


def _attr(site, name):
    for a in site.get("ATTRIBUTES", []):
        if a.get("AttributeName", "").lower() == name.lower():
            return a.get("AttributeValue", "")
    return ""


def _num_attr(site, name):
    """Numeric value of an attribute, or None if absent/blank/non-numeric."""
    try:
        return float(_attr(site, name))
    except (TypeError, ValueError):
        return None


def _equip_status(site):
    """Equipment verdict for a STANDARD site: 'rv', 'tent_only', or 'empty'.

    Non-STANDARD sites return 'not_standard'. The 'empty' case (STANDARD type but
    no permitted-equipment list) is a data gap we surface rather than assume —
    a CampsiteType of 'STANDARD' alone is NOT proof of RV capability (at RMNP's
    Moraine Park 143 STANDARD sites are explicitly tent-only by equipment).
    """
    if not site.get("CampsiteType", "").upper().startswith("STANDARD"):
        return "not_standard"
    equip = {e.get("EquipmentName", "").upper() for e in site.get("PERMITTEDEQUIPMENT", [])}
    if not equip:
        return "empty"
    return "rv" if (equip & RV_EQUIPMENT) else "tent_only"


def is_rv_capable(site):
    """Confirmed drive-in RV site: STANDARD type AND an RV-class item permitted."""
    return _equip_status(site) == "rv"


def classify_fit(site, fit_ft):
    """Return one of: 'fits', 'tight', 'too_small', 'unknown', 'not_rv'.

    Fit is judged on Driveway Length only (see module docstring on why
    Max Vehicle Length is not trusted). 'unknown' means RV-plausible but
    unconfirmed — either a STANDARD site with no equipment list, or an
    RV-capable site with no driveway length. Resolve those against the
    campground map; never assume they fit.
    """
    status = _equip_status(site)
    if status in ("not_standard", "tent_only"):
        return "not_rv"
    if status == "empty":
        return "unknown"  # STANDARD but can't confirm RV equipment — verify
    dl = _num_attr(site, "Driveway Length")
    if dl is None or dl <= 0:
        return "unknown"
    if dl >= fit_ft:
        return "fits"
    if dl >= 23:
        return "tight"
    return "too_small"


# ---------------------------------------------------------------------------
# Availability (recreation.gov sibling API — NOT RIDB; no key, browser UA only)
# ---------------------------------------------------------------------------
_AVAIL_CACHE = {}  # (cg_id, year, month) -> {campsite_id: {date_str: status}}


def fetch_availability_month(cg_id, year, month, cache=_AVAIL_CACHE):
    """Return {campsite_id: {'YYYY-MM-DDT00:00:00Z': status}} for a whole month.

    `cache` is the dict used to memoize months. The CLI shares the module-level
    cache (fine for a short run). Long-running callers (the Flask app) should
    pass a per-request dict so availability stays live, never going stale.
    """
    key = (str(cg_id), year, month)
    if cache is not None and key in cache:
        return cache[key]
    start = f"{year:04d}-{month:02d}-01T00:00:00.000Z"
    url = AVAIL_URL.format(cg=cg_id) + "?" + urllib.parse.urlencode({"start_date": start})
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "accept": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.load(r)
            break
        except Exception:  # noqa: BLE001 - simple retry on transient errors
            if attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))
    out = {cid: c.get("availabilities", {}) for cid, c in data.get("campsites", {}).items()}
    if cache is not None:
        cache[key] = out
    return out


def _nights(start, end):
    """List of night dates for check-in START, check-out END (END is not a night)."""
    return [start + datetime.timedelta(days=i) for i in range((end - start).days)]


def availability_matrix(facility, start, end, fit_ft=DEFAULT_FIT_FT, cache=None):
    """Per-night availability for EKKO-friendly sites over an INCLUSIVE range.

    Unlike `report_availability` (booking-oriented, checkout-exclusive,
    full-availability only), this is browse-oriented: every date from `start`
    to `end` INCLUSIVE is treated as a night, and a site is included if it has
    at least ONE available night in the window (partial OR full). Non-EKKO sites
    (tent-only / management / confirmed-too-small) are never included.

    Returns a JSON-serializable dict:
      {
        "nights":  ["YYYY-MM-DD", ...],
        "sites":   [ {id, name, loop, driveway_ft, verdict, statuses,
                      available_nights, total_nights, fully_available}, ... ],
        "fit_ft":  <int>,
        "site_count": <int>,        # EKKO sites with >=1 open night
        "fully_available": <int>,   # subset open EVERY night
      }
    `statuses` parallels `nights`: each is the raw recreation.gov status string
    (e.g. "Available", "Reserved", "NYR", "Not Reservable") or None if the API
    returned nothing for that site/night. Pass a dict as `cache` to memoize the
    month fetches within one request; None (default) fetches fresh each call.
    """
    cg_id = facility.get("FacilityID")
    sites = facility.get("_campsites", [])

    # EKKO-plausible catalog (skip confirmed non-EKKO before touching availability).
    ekko = {}
    for s in sites:
        v = classify_fit(s, fit_ft)
        if v in ("not_rv", "too_small"):
            continue
        ekko[s["CampsiteID"]] = {
            "name": s.get("CampsiteName", "?"),
            "loop": s.get("Loop", "") or "",
            "driveway_ft": _num_attr(s, "Driveway Length"),
            "verdict": v,
        }

    nights = [start + datetime.timedelta(days=i) for i in range((end - start).days + 1)]
    night_keys = [f"{d.isoformat()}T00:00:00Z" for d in nights]

    avail = {}  # campsite_id -> {date_str: status}
    for (yr, mo) in sorted({(d.year, d.month) for d in nights}):
        for cid, days in fetch_availability_month(cg_id, yr, mo, cache=cache).items():
            if cid in ekko:
                avail.setdefault(cid, {}).update(days)

    out_sites = []
    fully = 0
    for cid, info in ekko.items():
        statuses = [avail.get(cid, {}).get(k) for k in night_keys]
        open_n = sum(1 for st in statuses if st == "Available")
        if open_n == 0:
            continue  # no availability at all in window — omit
        full = open_n == len(nights)
        if full:
            fully += 1
        out_sites.append({
            "id": cid,
            "name": info["name"],
            "loop": info["loop"],
            "driveway_ft": info["driveway_ft"],
            "verdict": info["verdict"],
            "statuses": statuses,
            "available_nights": open_n,
            "total_nights": len(nights),
            "fully_available": full,
        })

    # Most-open first; then fit quality; then longer sites; then site name.
    _vrank = {"fits": 0, "tight": 1, "unknown": 2}
    out_sites.sort(key=lambda r: (-r["available_nights"], _vrank.get(r["verdict"], 9),
                                  -(r["driveway_ft"] or 0), r["name"]))
    return {
        "nights": [d.isoformat() for d in nights],
        "sites": out_sites,
        "fit_ft": fit_ft,
        "site_count": len(out_sites),
        "fully_available": fully,
    }


def report_availability(facility, start, end, fit_ft):
    """Print EKKO-friendly campsites bookable for EVERY night in [start, end).

    Only EKKO-plausible sites are considered (fits / tight / unknown-length);
    tent-only, management, and confirmed-too-small sites are never queried.
    """
    cg_id = facility.get("FacilityID")
    name = facility.get("FacilityName", "?")
    sites = facility.get("_campsites", [])

    # 1) EKKO-plausible campsite ids from the catalog, with display info + verdict.
    ekko = {}  # campsite_id -> {name, loop, driveway, verdict}
    for s in sites:
        v = classify_fit(s, fit_ft)
        if v in ("not_rv", "too_small"):
            continue  # explicitly not for EKKO — don't even look at availability
        ekko[s["CampsiteID"]] = {
            "name": s.get("CampsiteName", "?"),
            "loop": s.get("Loop", ""),
            "driveway": _num_attr(s, "Driveway Length"),
            "verdict": v,
        }

    nights = _nights(start, end)
    months = sorted({(d.year, d.month) for d in nights})

    # 2) Pull each needed month once and merge per-campsite night statuses.
    avail = {}  # campsite_id -> {date_str: status}
    for (yr, mo) in months:
        month_data = fetch_availability_month(cg_id, yr, mo)
        for cid, days in month_data.items():
            if cid in ekko:  # only merge EKKO-plausible sites
                avail.setdefault(cid, {}).update(days)

    night_keys = [f"{d.isoformat()}T00:00:00Z" for d in nights]

    # 3) A site is bookable iff EVERY night is 'Available'.
    bookable, blocked, nyr = [], 0, 0
    for cid, info in ekko.items():
        statuses = [avail.get(cid, {}).get(k) for k in night_keys]
        if all(st == "Available" for st in statuses):
            bookable.append((cid, info))
        elif any(st == "NYR" for st in statuses):
            nyr += 1
        elif cid in avail:
            blocked += 1

    rng = f"{start.isoformat()} → {end.isoformat()} ({len(nights)} night{'s' if len(nights) != 1 else ''})"
    print(f"\n=== Availability: {name} (FacilityID {cg_id}) ===")
    print(f"  Range: {rng}   EKKO fit threshold: driveway >= {fit_ft} ft")
    print(f"  EKKO-plausible sites considered: {len(ekko)}  "
          f"(bookable all nights: {len(bookable)}, taken some night: {blocked}, not-yet-released: {nyr})")
    if not bookable:
        print("  No EKKO-friendly site is open for the whole range.")
        return
    bookable.sort(key=lambda x: (x[1]["verdict"] != "fits", -(x[1]["driveway"] or 0)))
    print(f"  {'Site':<10}{'Loop':<22}{'Driveway':<10}{'Fit'}")
    for cid, info in bookable:
        dl = f"{info['driveway']:.0f} ft" if info["driveway"] else "—"
        print(f"  {info['name']:<10}{(info['loop'] or '')[:21]:<22}{dl:<10}{info['verdict']}")


def summarize(facility):
    f = facility
    name = f.get("FacilityName", "?")
    fid = f.get("FacilityID", "?")
    lat, lon = f.get("FacilityLatitude"), f.get("FacilityLongitude")
    sites = f.get("_campsites", [])

    print(f"\n=== {name}  (FacilityID {fid}) ===")
    print(f"  Coords: {lat},{lon}")
    print(f"  Reservable: {f.get('Reservable')}   Type: {f.get('FacilityTypeDescription')}")
    if f.get("FacilityPhone"):
        print(f"  Phone: {f.get('FacilityPhone')}")
    if f.get("FacilityEmail"):
        print(f"  Email: {f.get('FacilityEmail')}")

    # Reservation / official link
    for link in f.get("LINK", []):
        if link.get("LinkType") in ("Official Web Site", "Reservation"):
            print(f"  {link.get('LinkType')}: {link.get('URL')}")

    # Address
    for addr in f.get("FACILITYADDRESS", []):
        city = addr.get("City", "")
        state = addr.get("AddressStateCode", "")
        print(f"  Address: {addr.get('StreetAddress1','')} {city}, {state} {addr.get('PostalCode','')}".strip())

    fit_ft = getattr(summarize, "fit_ft", DEFAULT_FIT_FT)

    # Site breakdown by type
    type_counts = {}
    for s in sites:
        st = s.get("CampsiteType", "?")
        type_counts[st] = type_counts.get(st, 0) + 1

    # RV-fit classification (Driveway Length based — see module docstring)
    fit_counts = {"fits": 0, "tight": 0, "too_small": 0, "unknown": 0, "not_rv": 0}
    rv_driveways = []
    for s in sites:
        verdict = classify_fit(s, fit_ft)
        fit_counts[verdict] += 1
        if is_rv_capable(s):
            dl = _num_attr(s, "Driveway Length")
            if dl and dl > 0:
                rv_driveways.append(dl)
    rv_confirmed = sum(1 for s in sites if is_rv_capable(s))
    empty_equip = sum(1 for s in sites if _equip_status(s) == "empty")

    hdr = f"  Campsites: {len(sites)} total  ({rv_confirmed} RV-capable"
    if empty_equip:
        hdr += f", +{empty_equip} STANDARD w/ no equipment list — verify"
    print(hdr + ")")
    print(f"    By type: " + ", ".join(f"{k}={v}" for k, v in sorted(type_counts.items())))
    print(f"    EKKO fit (RV-capable, Driveway Length >= {fit_ft} ft):")
    print(f"      fits>={fit_ft}ft={fit_counts['fits']}  tight(23-{fit_ft-1})={fit_counts['tight']}"
          f"  too_small(<23)={fit_counts['too_small']}  unknown(verify)={fit_counts['unknown']}")
    if rv_driveways:
        rv_driveways.sort()
        print(f"      RV driveway lengths (ft): min={rv_driveways[0]:.0f} "
              f"median={rv_driveways[len(rv_driveways)//2]:.0f} max={rv_driveways[-1]:.0f}")

    # Per-facility field-coverage report — exposes sparsity so a low fit count
    # driven by missing data (not by short sites) is visible, not silent.
    rv_sites = [s for s in sites if is_rv_capable(s)]
    print(f"    Length-field coverage (populated / {len(rv_sites)} RV-capable sites):")
    for fl in ("Driveway Length", "Max Vehicle Length", "Site Length"):
        have = sum(1 for s in rv_sites if (_num_attr(s, fl) or 0) > 0)
        pct = (100 * have / len(rv_sites)) if rv_sites else 0
        flag = "  <-- sparse, fit count unreliable" if (fl == "Driveway Length" and pct < 80) else ""
        print(f"      {fl:20s} {have:3d}/{len(rv_sites):<3d} ({pct:3.0f}%){flag}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("facility_ids", nargs="*", help="RIDB FacilityID(s)")
    ap.add_argument("--search", help="Search facilities by name and exit")
    ap.add_argument("-o", "--output", default="ridb/facilities.json", help="Output JSON path")
    ap.add_argument("--fit-ft", type=int, default=DEFAULT_FIT_FT,
                    help=f"Driveway-length threshold (ft) for an EKKO fit (default {DEFAULT_FIT_FT})")
    ap.add_argument("--available", nargs=2, metavar=("CHECKIN", "CHECKOUT"),
                    help="Check-in/check-out dates (YYYY-MM-DD). Reports EKKO-friendly "
                         "sites bookable for every night in the range.")
    args = ap.parse_args()
    summarize.fit_ft = args.fit_ft

    if args.search:
        for f in search_facilities(args.search):
            print(f"{f['FacilityID']} | {f['FacilityName']} | {f.get('FacilityTypeDescription')}")
        return

    if not args.facility_ids:
        ap.error("provide one or more FacilityIDs, or use --search")

    start = end = None
    if args.available:
        try:
            start = datetime.date.fromisoformat(args.available[0])
            end = datetime.date.fromisoformat(args.available[1])
        except ValueError:
            ap.error("--available dates must be YYYY-MM-DD")
        if end <= start:
            ap.error("CHECKOUT must be after CHECKIN (need at least one night)")

    out = {}
    for fid in args.facility_ids:
        print(f"Fetching {fid} ...", file=sys.stderr)
        fac = fetch_facility(fid)
        out[fid] = fac
        summarize(fac)
        if args.available:
            report_availability(fac, start, end, args.fit_ft)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(out)} facility record(s) to {args.output}")


if __name__ == "__main__":
    main()
