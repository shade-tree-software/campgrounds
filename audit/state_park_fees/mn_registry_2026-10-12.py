"""Minnesota's registry row and state forests: python3 -I mn_registry_2026-10-12.py [--apply]

- state:MN fees was a `reported` row (a research target, docs/campground-schema.md): re-read from the DNR's fee page
  (dnr.state.mn.us/state_parks/fees.html, 2026-10-12). The $7 one-day / $35 year-round vehicle permit stands; the
  campsite reservation fee is added: '$8 (online)', '$10 (call center)', 'Non-refundable fee per each site reserved in
  advance. No fee for same-day reservations.'
- The 31 state forest campgrounds (26 of them unpriced) are `ownership: state`, so they inherited state:MN - the state parks' vehicle permit,
  reservation-only rule, 120-day window and 14-night maximum - though the row itself says 'State FORESTS are a separate
  system and DO keep first-come sites; this row covers state parks and recreation areas only'. They get policy_ref none
  (the rule for a campground outside its state's park system); mn_build.py prices them from the same fee page."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
D = "2026-10-12"
FEES = "https://www.dnr.state.mn.us/state_parks/fees.html"
pol_path = os.path.join(ROOT, "campground_policies.json")
pol = json.load(open(pol_path, encoding="utf-8"))
row = pol["state:MN"]
row["fees"] = {
    "currency": "USD",
    "reservation_fee": 8,
    "entrance": {"resident": 7, "nonresident": 7, "per": "vehicle_day"},
    "note": ("Vehicle permit: 'One-day vehicle permit ... $7', 'Year-round vehicle permit $35' ('valid for one year from the "
             "month of purchase'); 'Overnight guests need a state park vehicle permit in addition to a camping or lodging "
             "reservation'. No residency split, so both sides are recorded the same. Campsite reservation fee '$8 (online)', "
             "'$10 (call center)': 'Non-refundable fee per each site reserved in advance. No fee for same-day "
             "reservations.' Campsites: 'Drive-in campsites $20-$35/night', 'Electric hookup (where available) add "
             "$10/night', 'Water and sewer hookup (where available) add $8/night', tax additional - each park's own price "
             "is on its entries."),
}
row.setdefault("provenance", {})["fees"] = {"source": f"{FEES}, read {D}", "checked": D}
cs.validate_row(row, label="state:MN")

cg_path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(cg_path, encoding="utf-8"))
n = 0
for e in rows:
    if e.get("state") == "MN" and e.get("ownership") == "state" and "State Forest" in e["name"] \
            and not e.get(cs.POLICY_REF):
        e[cs.POLICY_REF] = cs.POLICY_REF_NONE
        cs.validate_row(e, label=e["name"])
        n += 1
        print(e["id"], e["name"])
print(n, "state forest entries -> policy_ref none")
print("state:MN fees:", json.dumps(row["fees"], ensure_ascii=False)[:300])
if "--apply" in sys.argv:
    for path, data in ((pol_path, pol), (cg_path, rows)):
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)
    print("written")
else:
    print("(dry run)")
