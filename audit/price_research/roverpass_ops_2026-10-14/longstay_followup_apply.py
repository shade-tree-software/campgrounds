"""Follow-ups of the long-stay rule (AWH 2026-10-14), from the 2026-10-14 report:
  - Cedar Beach 12647 drops on test 2: its rates page is empty (also in the 2026-01-24 Wayback capture) and CampLife,
    its only booking site, answers "We are not taking reservations for this time" for every date tried through
    June 2027 (17 sites listed there, against the ~80 overnight sites its note claimed). Same case as Rest Haven 4636.
  - The four parks held for a home-versus-RV count all pass test 5 (satellite 2026-10-14, Esri): Horseshoe Acres
    6764 ~30 RV sites to 9 mobile homes; Thompson Lake 7867 RV rows all round the lake, no homes inside the park;
    Yerby's 7929 ~60 RV pads beside ~15 mobile homes (the dense rows south of the street are a separate park);
    Oleander Acres 7684 states 300 RV sites and 10 park-model rentals and rents mobile-home lots by the month,
    selling no homes. Their notes now say what the park mostly is.
Run from the repo root; --apply writes."""
import json, os, sys
sys.path.insert(0, ".")
import trips

NOTES = {
    6764: "Mostly long-stay: an RV and mobile-home park on 36 acres off Hwy 53 near I-35 exit 40, Ardmore (58 Horseshoe "
          "Acres), with about 30 RV sites beside a small mobile-home section. 23+ full-hookup sites, 30/50 amp, Wi-Fi; "
          "daily, weekly and long-term stays. --Claude",
    7867: "Mostly long-stay (it calls itself an RV resort and manufactured-home park, though the grounds hold only RV "
          "sites): 80 sites (30/50 amp) round a 10-acre stocked lake with a swim area and fishing dock, in Big Thicket "
          "country ~25 mi N of Beaumont near Village Creek and the Neches River. Nightly $40, weekly and monthly too; "
          "free WiFi, playgrounds. --Claude",
    7684: "Mostly long-stay: a Winter Texan park in the Rio Grande Valley (Mission, 2421 S Conway Ave), sold mostly by "
          "the month and season, with 300 full-hookup sites (30/50-amp), 10 park-model rentals and a section of "
          "owner-placed mobile homes on rented lots. Takes daily ($45-65) and weekly stays; all ages, big-rig "
          "friendly, WiFi. Book online or by phone, 956-585-9093. --Claude",
    7929: "Mostly long-stay: a family-owned in-town RV and mobile-home park (since 1985) on S Meredith Ave in Dumas, "
          "next to McDade Park, on the US-287 panhandle overnight-stop corridor. About 75 full-hookup RV spaces (30/50 "
          "amp) with concrete patios beside ~15 mobile homes; laundry, WiFi, no on-site restrooms or showers. Takes "
          "overnighters; reservations by phone, 806-935-4940. --Claude",
}
DROP = {12647: "long-stay park with no nightly rate posted (its rates page is empty) and no booking site that sells a "
               "night: CampLife takes no reservations on any date through June 2027 (AWH 2026-10-14: the long-stay "
               "rule, docs/campground-curation.md)"}
rows = json.load(open("campgrounds.json", encoding="utf-8"))
by = {r["id"]: r for r in rows}
for i, n in NOTES.items():
    assert "--AWH" not in by[i]["note"], i
    by[i]["note"] = n
log = []
for i, why in DROP.items():
    e = by[i]
    assert e["ownership"] == "private" and not trips.campground_references(i), i
    log.append({"id": i, "name": e["name"], "state": e["state"], "ownership": e["ownership"], "action": "removed", "why": why})
rows[:] = [r for r in rows if r["id"] not in DROP]
if "--apply" in sys.argv:
    with open("campgrounds.json.tmp", "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False); fh.write("\n")
    os.replace("campgrounds.json.tmp", "campgrounds.json")
    with open("audit/price_research/dropped_2026-10-11.jsonl", "a", encoding="utf-8") as fh:
        for x in log: fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    print("written")
