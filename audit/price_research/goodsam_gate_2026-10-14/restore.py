"""AWH 2026-10-14: "I have a Good Sam membership and qualify for a Good Sam
discount at participating parks. This means a park may pass the price gate on
this discount."  Re-test the price-gate drops that are Good Sam Parks
(discounts.good_sam true) at the park's own Good Sam rate, else 10% off.
Pass: 4943, 7385, 7860, 2227.  Still over: 12655 (C$80), 11305 ($54),
1519 ($58.50, also long-stay)."""
import json, sys
P = "campgrounds.json"; D = "2026-10-14"
HERE = "audit/price_research/goodsam_gate_2026-10-14/"
snap = json.load(open(HERE + "dropped_entries_snapshot.json", encoding="utf-8"))
GS = "with AWH's Good Sam membership (AWH 2026-10-14: a Good Sam Park may pass the price gate on its discount)"
R = {
 4943: dict(fees=(53, None, "RV sites from $53 a night; $47.70 with the 10% Good Sam discount. Read 2026-10-14."),
            src="https://thegulfbreezervresort.com/ (Newbook: 'RV Sites From $53.00 / night'), read 2026-10-14",
            ie=f"from $53 a night, $47.70 {GS}"),
 7385: dict(fees=(55, None, "30/50-amp sites $55 a day; $49.50 with the 10% Good Sam discount. Read 2026-10-14."),
            src="https://bayoubendrvresort.com/rv-lots ('Daily – $55'), read 2026-10-14",
            ie=f"$55 a day, $49.50 {GS}", web=["https://bayoubendrvresort.com/"],
            note="Large RV resort in Baytown at 10220 I-10 E (opened 2015). 118 concrete-slab RV sites (30/50/100 amp) "
                 "plus furnished cabins; pool, playground, 24-hr laundry, WiFi, pet-friendly. Right off I-10/Hwy 146, "
                 "~30 min from downtown Houston. Reservable online. --Claude"),
 7860: dict(fees=(55, None, "Regular sites from $55 a day; $49.50 with the 10% Good Sam discount. Read 2026-10-14."),
            src="https://thepalmsrvpark.com/rates ('Regular Site Daily $55 starting rate'), read 2026-10-14",
            ie=f"from $55 a day, $49.50 {GS}",
            web=["https://thepalmsrvpark.com/", "https://www.facebook.com/palmsrvpark/"],
            note="Coastal RV park in Aransas Pass, ~136 full-hookup sites (RV only, big-rig pull-throughs), "
                 "solar-heated pool and spa, laundry, free WiFi; a short drive to the Port Aransas ferry and Rockport. "
                 "--Claude"),
 2227: dict(fees=(52.8, None, "Full-hookup pull-throughs $52.80 a night (50 amp), $48 with a Good Sam, veteran or AARP "
                            "discount. Read 2026-10-14."),
            src="https://triplejrvpark.com/ ($52.80 a night, $48 with Good Sam), read 2026-10-14",
            ie=f"$52.80 a night, $48 {GS}"),
}
db = json.load(open(P, encoding="utf-8"))
have = {x["id"] for x in db}
for i, v in sorted(R.items()):
    if i in have: sys.exit(f"{i} already present")
    e = snap[str(i)]
    lo, hi, fn = v["fees"]
    e["fees"] = {"nightly_low": lo, **({"nightly_high": hi} if hi else {}), "currency": "USD", "checked": "2026", "note": fn}
    e.setdefault("provenance", {})["fees"] = {"source": v["src"], "checked": D}
    if "web" in v: e["website"] = "\n".join(v["web"])
    if "note" in v: e["note"] = v["note"]
    e["inclusion_evidence"] = (e.get("inclusion_evidence") or "").rstrip() + f"; restored {D} (Good Sam price gate): {v['ie']}"
    pos = max(k for k, x in enumerate(db) if x["id"] < i) + 1
    db.insert(pos, e)
    print("restored", i, e["name"], e["fees"])
if "--apply" in sys.argv:
    with open(P, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2); f.write("\n")
    with open("audit/price_research/dropped_2026-10-11.jsonl", "a", encoding="utf-8") as f:
        for i, v in sorted(R.items()):
            e = snap[str(i)]
            f.write(json.dumps({"id": i, "name": e["name"], "state": e["state"], "ownership": e["ownership"],
                                "action": "restored", "why": v["ie"]}, ensure_ascii=False) + "\n")
    print("written")
