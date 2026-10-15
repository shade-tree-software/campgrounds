"""Restore the parks dropped on 2026-10-14 for no live web presence that pass the Google-listing rule AWH
reaffirmed that evening ("a Google maps review of a park that is open with a phone and 25+ reviews can be used to
add or keep a park in the absence of a website"). The 17 drops that never had a Google check were looked up with
audit/aggregator_url/gm3.py (google_restore_2026-10-14.txt); five pass. All five are RV Life $$, which keeps a
park with no posted rate (AWH 2026-10-14). Stephenville 7826 fails: Google's "Stephenville RV Park" is a
different, smaller park 2.3 km east on FM 8 (both seen on satellite). Run from the repo root; --apply writes."""
import json, os, sys

HERE = "audit/price_research/roverpass_ops_2026-10-14"
old = json.load(open(f"{HERE}/google_restore_2026-10-14_entries.json", encoding="utf-8"))
G = "Google Maps listing at our pin, open, phone {ph}, {n} reviews (read 2026-10-14); kept under the Google-listing rule (AWH 2026-10-14)"
FIX = {
    1204: dict(web="", n=31, ph="304-657-4595",
               note="Private family RV campground (gated, ~15 sites on 20 wooded acres) along the Middle Fork River "
                    "between Buckhannon and Elkins; on-site rafting, kayaking and tubing. Full hookups, 50-amp. Despite "
                    "the joke name it's a normal public campground. RV sites near or overlooking the river (on-bank "
                    "siting not confirmed). No website; book by phone, 304-657-4595. --Claude"),
    3887: dict(web="", n=97, ph="906-643-8248",
               note="Rustic family-run campground on Lake Huron (St. Martin Bay) north of St Ignace via ~2 mi of dirt "
                    "road (passable; a 37-ft motorhome reported easy access). Mostly non-electric dry sites, first come "
                    "first served and cash, plus ~6 electric 30-amp sites reservable by phone. Vault toilets, well "
                    "water, fire rings, sandy beach. No website; call 906-643-8248. --Claude"),
    3910: dict(web="https://www.river-road-campground.com/book-now", n=123, ph="906-231-1997",
               note="Private RV park and campground at 600 River Rd, Ontonagon, ~1 mi from downtown on the Ontonagon "
                    "River near the marina. ~40 sites, pull-through full hookups at 30 or 50 amp, plus tent sites and a "
                    "bunkhouse; bathhouse, laundry, kayak launch. Overnight and long-term stays. Book by phone, text or "
                    "email (906-231-1997). --Claude",
               fees=(40, 55, "RV sites from $40 a night (30-amp electric) to $55 (50-amp full hookup); tent sites "
                             "$20-30. Read 2026-10-14."),
               src="https://www.river-road-campground.com/book-now ('Electric 30 Amp Starting at $40 / Night'; "
                   "'Full Hook-up 50 Amp Starting at $55 / Night'), read 2026-10-14"),
    7877: dict(web="", n=101, ph="806-433-5671",
               note="Small Texas Panhandle RV park at 500 Orient St in Claude, ~30 min east of Amarillo near Palo Duro "
                    "and Caprock Canyons. ~30 back-in and pull-through sites with full hookups (20/30/50 amp) and "
                    "laundry; daily, weekly and monthly guests. Its website is down (403 since 2025); call "
                    "806-433-5671. --Claude"),
    10160: dict(web="", n=129, ph="435-586-9150",
                note="Small private RV park on Main St in Kanarraville, between Zion and Bryce (Cedar Breaks nearby). "
                     "22 full-hookup sites (6 pull-through), big-rig friendly to 40 ft; restrooms with hot showers, "
                     "laundry, dump, playground. ~0.5 mi from the Kanarraville Falls trailhead. No website; call "
                     "435-586-9150. --Claude"),
}
rows = json.load(open("campgrounds.json", encoding="utf-8"))
have = {r["id"] for r in rows}
for i, f in FIX.items():
    assert i not in have, i
    e = old[str(i)]
    e["note"], e["phone"] = f["note"], f["ph"]
    if f["web"]: e["website"] = f["web"]
    else: e.pop("website", None)
    b = e.get("booking")
    if b and b.get("platform") == "hipcamp": b["platform"] = "phone"
    if "fees" in f:
        lo, hi, note = f["fees"]
        e["fees"] = {"nightly_low": lo, "nightly_high": hi, "currency": "USD", "checked": "2026", "note": note}
        e.setdefault("provenance", {})["fees"] = {"source": f["src"], "checked": "2026-10-14"}
    e["inclusion_evidence"] = (e.get("inclusion_evidence") or "").rstrip() + "; " + G.format(ph=f["ph"], n=f["n"])
    # the file isn't in id order: insert after the largest lower id, so the diff is just these entries
    k = max(range(len(rows)), key=lambda j: rows[j]["id"] if rows[j]["id"] < i else -1)
    rows.insert(k + 1, e)
print("restored", len(FIX))
if "--apply" in sys.argv:
    with open("campgrounds.json.tmp", "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False); fh.write("\n")
    os.replace("campgrounds.json.tmp", "campgrounds.json")
    p = "audit/price_research/dropped_2026-10-11.jsonl"
    keep = [l for l in open(p, encoding="utf-8") if not (json.loads(l)["id"] in FIX and "2026-10-14" in l)]
    open(p, "w", encoding="utf-8").writelines(keep)
    print("written")
