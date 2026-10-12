"""Give New York's DEC campgrounds their own registry row instead of NY State Parks':
python3 -I ny_dec_row_2026-10-12.py [--apply]

AWH 2026-10-12, on Cranberry Lake ($20) and Meadowbrook ($18): how do those fit NY State Parks' $17-plus-add-ons schedule?
They don't - they are DEC campgrounds, a different agency on the same ReserveAmerica site, and DEC sets one nightly fee
per campground. But being `ownership: state` in NY made them inherit the `state:NY` row (OPRHP), so their popups put
"Typical for New York state parks" under DEC's terms. AWH: give DEC its own row.

1. Registry row `state:new-york-dec-campgrounds`, from DEC's own pages (read 2026-10-12). Registry levels merge per KEY,
   so the row sets every key `state:NY` sets (booking reservable/platform/note, fees currency/nonresident/surcharges/
   note); otherwise a State Parks value would show through under DEC's name.
2. `policy_ref` -> that row on the 43 DEC campgrounds (the entries priced from DEC's campground summary).
3. `policy_ref: none` on three DEC state-forest / wild-forest camping areas (Sugar Hill, Hunts Pond, Moose River Plains;
   Stoney Pond already had it): outside both State Parks and DEC's campground program - primitive state-land camping
   runs on its own rules ('stays of more than three days in one place require a permit from the New York State Forest
   Ranger', dec.ny.gov/things-to-do/camping/state-land-rules), so the campground row's 14-night limit would be wrong
   for them.
4. The 23 DEC campgrounds priced 2026-10-09 got only a price; their provenance already cites the summary's non-resident
   footnote, which covers 'all facilities', so they get it as their own value (as the other 20 have)."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
D = "2026-10-12"
REF = "state:new-york-dec-campgrounds"
SUMMARY = "https://dec.ny.gov/sites/default/files/2025-04/summerreccampgroundsummary.pdf"
FOREST_AREAS = (1398, 1431, 13729)
ROW = {
    "booking": {
        "reservable": True,
        "platform": "reserveamerica",
        "url": "https://newyorkstateparks.reserveamerica.com",
        "window_opens_days": 270,
        "max_stay_nights": 14,
        "note": ("New York's Department of Environmental Conservation (DEC) runs 51 campgrounds in the Adirondack and "
                 "Catskill Parks, separately from NY State Parks but on the same booking site: 'All reservations must "
                 "be made using the ReserveAmerica system' (online or 1-800-456-CAMP; 'Do not call the individual "
                 "campgrounds'), and 'You may reserve a DEC campground up to 9 months in advance.' Each campground "
                 "has its own reservation minimum of 1 to 3 nights (the RES MIN column of DEC's campground summary: 2 "
                 "at the Catskill and Lake George campgrounds, 3 at Fish Creek Pond), and 'When the first campground "
                 "opens for the season, the reservation minimums at all facilities will become 1 night until "
                 "closing.' A permit runs at most 14 nights, renewable if sites are free, and 'From July 1 through "
                 "Labor Day only 14 cumulative nights of camping can be obtained at any campground.' Check-in 2-9 pm, "
                 "check-out 11 am; generators only 9-11 am and 4-7 pm, at most 5 hours a day."),
    },
    "fees": {
        "currency": "USD",
        "nonresident": {"type": "surcharge", "amount": 5, "per": "night"},
        "reservation_fee": 7.25,
        "surcharges": {"weekend": 0},
        "note": ("DEC sets one nightly fee per campground in its annual campground summary ($16 to $28 in 2026), the "
                 "same every night: no weekend rate and no base-plus-amenities schedule, unlike NY State Parks. "
                 "'Non-New York State residents will be charged an additional $5/night for camping at all "
                 "facilities.' Frontier Town's electric sites and the Family Sites at some campgrounds cost 'an "
                 "additional nightly rate' the summary does not give. The $7.25 reservation fee is the booking "
                 "site's, on every DEC campground sampled."),
    },
    cs.PROVENANCE: {
        "booking": {"source": ("https://dec.ny.gov/things-to-do/camping/reservations ('All reservations must be made "
                               "using the ReserveAmerica system', 'You may reserve a DEC campground up to 9 months in "
                               "advance') + https://dec.ny.gov/things-to-do/camping/campground-rules-regulations "
                               "('Camping permits will not be issued for more than 14 nights but may be renewed', "
                               "'From July 1 through Labor Day only 14 cumulative nights', check-in/out, generator "
                               "hours) + https://dec.ny.gov/things-to-do/camping ('DEC operates 51 campgrounds located "
                               "in the Adirondack and Catskill Parks') + " + SUMMARY + " (RES MIN column and its "
                               "footnote), all read 2026-10-12"),
                    "checked": D},
        "fees": {"source": (SUMMARY + " (2026 Summer Recreation Campground Summary, revised 1/12/26: one nightly "
                            "camping fee per campground; '* Non-New York State residents will be charged an additional "
                            "$5/night for camping at all facilities'; '*** RV/Trailer electric hookup sites ... at "
                            "additional nightly rates') + newyorkstateparks.reserveamerica.com (six DEC campgrounds "
                            "sampled, 'Reservation Fees $7.25' on every site; ny_booking_sample_2026-10-12.jsonl), "
                            "read 2026-10-12"),
                 "checked": D},
    },
}

cg_path = os.path.join(ROOT, "campgrounds.json")
reg_path = os.path.join(ROOT, "campground_policies.json")
rows = json.load(open(cg_path, encoding="utf-8"))
reg = json.load(open(reg_path, encoding="utf-8"))

# The row goes right after state:NY, so the two New York agencies read together.
missing = {g: sorted(set(reg["state:NY"][g]) - set(ROW[g])) for g in reg["state:NY"] if g != cs.PROVENANCE}
assert not any(missing.values()), f"the DEC row must set every key state:NY sets: {missing}"
cs.validate_row(ROW, label=REF)
reg = {k: v for k, v in reg.items() if k != REF}
out = {}
for k, v in reg.items():
    out[k] = v
    if k == "state:NY":
        out[REF] = ROW
reg = out

dec = [e for e in rows if SUMMARY.split("/")[-1] in json.dumps((e.get(cs.PROVENANCE) or {}).get("fees") or {})]
assert len(dec) == 43, len(dec)
added_nr = []
for e in dec:
    assert e.get("state") == "NY" and e.get("ownership") == "state" and not e.get("policy_ref"), e["id"]
    e["policy_ref"] = REF
    fees = e["fees"]
    if "nonresident" not in fees:
        cs.apply_update(e, {"fees": {"nonresident": {"type": "surcharge", "amount": 5, "per": "night"}}})
        prov = dict(e.get(cs.PROVENANCE) or {})
        pf = dict(prov.get("fees") or {})
        pf["source"] = (pf["source"] + "; non-resident +$5/night from the summary's footnote '* Non-New York State "
                        "residents will be charged an additional $5/night for camping at all facilities', read 2026-10-12")
        pf["checked"] = D
        prov["fees"] = pf
        e[cs.PROVENANCE] = prov
        added_nr.append(e["id"])
    cs.validate_row(e, label=e["name"])
by = {e["id"]: e for e in rows}
for i in FOREST_AREAS:
    e = by[i]
    assert e.get("state") == "NY" and not e.get("policy_ref") and "dec.ny.gov" in (e.get("website") or ""), i
    e["policy_ref"] = cs.POLICY_REF_NONE
    cs.validate_row(e, label=e["name"])
print(f"row {REF}; policy_ref on {len(dec)} DEC campgrounds; 'none' on {len(FOREST_AREAS)} state-forest areas; "
      f"own non-resident fee added to {len(added_nr)}: {added_nr}")
for i in (287, 343, 20, 1398, 15339):
    r = cs.resolve(by[i], out)
    print(i, by[i]["name"], cs.policy_refs(by[i]),
          {g: v["inherited"] for g, v in r.items() if v.get("inherited")})
if "--apply" in sys.argv:
    for path, data in ((cg_path, rows), (reg_path, reg)):
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)
    print("written")
else:
    print("(dry run)")
