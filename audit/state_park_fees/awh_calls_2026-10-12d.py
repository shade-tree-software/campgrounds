"""AWH's calls of 2026-10-12 (night): python3 -I awh_calls_2026-10-12d.py [--apply]

"For the 6 SK sites you might as well just say $18-$20. It's not worth trying to narrow it down for a $2 difference.
Drop Besant."

- The six Sask Parks self-registration campgrounds that are not on the booking site get $18-20: the 2026-27 fee
  table's economy ($18) and non-electrical ($20) rates, one of which applies to an unserviced site. Written to
  sk_self_registration_fees_2026-10-12.json; land it with apply.py. Amisk Lake's electric sites are the table's $35, in
  the note. The vehicle entry permit goes on the four provincial-park campgrounds and Tyrrell Lake (its note: 'Sask
  Parks Pass required'), not on Amisk Lake, where nothing says so.
- Besant Campground (SK 9290) is dropped: a leased recreation site with only a Facebook page and a phone number, no
  published rate. Logged in dropped.jsonl."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import trips  # noqa: E402
D = "2026-10-12"
CALL = f"AWH {D}: 'For the 6 SK sites you might as well just say $18-$20.'"
TABLE = "https://parks.saskatchewan.ca/resource/contracts/skpp/Parks_Rates_and_Fees_Table-2026-27.pdf"
ENTRY_PERMIT = {"resident": 11, "nonresident": 11, "per": "vehicle_day"}
SITES = {9157: False, 9160: True, 9168: True, 9180: True, 9185: True, 9206: True}   # entry -> vehicle permit recorded
path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(path, encoding="utf-8"))
by = {r["id"]: r for r in rows}
out = []
for eid, permit in SITES.items():
    e = by[eid]
    assert not e.get("fees"), eid
    text = ("Self-registration, first come, first served. Sask Parks' 2026-27 fee table charges an unserviced site $18 "
            "(economy) or $20 (non-electrical) a night, taxes included; which class this campground is isn't published." +
            (" Its electric sites are the table's $35." if eid == 9157 else "") +
            (" Plus a vehicle entry permit, $11 a day ($42 a week, $82 a year; free for Saskatchewan residents 65 and "
             "older)." if permit else "") + f" {CALL}")
    fees = {"nightly_low": 18, "nightly_high": 20, "currency": "CAD", "surcharges": {"weekend": 0}, "checked": "2026",
            "note": text}
    if permit:
        fees["entrance"] = ENTRY_PERMIT
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": f"{TABLE} (Economy Campsite $18.00, Non-Electrical Campsite $20.00) + {CALL}, read {D}"})
for x in out:
    print("price", x["id"], x["name"], x["fees"]["nightly_low"], x["fees"]["nightly_high"])
DROPS = {9290: ("no published rate and no booking page: a leased provincial recreation site (Besant Trans-Canada "
                "Campground) with only a Facebook page and a phone number; Tourism Saskatchewan's listing gives no rate "
                f"(read {D}). AWH {D}: drop.")}
log = []
for i, why in DROPS.items():
    e = by.get(i)
    if e is None:
        print(i, "already dropped")
        continue
    assert not trips.campground_references(i), (i, "referenced by a trip")
    log.append({"id": i, "name": e["name"], "state": e["state"], "ownership": e.get("ownership"), "action": "dropped",
                "decided": D, "why": why})
gone = {x["id"] for x in log}
rows[:] = [r for r in rows if r["id"] not in gone]
for x in log:
    print(x["action"], x["id"], x["state"], x["name"])
if "--apply" in sys.argv:
    json.dump(out, open(os.path.join(HERE, "sk_self_registration_fees_2026-10-12.json"), "w", encoding="utf-8"), indent=1,
              ensure_ascii=False)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
    with open(os.path.join(HERE, "dropped.jsonl"), "a", encoding="utf-8") as fh:
        for x in log:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    print("written")
else:
    print("(dry run)")
