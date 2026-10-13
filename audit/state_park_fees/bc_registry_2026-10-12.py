"""BC Parks' registry row, fees group: python3 -I bc_registry_2026-10-12.py [--apply]

provincial:BC fees had only a note. BC Parks' camping fees page and its 2026 camping fees information sheet (read
2026-10-12, bc_fee_pages_2026-10-12.txt) add the non-resident fee: 'Starting in 2026, a $20 non-resident fee is added
for visitors who do not live in British Columbia', 'Frontcountry camping: $20 per party per campground', applying to
'reservations, registrations, and first come, first served (FCFS) stays', from stays beginning May 15, 2026; and peak
fees 'from June 15 to Labour Day' at 59 high-use parks (the fee schedule lists each park's). The reservation fee stays
as the note had it ('$6 per campsite per night, to a maximum of $18 per site (plus tax)'), now as a number."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
D = "2026-10-12"
pol_path = os.path.join(ROOT, "campground_policies.json")
pol = json.load(open(pol_path, encoding="utf-8"))
row = pol["provincial:BC"]
row["fees"] = {
    "currency": "CAD", "reservation_fee": 6,
    "nonresident": {"type": "surcharge", "amount": 20, "per": "stay"},
    "note": ("Reservation fee '$6 per campsite per night, to a maximum of $18 per site (plus tax)'; phone adds a $5 "
             "per-transaction surcharge; first-come sites have none. Since May 15, 2026, people who do not live in B.C. "
             "pay a $20 non-resident fee 'per party per campground' - reserved or first come, first served - shown at "
             "booking or paid in the park without proof of B.C. residency. Fees vary by park and season: peak (summer) "
             "June 15 to Labour Day, higher at 59 high-use parks; shoulder; and a winter rate at some. Each campground's "
             "fees are on its entry. Cancelling more than seven days out refunds camping fees but never the transaction "
             "fees. NOTE on rating.price_tier for Canadian entries: the imported RV Life tier is computed on nominal "
             "dollars with no CAD conversion, so Canadian parks sit roughly one level high - see "
             "docs/campground-schema.md 4.3."),
}
row.setdefault("provenance", {})["fees"] = {
    "source": "https://bcparks.ca/reservations/camping-fees/ (non-resident fee, seasons) + "
              "https://nrs.objectstore.gov.bc.ca/kuwyyf/2026_camping_fees_information_sheet_7eed24d2eb.pdf ('$20 per party "
              f"per campground') + https://bcparks.ca/reservations/frontcountry-camping/ (reservation fee), read {D}",
    "checked": D}
cs.validate_row(row, label="provincial:BC")
print(json.dumps(row["fees"], ensure_ascii=False)[:250])
if "--apply" in sys.argv:
    tmp = pol_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(pol, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, pol_path)
    print("written")
