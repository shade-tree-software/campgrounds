"""Nebraska's registry row, fees group: python3 -I ne_registry_2026-10-12.py [--apply]

state:NE fees was a `reported` row with no amounts ('Resident/non-resident amounts were not published on the pages
checked'). Re-read 2026-10-12: outdoornebraska.gov/parks/park-pricing/ lists the park entry permit under its 'NEBRASKA
LICENSED VEHICLE' tab ('Daily permit: $7 Annual permit: $35 Duplicate annual permit: $17.50') and 'NON-NEBRASKA LICENSED
VEHICLE' tab ('Daily permit: $14 Annual permit: $70 Duplicate annual permit: $35'), and the booking site's quote adds
'Reservation Fees $8.50' (nebraskastateparks.reserveamerica.com, Branched Oak, 2027-06-15)."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
D = "2026-10-12"
pol_path = os.path.join(ROOT, "campground_policies.json")
pol = json.load(open(pol_path, encoding="utf-8"))
row = pol["state:NE"]
row["fees"] = {
    "currency": "USD", "reservation_fee": 8.5,
    "entrance": {"resident": 7, "nonresident": 14, "per": "vehicle_day"},
    "note": ("'A Motor Vehicle Park Entry Permit is required on all licensed vehicles entering any state park, state "
             "recreation area or state historical park.' Daily permit $7 for a Nebraska-licensed vehicle, $14 for any other "
             "(annual $35 / $70; a duplicate for a second household vehicle half price). The $8.50 reservation fee is on "
             "each online booking; first-come sites have none. Campsite prices are statewide by site level (camping rates "
             "grid) and are on the entries."),
}
row.setdefault("provenance", {})["fees"] = {
    "source": f"https://outdoornebraska.gov/parks/park-pricing/ (park permit tabs) and nebraskastateparks.reserveamerica.com "
              f"(reservation fee on a quote), read {D}", "checked": D}
cs.validate_row(row, label="state:NE")
print(json.dumps(row["fees"], ensure_ascii=False)[:300])
if "--apply" in sys.argv:
    tmp = pol_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(pol, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, pol_path)
    print("written")
