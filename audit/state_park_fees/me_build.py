"""ME findings: the Bureau of Parks and Lands camping fee schedule, read 2026-10-12.

    python3 -I me_build.py OUT

The schedule is the page the booking engine links to as its "complete fee schedule". Its table
is the same in Wayback captures of 2024-04-16, 2025-04-30 and 2026-05-28. The engine
(cg-public-prod.web.maine.gov) only takes dates in its current online season, 5/18-9/13/2026,
so no 2027 night could be priced there."""
import json, os, sys
out_path = sys.argv[1]
URL = "https://www.maine.gov/dacf/parks/camping/reservations/campground_fees.shtml"
ENGINE = "https://cg-public-prod.web.maine.gov/public/index"
# id: (park as named in the table, resident base, resident water & electric or None)
P = {15: ("Lily Bay", 20, None), 16: ("Cobscook Bay", 20, None), 17: ("Sebago Lake", 25, 35),
     210: ("Camden Hills", 25, 35), 613: ("Bradbury Mountain", 15, None),
     4172: ("Lake St. George", 20, None), 4173: ("Lamoine", 20, None), 4174: ("Mount Blue", 20, 30),
     4175: ("Rangeley Lake", 20, 30), 4176: ("Peaks-Kenny", 20, 30), 4177: ("Aroostook", 15, 25)}
EXTRA = {4177: " At the park's 2026 reopening the hookups were not yet working (see the note).",
         16: " The schedule lists no hookup rate for this park."}
rows = {e['id']: e for e in json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), 'campgrounds.json'), encoding='utf-8'))}
out = []
for eid, (park, base, we) in sorted(P.items()):
    fees = {"nightly_low": base, "nightly_high": base, "currency": "USD", "reservation_fee": 5,
            "nonresident": {"type": "surcharge", "amount": 10, "per": "night"}}
    text = f"${base} a night for a Maine resident, ${base + 10} for a non-resident"
    if we:
        fees["surcharges"] = {"electric": we - base}
        text += f"; sites with water and electric ${we} (non-resident ${we + 10})"
    text += (". Fees are per site for up to 6 people. Reserving adds a non-refundable $5 processing fee for each "
             "night, not once per booking. 9% lodging tax on camping fees." + EXTRA.get(eid, "") +
             " Bureau of Parks and Lands fee schedule, read 2026-10-12 (the same table since at least April 2024).")
    fees["checked"] = "2026"
    fees["note"] = text
    out.append({"id": eid, "name": rows[eid]['name'], "fees": fees,
                "source": f"{URL} ({park} row, read 2026-10-12; same table in Wayback captures of 2024-04-16, "
                          f"2025-04-30 and 2026-05-28) + {ENGINE} ('$5 per night processing fees'; online "
                          f"season 5/18-9/13/2026, so no 2027 night could be priced)"})
json.dump(out, open(out_path, 'w'), indent=1, ensure_ascii=False)
print(len(out), 'ME findings'); print(json.dumps(out[2]['fees'], ensure_ascii=False))
