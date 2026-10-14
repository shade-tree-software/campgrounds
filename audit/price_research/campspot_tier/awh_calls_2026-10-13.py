"""AWH's calls on the Campspot tier pass, 2026-10-13: python3 -I awh_calls_2026-10-13.py [--apply]

"drop all #1.  #2 Drop Geronimo, keep Tymber and Clemson.  Drop #3 and #4.  Re-audit #5.  #6 remove bad values.
Leave #8 as is."  (The numbers are the decisions in that day's final report; report_items_2026-10-13.md has each.)

- #1, #2, #3, #4: the 18 entries in DROPS leave campgrounds.json, each logged with its reason in
  ../dropped_2026-10-11.jsonl (the price-research drop log). Every reason was read on 2026-10-13 during the batches;
  the commit that held each entry for AWH says the same.
- #2: Tymber Park (1224) and Clemson Hills (4377) stay; inclusion_evidence records the call so a later audit doesn't
  raise them again.
- #6: sites.max_rig_ft 23 is removed from the 28 entries in RIG. The note scan read it from our own sweep prose,
  "fits a 23-ft rig" (the sweeps checked that EKKO, a 23-ft rig, fits), which says nothing about the longest rig a
  campground takes (3206 also says "on 23 acres"). A sites group left empty goes, with its provenance. The 8 entries
  whose 23 ft is a real limit keep it: 6095 6112 6513 7121 7972 8041 8584 10435.
- #5 (the waterfront re-audit) is its own commit; #8 (Hilltop's phone) is unchanged; #7 (Riverbrook NH, Cross Creek
  in Cairo GA) is not decided yet.
"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
import trips  # noqa: E402
D = "2026-10-13"
ONE = f"AWH {D}: 'drop all #1'"
GERONIMO = f"AWH {D}: 'Drop Geronimo, keep Tymber and Clemson'"
THREE_FOUR = f"AWH {D}: 'Drop #3 and #4'"
TAIL = "(Campspot tier pass, read 2026-10-13; {})"
DROPS = {
    2031: ("dead: its website no longer resolves, and Campspot has listed The Fort closed since 2023-01-01, with no "
           "sites to book", ONE),
    2662: ("fairground camping by event permit only: the Campspot slug is gone, and Adams County's rules allow overnight "
           "RV parking only by permit for a county event; the entry's site counts, three-week limit and first website "
           "belonged to the Adams County Fairgrounds in Hastings NE (entry 2765)", ONE),
    2849: ("dead: its website is now a gambling spam site, Campspot has shown it closed since 2021, and 2025 reviews "
           "describe full-timers and a run-down park", ONE),
    4598: ("no live booking channel: Campspot's booking page offers no sites on any date, Hipcamp has only an unclaimed "
           "'coming soon' listing, and the park has no website of its own", ONE),
    4599: ("dead: its website and Campspot link belong to a different Cross Creek, in Cairo GA, 450 km away; the "
           "Mountain City park's own domain still advertised the 2018 season in 2023, was taken over by a gambling site "
           "in 2024 and now fails, and no other booking channel was found", ONE),
    5941: ("dead: its domain is a GoDaddy parking page, and its Campspot listing has been closed since 2021 with no "
           "site types", ONE),
    6791: ("dead: its domain doesn't resolve, Campspot has shown it closed since June 2022 with no site types, and only "
           "a TravelOK listing remains", ONE),
    6981: ("dead: it never had a website, Campspot has shown it closed since 2021 with no site types, and only "
           "aggregator listings remain", ONE),
    7399: ("dead: its domain is now a gambling spam site, and Campspot shows it closed from 2021 to 2027-03-19 with no "
           "site types", ONE),
    7416: ("long-stay only: it now sells monthly sites only ($745 plus electric, with Patriot RV Park next door), and "
           "Campspot has shown it closed since 2022", ONE),
    7511: ("long-stay only: weekly ($175 and up) and monthly ($450 and up) sites, booked by phone; its Campspot listing, "
           "renamed Twin Lakes RV Park, has been closed since 2023", ONE),
    7552: ("dead: its domain doesn't resolve, Campspot lists no sites, and only directory listings remain", ONE),
    7563: ("long-stay only: an adults-only long-term park with monthly rates only ($750-800 plus electric), a $30 "
           "application fee and a background check; neither of its Campspot listings has sites", ONE),
    7639: ("long-stay only: its own site sells only monthly sites ($500 plus metered electric), and its Campspot slug "
           "is dead", ONE),
    7866: ("closed: lostrece.com times out, the venue's own site said 'Permanently Closed' by June 2025 (Wayback), and "
           "Campspot shows no sites for sale", ONE),
    7537: ("approval-only: its site leads with $495 a month and 'APPLY NOW', and every overnight guest must apply "
           "online and be approved by the manager", GERONIMO),
    12695: ("7-night summer minimum: from June 19 to early September 2027 Campspot sells only Saturday-to-Saturday "
            "weeks ('No Sunday through Friday arrivals. No Sunday through Friday departures.'), like Nickerson Beach "
            "1447 and Alcona 3996", THREE_FOUR),
    4777: ("brand: a Sun Outdoors park, a brand AWH skips (2026-10-03: never in the price range); not researched",
           THREE_FOUR),
}
KEEP = {
    1224: ("AWH 2026-10-13: keep. Raised in the Campspot tier pass as a possible workforce long-stay park; it sells "
           "nightly sites year-round by phone (Campspot had no sites to book on 2026-10-13)."),
    4377: ("AWH 2026-10-13: keep. Raised in the Campspot tier pass because only its 3 Deluxe sites sell by the night "
           "(the Economy sites go by the week or month)."),
}
RIG = [3131, 3133, 3141, 3206, 3259, 3260, 3261, 3262, 3263, 3264, 3265, 3266, 3268, 3616, 3618, 3636, 3637, 3773,
       3852, 4086, 4379, 4534, 4687, 4822, 7013, 7189, 7406, 7519]

path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(path, encoding="utf-8"))
by = {r["id"]: r for r in rows}
log = []
for i, (why, said) in DROPS.items():
    e = by.get(i)
    if e is None:
        print(i, "already dropped")
        continue
    assert not trips.campground_references(i), (i, "referenced by a trip")
    log.append({"id": i, "name": e["name"], "state": e["state"], "ownership": e.get("ownership"),
                "action": "removed", "why": f"{why} {TAIL.format(said)}"})
gone = {x["id"] for x in log}
rows[:] = [r for r in rows if r["id"] not in gone]
for x in log:
    print("drop", x["id"], x["state"], x["name"])
for i, line in KEEP.items():
    e = by[i]
    if line not in (e.get("inclusion_evidence") or ""):
        e["inclusion_evidence"] = f"{e['inclusion_evidence']}; {line}" if e.get("inclusion_evidence") else line
        print("keep", i, e["name"])
for i in RIG:
    e = by[i]
    s = e.get("sites") or {}
    if s.get("max_rig_ft") != 23:
        print(i, "no max_rig_ft 23, skipped")
        continue
    prov = (e.get("provenance") or {}).get("sites") or {}
    assert prov.get("method") == "derived" and prov.get("source") == "note prose", (i, prov)
    del s["max_rig_ft"]
    if not s:
        del e["sites"]
        del e["provenance"]["sites"]
        if not e["provenance"]:
            del e["provenance"]
    print("rig", i, "sites now", json.dumps(e.get("sites")))
if "--apply" in sys.argv:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dropped_2026-10-11.jsonl"),
              "a", encoding="utf-8") as fh:
        for x in log:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    print("written")
else:
    print("(dry run)")
