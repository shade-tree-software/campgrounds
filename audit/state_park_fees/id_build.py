"""Idaho State Parks findings, read 2026-10-12 (texts in id_fee_pages_2026-10-12.txt).

    python3 -I id_build.py OUT

Idaho prices campsites by demand: 'Dynamic pricing means that campsite, cabin, and day-use fees may vary based on
demand. During high-demand periods - such as summer weekends - rates may be higher' (the reservations page). The
camping page gives the ranges, 'tax inclusive': 'Basic ... $14-$24', 'Electric ... $26-$32', 'Full Hook-Up ...
$28-$40'; 'Campsite fees listed below do not include MVEF (Motor Vehicle Entrance Fee)', $7 a vehicle a day, doubled
for non-residents at Bear Lake, Farragut, Hells Gate, Priest Lake and Round Lake; a non-resident campsite fee of $3 a
night at most parks and '$24-$80 (Tier A)' at Farragut, Henrys Lake, Ponderosa, Priest Lake and Round Lake, where the
2023 law made non-residents pay double; a $10.00 transaction fee per reservation and a 3% card fee. (IDAPA 26.01.20
holds only the maxima: $34 / $42 / $46.) The booking site, getoutside.idaho.gov, is Itinio behind DataDome and was
not read. Each entry carries the ranges of the site types it has (from its note): nightly_low the cheapest type's
bottom, nightly_high the dearest type's top; no weekend figure (demand-priced)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
CAMPING = "https://parksandrecreation.idaho.gov/park-activity/camping/"
RES = "https://parksandrecreation.idaho.gov/reservations/"
RANGE = {"basic": (14, 24), "electric": (26, 32), "full": (28, 40)}
WORD = {"basic": "basic", "electric": "electric", "full": "full hookups"}
TIER_A = {9742, 9749, 9764, 9765, 9766}          # Henrys Lake, Ponderosa, Farragut, Round Lake, Priest Lake
MVEF_DOUBLE = {9709, 9756, 9764, 9765, 9766}     # Bear Lake, Hells Gate, Farragut, Round Lake, Priest Lake
TYPES = {
    9428: ("electric",), 9709: ("electric",), 9714: ("basic", "electric"), 9715: ("electric",),
    9716: ("full",), 9718: ("basic", "electric"), 9720: ("electric",), 9732: ("full",), 9737: ("basic",),
    9738: ("basic",), 9740: ("electric",), 9741: ("basic",), 9742: ("electric", "full"), 9745: ("full",),
    9746: ("basic",), 9749: ("electric", "full"), 9755: ("basic", "electric"), 9756: ("electric", "full"),
    9759: ("basic", "electric"), 9761: ("electric", "full"), 9762: ("electric", "full"), 9764: ("basic", "electric"),
    9765: ("basic", "electric"), 9766: ("basic", "electric", "full"),
}
out = []
for eid, types in sorted(TYPES.items()):
    e = rows[eid]
    if e.get("fees"):
        continue
    lo = min(RANGE[t][0] for t in types)
    hi = max(RANGE[t][1] for t in types)
    tier = eid in TIER_A
    fees = {"nightly_low": lo, "nightly_high": hi, "currency": "USD", "reservation_fee": 10,
            "entrance": {"resident": 7, "nonresident": 14 if eid in MVEF_DOUBLE else 7, "per": "vehicle_day"},
            "nonresident": ({"type": "multiplier", "factor": 2, "applies_to": "base"} if tier else
                            {"type": "surcharge", "amount": 3, "per": "night"}),
            "checked": "2026",
            "note": ("Idaho prices each site by demand ('rates may be higher' at busy times such as summer weekends) within "
                     "its statewide ranges, tax included: " +
                     "; ".join(f"{WORD[t]} ${RANGE[t][0]}-{RANGE[t][1]}" for t in ("basic", "electric", "full") if t in types) +
                     " a night (the site types here). " +
                     ("Non-residents pay double here. " if tier else "Non-residents pay $3 a night more. ") +
                     "Plus the motor vehicle entrance fee, $7 a day" +
                     (" ($14 for non-residents here)" if eid in MVEF_DOUBLE else "") +
                     ", and a $10 transaction fee per reservation (3% more by card). Idaho Parks and Recreation's "
                     f"camping and reservations pages, read {D}.")}
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": f"{CAMPING} ('Campsite & Facility Fees' ranges, non-resident fees, MVEF, transaction fee) + "
                          f"{RES} (dynamic pricing), read {D}; site types from the entry's note"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "ID findings")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:45], f["nightly_low"], f["nightly_high"], f["nonresident"], f["entrance"]["nonresident"])
