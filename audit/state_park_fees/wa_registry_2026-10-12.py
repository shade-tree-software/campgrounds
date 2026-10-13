"""Washington State Parks' registry row, fees group: python3 -I wa_registry_2026-10-12.py [--apply]

state:WA fees was a `reported` row with no amounts ('A Discover Pass is the state's vehicle access pass; its interaction
with camping fees was not confirmed on the pages checked'). Re-read 2026-10-12: the agency's fees page
(parks.wa.gov/passes-permits/fees, text in wa_fee_pages_2026-10-12.txt) answers both: day-use parking 'requires a
Discover Pass which is $10 for the day or $45 for an annual pass. You don't have to pay this if you have already paid
for camping in the park you staying in', so no entrance is recorded; 'A non-refundable reservation fee is charged for
each reservation, $8 if made online and $10 if made by phone'; and 'Customers who do not reside in Washington state
will be charged a $15 fee per reservation. This fee is in addition to the regular reservation fee.'"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
D = "2026-10-12"
pol_path = os.path.join(ROOT, "campground_policies.json")
pol = json.load(open(pol_path, encoding="utf-8"))
row = pol["state:WA"]
row["fees"] = {
    "currency": "USD", "reservation_fee": 8,
    "nonresident": {"type": "surcharge", "amount": 15, "per": "stay"},
    "note": ("Camping includes parking for one vehicle: the $10 day / $45 annual Discover Pass is not needed in the park "
             "you are camping in. The $8 reservation fee is per reservation online ($10 by phone); people who do not live "
             "in Washington pay a $15 fee per reservation on top of it, so a first-come stay pays neither. Statewide "
             "ranges: peak season (May 15 - Sept. 15) standard sites $31-43, partial utility $41-51, full utility "
             "$46-56; shoulder season (April 1 - May 14, Sept. 16 - Oct. 31) $23-35 / $35-46 / $41-51, running through "
             "the winter at Cape Disappointment, Grayland Beach, Pacific Beach and Fort Worden; winter $23 / $35 / $41; "
             "primitive sites $12 all year. Extra vehicle $10 a night. Tax included. Each park's own prices are on its "
             "entry."),
}
row.setdefault("provenance", {})["fees"] = {
    "source": f"https://parks.wa.gov/passes-permits/fees (day-use parking, camping fees by season, reservation fees, "
              f"non-resident reservation fee), read {D}", "checked": D}
cs.validate_row(row, label="state:WA")
print(json.dumps(row["fees"], ensure_ascii=False)[:300])
if "--apply" in sys.argv:
    tmp = pol_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(pol, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, pol_path)
    print("written")
