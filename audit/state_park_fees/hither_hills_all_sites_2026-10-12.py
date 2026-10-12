"""Re-check Hither Hills (291) against every site, and say what its $33 already contains:
python3 -I hither_hills_all_sites_2026-10-12.py [--apply]

AWH 2026-10-12: the campground sits in the dunes right on the Atlantic - are we sure no site carries New York's
oceanfront (+$10) or premium (+$3) charge? Maybe the $33-37 already includes them?

The first pass priced 23 of the 176 sites. ny_hither_hills_all_sites_2026-10-12.jsonl prices all 176 (ra_list.py, then
ra_price.py per site): every one is a plain 'Campsite' with no electric or full hookup, $33 on Tuesday 2027-06-15 and
$37 on Saturday 2027-06-19. So no site costs more than another and nothing is charged on top.

The charges are inside the $33. parks.ny.gov/camping/fees-policies (read 2026-10-12): 'Standard Site $17.00 / Primitive
Site $14.00 ... Flagship campgrounds incur an additional $3.00 per night fee and are noted with an asterisk' and lists
'Hither Hills*'; amenity fees are Platform/Pad $3, Weekend/Holiday $4, XL Site+ $5, Waterfront $6, Electric $7/$9,
Oceanfront $10, Full Hook-up $13/$15. With no electric, the only ways to reach $33 on a weeknight both contain the $10
oceanfront charge: 17 + 3 flagship + 10 oceanfront + 3 pad, or 14 + 3 + 10 + 6 waterfront. Without it no combination
comes to $33 (the nearest are $31 and $34). The flagship charge is stated; the oceanfront one is inferred from that
arithmetic, since Hither Hills already departs from the statewide rules (non-residents pay double, not +$5), so the note
says 'matches the fee table' rather than claiming New York itemizes it. The weekend charge also applies to the night
before a holiday."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
D = "2026-10-12"
cg_path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(cg_path, encoding="utf-8"))
hh = next(r for r in rows if r["id"] == 291)
fees = dict(hh["fees"])
fees["note"] = ("$33 a night, or $37 on a Friday, a Saturday or the night before a holiday, for New York residents; "
                "non-residents pay double ($66 / $74). Nothing is added on top: all 176 sites are plain campsites with "
                "no hookups, and the booking site charges every one the same. The $33 already contains New York's $3 "
                "flagship-campground charge, and it matches the state's fee table only with the $10 oceanfront charge "
                "included too. $7.25 reservation fee. Read 2026-10-12.")
prov = dict(hh.get(cs.PROVENANCE) or {})
prov["fees"] = {"source": "https://parks.ny.gov/camping/fees-policies ('Standard Site $17.00', 'Flagship campgrounds "
                          "incur an additional $3.00 per night fee', 'Hither Hills*: $33.00 - $74.00', 'Weekend/Holiday "
                          "(Friday, Saturday, & night before a holiday) $4.00', 'Oceanfront $10.00') + "
                          "https://parks.ny.gov/visit/state-parks/hither-hills-state-park ('NY Resident Weekday "
                          "Reservation: $33', 'Weekend Reservation: $37', 'Non-Resident Weekday Reservation: $66', "
                          "'Weekend Reservation: $74') + newyorkstateparks.reserveamerica.com parkId 297 (all 176 sites, "
                          "no hookups: $33 on 2027-06-15, $37 on 2027-06-19, $7.25 reservation fee), all read 2026-10-12",
                "checked": D}
cs.apply_update(hh, {"fees": fees, cs.PROVENANCE: prov})
cs.validate_row(hh, label=hh["name"])
print(291, hh["name"], json.dumps(hh["fees"], ensure_ascii=False))
if "--apply" in sys.argv:
    tmp = cg_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, cg_path)
    print("written")
else:
    print("(dry run)")
