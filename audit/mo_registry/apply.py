#!/usr/bin/env python3
"""Missouri's two state camping agencies in the policy registry (2026-10-12).

    python3 -I audit/mo_registry/apply.py [--apply]

Missouri's 275 `state` entries are two agencies: 40 Missouri State Parks (DNR) and 235
Department of Conservation areas. `state:MO` is the parks row, reached by ownership+state as
usual; the conservation areas get `policy_ref: state:missouri-conservation-areas`, the way the
Michigan state forests and Washington DNR campgrounds name their own rows.

Because an explicit ref still merges with `state:MO` field by field (campground_schema
`_inherited`), the parks row keeps its reservation fee and hookup surcharges in its note and on
the 40 park entries rather than as row fields: as fields they would surface under "Typical for
Missouri Conservation Areas" on campgrounds where camping is free and nothing is booked. The
parks row's booking keys and discounts are already dropped there by the entries' own
`reservable: false` and $0 fees (`_moot_agency_keys`).

Entry edits: the 2026 rates per park (build.py, from the agency's rate charts), the weekend
two-night minimum on the seven parks the agency names, Battle of Athens' reservable season
(its note said it was not on the reservation system), and the off-season first-come rules
at Graham Cave and Watkins Mill. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import campground_schema as cs  # noqa: E402
import build  # noqa: E402

CHECKED = "2026-10-12"
MDC_REF = "state:missouri-conservation-areas"
MSP = "https://mostateparks.com"

ROWS = {
    "state:MO": {
        "booking": {
            "reservable": True,
            "platform": "usedirect",
            "url": "https://icampmo.usedirect.com/MSPWeb/",
            "window_opens_days": 365,
            "reserve_until": {"relative_to": "arrival", "at": "19:00"},
            "fcfs": "after_cutoff",
            "max_stay_nights": 15,
            "note": "Missouri State Parks (DNR). Reservations open 'at 7 a.m. CT 12 months prior to the first day of your trip' (the same 12 months is on 39 of the 40 park camping pages read) and can be made 'up to 7 p.m. the day of arrival', online or at 877-422-6766. 39 parks and historic sites take reservations, and each 'allows all campsites to be reserved during their reservable season'; 'Campsites that are not reserved remain available for walk-up registration' (36 of the 40 park pages say the same), so fcfs is after_cutoff: there are no walk-up-only loops. Exceptions: Battle of Athens is reservable only Apr 15-Oct 31 and walk-up only otherwise, Graham Cave is all first-come November-March, and Watkins Mill keeps sites 1-34, 98 and 99 walk-in only in the off-season; Prairie and Taum Sauk Mountain are not on the reservation list. No agency-wide minimum stay: 'A two-night minimum stay on the weekend (Friday and Saturday or Saturday and Sunday) is required at Big Lake, Lake of the Ozarks, St. Joe, Mark Twain, Wakonda, Wallace and Watkins Mill state parks' - those seven entries carry it themselves - and Bennett Spring's page says it has 'no minimum stay requirement'. max_stay_nights: 'Camping is limited to any 15 days within a 30-consecutive-day period at any one park.' Check-in 3 p.m., checkout 2 p.m.; a site not claimed within the first 24 hours of the stay (3 p.m. to 3 p.m.) is resold. Changes until 7 p.m. the day before arrival ($5.25); cancelling 1-30 days out costs $10 plus the reservation fee, 31 or more days out only the reservation fee.",
        },
        "fees": {
            "nightly_low": 8,
            "nightly_high": 17,
            "currency": "USD",
            "checked": "2026",
            "note": "Base (basic-site) rates from the 2026 rate charts: $15 a night in the on-season at most parks ($16 at Long Branch, Roaring River, Table Rock and Lake Wappapello's Asher Creek loop) and $14 in the off-season. The on-season runs Apr 1-Oct 31, from Feb 25 at Roaring River, Bennett Spring and Montauk, from Apr 15 at some northern parks, and March-November at Table Rock. Nine 'value camping' parks charge less on weeknights (Graham Cave, Lake Wappapello, Pomme de Terre, Robertsville, Stockton, Truman, Mark Twain, Van Meter and Washington), so the range runs from $8 (Stockton, off-season) to $17 (Truman's holiday weekends). Hookup sites at most parks, on-season: 30-amp electric $27, 50-amp $29, electric/water 50-amp $32, sewer/electric/water 50-amp $35 (off-season $23/$25/$26/$29); 'Camping rates are charged on the basis of available utilities, whether used or not.' Advance reservations add a nonrefundable fee per site: $6.50 online, $8 by phone. Each of the 40 park entries carries its own 2026 figures, surcharges and reservation fee; they are not row fields here because the conservation-area row inherits this one field by field. No non-resident rate: one price list for everyone. No entrance fee: 'admission to all Missouri state parks and historic sites is free' (DNR news release, May 18, 2026).",
        },
        "discounts": {
            "military": True,
            "note": "'A $2 per night camping discount is available year-round for senior citizens (65 years and older), people with disabilities, current and former military personnel, and family members of active-duty military personnel', asked for when paying, with ID shown at check-in; veterans count. The America the Beautiful Senior Pass is NOT accepted as proof of age ('issued at age 62 ... please provide proof other than these two federal passes'), while the Access Pass IS accepted as proof of disability - so interagency_senior_access stays absent: either way the discount is Missouri's own $2, not a federal one.",
        },
        "provenance": {
            "booking": {"source": f"{MSP}/activity/camping/reservation-system, {MSP}/activity/camping, {MSP}/page/reservation-faqs, {MSP}/activity/camping/rules-regulation and the 40 park camping pages", "checked": CHECKED, "method": "manual"},
            "fees": {"source": f"{MSP}/activity/camping/camping-fees and its 2026 on- and off-season rate charts (2026rates_on-seasonchart.pdf, 2026rates_offseasonchart.pdf); free admission: DNR news release 2026-05-18 (dnr.mo.gov/communications/news/missouri-state-parks-honors-military-service-1)", "checked": CHECKED, "method": "manual"},
            "discounts": {"source": f"{MSP}/activity/camping/camping-fees", "checked": CHECKED, "method": "manual"},
        },
    },
    MDC_REF: {
        "booking": {
            "reservable": False,
            "platform": "none",
            "fcfs": "always",
            "max_stay_nights": 14,
            "note": "Missouri Department of Conservation areas: 'All camping on conservation areas is free, and most camping is first come, first served. Be sure to have a backup plan in case the spot where you want to camp is already occupied.' 'Most', because 'Some areas require a special use permit for all camping' and some allow camping only in designated sites - read the area's own page - and 'some areas expand or restrict camping during firearm hunting seasons'. The Wildlife Code (3 CSR 10-11.140) limits a stay to 'fourteen (14) consecutive days in any thirty- (30-) day period' and each camper to 30 camping days a calendar year on all department land; two camping or sleeping units per established site (one at Thomas Hill Reservoir); quiet hours 10 p.m.-6 a.m., with visitors out of the campground by 10 p.m.; groups of more than ten need a special use permit.",
        },
        "fees": {
            "nightly_low": 0,
            "nightly_high": 0,
            "currency": "USD",
            "checked": "2026",
            "note": "'All camping on conservation areas is free.' Little is provided for it: 'no RV hookups are provided at any department area. Campers should expect to bring their own water.' Designated campgrounds may have fire rings, tables, dumpsters and latrines, but most conservation-area camping is primitive.",
        },
        "provenance": {
            "booking": {"source": "https://mdc.mo.gov/discover-nature/activities/camping and 3 CSR 10-11.140 (https://www.sos.mo.gov/cmsimages/adrules/csr/current/3csr/3c10-11.pdf)", "checked": CHECKED, "method": "manual"},
            "fees": {"source": "https://mdc.mo.gov/discover-nature/activities/camping", "checked": CHECKED, "method": "manual"},
        },
    },
}

WEEKEND_MIN = "'For weekend reservations, there is a required two-night minimum stay of Friday/Saturday or Saturday/Sunday.'"
BOOKING = {   # id -> (booking update, the park page it was read on)
    1827: ({"min_stay": [{"nights": 2, "applies": "weekend"}], "note": WEEKEND_MIN}, "park/big-lake/camping"),
    1839: ({"min_stay": [{"nights": 2, "applies": "weekend"}], "note": WEEKEND_MIN}, "park/lake-ozarks/camping"),
    1841: ({"min_stay": [{"nights": 2, "applies": "weekend"}], "note": WEEKEND_MIN}, "park/mark-twain-state-park/camping"),
    1852: ({"min_stay": [{"nights": 2, "applies": "weekend"}], "note": WEEKEND_MIN}, "park/st-joe-state-park/camping"),
    1858: ({"min_stay": [{"nights": 2, "applies": "weekend"}], "note": WEEKEND_MIN}, "park/wakonda-state-park/camping"),
    1859: ({"min_stay": [{"nights": 2, "applies": "weekend"}], "note": WEEKEND_MIN}, "park/wallace-state-park/camping"),
    1860: ({"min_stay": [{"nights": 2, "applies": "weekend"}], "note": WEEKEND_MIN + " 'All campsites are reservable during on-season. During the off-season, sites 1-34, 98, and 99 are available for walk-in users only.'"}, "park/watkins-mill-state-park/camping"),
    1833: ({"note": "'During the off-season (November through March), all sites are first-come, first-serve.'"}, "park/graham-cave/camping"),
    1825: ({"reservable": True, "fcfs": "after_cutoff", "note": "'The campground is fully reservable during the on-season (April 15 through Oct. 31). During the off-season, sites are available on walk-up registration basis only.'"}, "parks/battle-of-athens-hs/camping"),
}
NOTE_FIX = {1825: ("~29-site FCFS campground", "~29-site campground",
                   "walk-up registration, not on the reservation system.",
                   "reservable on the state system Apr 15-Oct 31, walk-up only the rest of the year (park page, 2026-10-12).")}


def main():
    apply = "--apply" in sys.argv
    reg_path = os.path.join(ROOT, "campground_policies.json")
    reg = json.load(open(reg_path, encoding="utf-8"))
    added = [k for k in ROWS if k not in reg]
    for k in added:
        reg[k] = ROWS[k]
    cg_path = os.path.join(ROOT, "campgrounds.json")
    rows = json.load(open(cg_path, encoding="utf-8"))
    by = {r["id"]: r for r in rows}
    n_ref = n_fee = n_book = 0
    for r in rows:
        if r.get("state") == "MO" and r.get("ownership") == "state" and "mdc.mo.gov" in (r.get("website") or "") \
                and r.get(cs.POLICY_REF) != MDC_REF:
            cs.apply_update(r, {cs.POLICY_REF: MDC_REF})
            n_ref += 1
    for p in build.build():
        e = by[p["id"]]
        fees = dict(p["fees"])
        fees["reservation_fee"] = 6.5
        for k in ("nightly_low", "nightly_high"):
            fees[k] = int(fees[k]) if float(fees[k]).is_integer() else fees[k]
        if fees.get("surcharges"):
            fees["surcharges"] = {k: int(v) if float(v).is_integer() else v for k, v in fees["surcharges"].items()}
        if e.get("fees") == fees:
            continue
        prov = dict(e.get(cs.PROVENANCE) or {})
        prov["fees"] = {"source": f"Missouri State Parks 2026 on- and off-season rate charts, {MSP}/activity/camping/camping-fees", "checked": CHECKED, "method": "derived"}
        e.pop("fees", None)
        cs.apply_update(e, {"fees": fees, cs.PROVENANCE: prov})
        n_fee += 1
    for i, (upd, page) in BOOKING.items():
        e = by[i]
        if all((e.get("booking") or {}).get(k) == v for k, v in upd.items()):
            continue
        prov = dict(e.get(cs.PROVENANCE) or {})
        prov["booking"] = {"source": f"{MSP}/{page} and {MSP}/activity/camping", "checked": CHECKED, "method": "manual"}
        cs.apply_update(e, {"booking": upd, cs.PROVENANCE: prov})
        n_book += 1
    for i, (a, b, c, d) in NOTE_FIX.items():
        note = by[i]["note"]
        if c in note:
            by[i]["note"] = note.replace(a, b).replace(c, d)
            print("note fixed:", i)
    for r in rows:
        if r.get("state") == "MO":
            cs.validate_row(r, label=r["name"])
    print(f"rows added {added}; policy_ref set on {n_ref}; fees on {n_fee}; booking on {n_book}",
          "(written)" if apply else "(dry run)")
    if apply:
        for path, data, ind in ((reg_path, reg, 2), (cg_path, rows, 2)):
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=ind, ensure_ascii=False)
                fh.write("\n")
            os.replace(tmp, path)


if __name__ == "__main__":
    main()
