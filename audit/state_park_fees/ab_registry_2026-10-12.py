"""Alberta Parks' registry row, fees group: python3 -I ab_registry_2026-10-12.py [--apply]

provincial:AB fees had no amounts ('The reservation FAQ names only "non-refundable administrative fees" without
amounts'). The fee guidelines page (albertaparks.ca/.../camping-in-alberta-parks/fee-guidelines/, read 2026-10-12)
gives them: 'Shop.Albertaparks.ca: Non-refundable $12 reservation fee per reservation plus full pre-payment of camping
fees' (the same $12 by phone), 'Fees are inclusive of the federal Goods and Services Tax (GST)', basic campsites '$8 -
$31/night ... plus additional service fees', '$8/night' each for water, electric and sewer hook-ups, and 'There are no
fees for day use in provincial parks, however a vehicle parking pass is required ... in Kananaskis Country and the Bow
Valley Corridor'."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
D = "2026-10-12"
pol_path = os.path.join(ROOT, "campground_policies.json")
pol = json.load(open(pol_path, encoding="utf-8"))
row = pol["provincial:AB"]
row["fees"] = {
    "currency": "CAD", "reservation_fee": 12,
    "note": ("Each campground's fees are set by market demand and services within the approved range: basic campsites "
             "$8-31 a night, plus $8 a night each for water, electric and sewer hook-ups (and for showers where they are "
             "not coin-operated); GST included. A non-refundable $12 reservation fee per reservation, online or by phone; "
             "first-come sites have none. No day-use fee and no out-of-province rate difference, but vehicles parked in "
             "Kananaskis Country and the Bow Valley need a Kananaskis Conservation Pass ($15 a day, $90 a year; on those "
             "entries). Each campground's prices are on its entry. See the BC row's note on Canadian rating.price_tier "
             "being roughly one level high."),
}
row.setdefault("provenance", {})["fees"] = {
    "source": f"https://www.albertaparks.ca/albertaparks-ca/visit-our-parks/camping-in-alberta-parks/fee-guidelines/ "
              f"(camping fees, additional services, reservations, Kananaskis Conservation Pass), read {D}", "checked": D}
cs.validate_row(row, label="provincial:AB")
print(json.dumps(row["fees"], ensure_ascii=False)[:300])
if "--apply" in sys.argv:
    tmp = pol_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(pol, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, pol_path)
    print("written")
