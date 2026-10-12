"""Say what each non-resident multiplier multiplies (fees.nonresident.applies_to), and rebuild Hither Hills' fees:
python3 -I nonresident_scope_2026-10-12.py [--apply]

AWH 2026-10-12, on Hither Hills' popup: is the add-on inside the range or extra, and does 'x2' double the base or the
price after add-ons? The answer differs by agency:
- 'total' - the whole nightly price scales: Delaware ('Non-residents pay 1.25 times the resident price, rounded up',
  measured on the booking site weekday and weekend), Hither Hills ($33/$37 resident weekday/weekend vs $66/$74), and Bucks
  County's two parks ($25 vs $50, no add-ons).
- 'base' - only the base doubles and the add-ons cost everyone the same: Suffolk County ('Resident $18 ... Non-resident
  $36'; its own worked example is '$36 base + $8 electric + site tier'), its six parks and its registry row.
Massachusetts' x3.2 stays unspecified: its rate table gives out-of-state prices per tier and nothing on add-ons.

Hither Hills: the park page gives $33 weekday / $37 weekend for residents and exactly double for non-residents; 23 sites
sampled on the booking site (ny_hither_hills_sample_2026-10-12.jsonl) are all plain campsites, no hookups, $33 on a
Tuesday and $37 on a Saturday, plus a $7.25 reservation fee. So $33 base, +$4 on weekends, non-residents double the
whole price; the statewide add-ons it used to borrow (electric, oceanfront, premium) do not apply."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
D = "2026-10-12"
SCOPE = {215: "total", 649: "total", 670: "total", 867: "total", 868: "total", 13365: "total", 13366: "total",
         1446: "base", 1450: "base", 1451: "base", 1452: "base", 1453: "base", 1456: "base"}
ROW_SCOPE = {"local:suffolk-county-ny": "base"}
cg_path = os.path.join(ROOT, "campgrounds.json")
reg_path = os.path.join(ROOT, "campground_policies.json")
rows = json.load(open(cg_path, encoding="utf-8"))
reg = json.load(open(reg_path, encoding="utf-8"))
by = {r["id"]: r for r in rows}
for eid, scope in SCOPE.items():
    e = by[eid]
    nr = dict(e["fees"]["nonresident"])
    assert nr["type"] == "multiplier", eid
    nr["applies_to"] = scope
    cs.apply_update(e, {"fees": {"nonresident": nr}})
    cs.validate_row(e, label=e["name"])
    print(eid, e["name"], "->", scope)
for ref, scope in ROW_SCOPE.items():
    nr = dict(reg[ref]["fees"]["nonresident"])
    nr["applies_to"] = scope
    reg[ref]["fees"]["nonresident"] = nr
    cs.validate_row(reg[ref], label=ref)
    print(ref, "->", scope)
hh = by[291]
hh.pop("fees", None)
prov = dict(hh.get(cs.PROVENANCE) or {})
prov["fees"] = {"source": "https://parks.ny.gov/visit/state-parks/hither-hills-state-park ('NY Resident Weekday Reservation: "
                          "$33', 'Weekend Reservation: $37', 'Non-Resident Weekday Reservation: $66', 'Weekend Reservation: "
                          "$74', read 2026-10-12) + newyorkstateparks.reserveamerica.com parkId 297 (23 sampled sites, no "
                          "hookups: $33 on 2027-06-15, $37 on 2027-06-19, $7.25 reservation fee, read 2026-10-12)",
                "checked": D}
cs.apply_update(hh, {"fees": {
    "nightly_low": 33, "nightly_high": 33, "currency": "USD", "reservation_fee": 7.25,
    "nonresident": {"type": "multiplier", "factor": 2, "per": "night", "applies_to": "total"},
    "surcharges": {"weekend": 4}, "checked": "2026",
    "note": ("$33 a night on a weekday, $37 on a Friday or Saturday night, for New York residents; non-residents pay double "
             "($66 / $74). Every site is a plain campsite: no electric, water or sewer hookups, and the booking site charged "
             "every sampled site the same. $7.25 reservation fee. The park's fees page and the booking site, read 2026-10-12.")},
    cs.PROVENANCE: prov})
cs.validate_row(hh, label=hh["name"])
print(291, hh["name"], json.dumps(hh["fees"], ensure_ascii=False)[:300])
if "--apply" in sys.argv:
    for path, data, nl in ((cg_path, rows, True), (reg_path, reg, True)):
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            if nl:
                fh.write("\n")
        os.replace(tmp, path)
    print("written")
else:
    print("(dry run)")
