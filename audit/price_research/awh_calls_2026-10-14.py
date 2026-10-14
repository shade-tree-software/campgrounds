"""AWH's calls on the CampLife and RoverPass tier passes, 2026-10-14: python3 -I awh_calls_2026-10-14.py [--apply]

"#3 keep if website (not facebook) publishes prices and provides phone number.  #4 drop if over price limit unless
very close to major gateway points (major cities, major tourist attractions, National Parks, etc.).  #5 keep if
(published prices on regular website and phone number) or active booking site, drop otherwise.  #6 prefer a published
phone number to our own that cannot be confirmed on any website. [...] #8 rename our name to currently-published name.
If our ownership looks wrong, change it to what is actively published.  Remove dead or unclaimed hipcamp links. [...]
For 'Over the price limit, priced and kept without asking you', drop unless we have an exception in place or they are
near major gateway points (major cities, major tourist attractions, National Parks, etc.)."  (The numbers are the
decisions in that day's final report; report_items_2026-10-14.md in camplife_tier/ and roverpass_tier/ has each.)

- The price limit is a private entry's cheapest RV site: $50 a night in the US, about C$69 before tax in Canada
  (docs/campground-curation.md). The report's "~C$55" was RV Life's avg_rate line, not the limit. A gateway is
  within 40 km of a 1M+ metro's downtown, a national park entrance or a major attraction (gateways.py).
- #4 and the FYI list: the 10 entries in DROPS over the limit have no gateway within 40 km (each reason names the
  nearest). Rockwell 14708 stays, 11 km from downtown Oklahoma City. The six Ontario parks under C$69 stay, and the
  two whose evidence called C$55 the gate are corrected; Whispering Pines 12789 (C$65) and MacLeod's Beach 12934
  (C$55) are under the limit too and are left as they are.
- #3: the nine parks whose booking calendar needs a login stay; each one's own website posts rates and a phone.
- #5: 7826, 1977 and 2064 go. Almeda 11057 stays: CampLife sells its two RV sites.
- #6: seven phones switch to the number the park publishes on its own pages or its active booking listing.
  Edmond's 405-216-7474/7476 (6829, 6834) and Crook County's 541-447-2599 (11073) stay: CampLife's park records
  publish them.
- #8b: 10641 takes the name Jackson County publishes. #8c: 5088 becomes private and loses its Hipcamp link (the
  listing takes no bookings; its RoverPass listing is claimed and bookable). #8d: 1981 becomes private: the city's
  page for it is gone, its own site names no government operator, and The Dyrt calls it a private facility on a
  church campus. #8e: the unclaimed "Coming soon" Hipcamp links on 2230 and 2231 go; both RoverPass listings are
  claimed and bookable. The other Hipcamp links are checked in their own pass.
- #1 (Riverbrook NH, Cross Creek in Cairo GA) aren't added: too expensive. #2 waits for criteria, #7 is its own
  commit, and 14655's rename (#8a) is moot.
"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import trips  # noqa: E402
D = "2026-10-14"
FOUR = f"AWH {D}: '#4 drop if over price limit unless very close to major gateway points'"
FYI = (f"AWH {D}: 'Over the price limit, priced and kept without asking you', drop unless we have an exception in "
       f"place or they are near major gateway points")
FIVE = f"AWH {D}: '#5 keep if (published prices on regular website and phone number) or active booking site'"
TAIL = "(price research, read 2026-10-14; {})"
CAD = "over the ~C$69 limit for a Canadian private park"
DROPS = {
    8295: (f"over the price limit: an RV pull-through is C$89 plus HST a night for 2 on the park's rates page, {CAD}; "
           "nearest gateway Toronto, 64 km", FOUR),
    12636: (f"over the price limit: CampLife's RV sites are C$76.10-107.08 a night before tax, {CAD}; nearest gateway "
            "Toronto, 55 km", FOUR),
    12648: (f"over the price limit: C$70 a night off season and C$85 in peak season, plus HST, on the park's rates "
            f"page, {CAD}; nearest gateway Toronto, 100 km", FOUR),
    12655: (f"over the price limit: CampLife's RV sites are C$89-97 a night before tax, {CAD}; nearest gateway Bruce "
            "Peninsula NP, 133 km", FOUR),
    1990: ("over the price limit: Campspot's RV sites are $88-131 a night before tax; nearest gateway Branson, 171 km",
           FYI),
    1496: ("over the price limit: $105 a night for two ($35 a person plus a $35 hookup fee) on the resort's own pages; "
           "nearest gateway Newark, 98 km", FYI),
    11305: ("over the price limit: Campspot's RV sites are $60-86 a night before tax; nearest gateway Death Valley NP, "
            "78 km", FYI),
    14851: ("over the price limit: Campspot's RV sites are $75 a night before tax; nearest gateway Joshua Tree NP, "
            "158 km", FYI),
    14655: ("over the price limit: Campspot's RV sites are $55 a night before tax; nearest gateway Hot Springs NP, "
            "125 km", FYI),
    1823: ("over the price limit: $60 a night for 2 adults ($30 each) on the park's rates page; nearest gateway "
           "Newark, 70 km (the Delaware Water Gap NRA, about 10 km away, isn't one)", FYI),
    7826: ("no live web presence: randrbytheres.com doesn't resolve, stephenvillerv.com answers 404, the CampLife "
           "listing has no park behind it, and RV Life's newest review is from October 2023", FIVE),
    1977: ("Facebook only: no website of its own and no booking site (its CampLife link sold a different park); the "
           "rate came from camper reports", FIVE),
    2064: ("Facebook only: no website of its own and no booking site (its CampLife link sold a different park); the "
           "rate came from camper reports", FIVE),
}
THREE = (f"AWH {D} (#3): keep - a booking calendar behind a login is fine when the operator's own website posts the "
         "rates and a phone number")
LINN = f"{THREE}: linncountyor.gov posts {{}} and 541-967-3917"
UNDER = f"price check {D}: the cheapest RV site, C${{}} before tax, is under the ~C$69 limit; AWH {D} (#4): keep"
KEEP = {
    6829: f"{THREE}: edmondok.gov posts $30-40 and (405) 216-7470",
    6834: f"{THREE}: edmondok.gov posts $30-35 and (405) 216-7470",
    9615: f"{THREE}: idahopower.com posts $35-40 and 1-844-472-7275",
    11014: LINN.format("$25-50"),
    11033: LINN.format("$28-37"),
    11083: LINN.format("$28"),
    11084: LINN.format("$45-50"),
    10515: f"{THREE}: pacificorp.com posts $37 and 801-280-3233",
    11073: f"{THREE}: ccprd.org posts $40-50 and 541.447.1209",
    11057: (f"AWH {D} (#5): keep - CampLife, an active booking site, sells pull-through sites 02 and 03 to "
            "self-contained RVs at $25 a night"),
    14708: (f"AWH {D}: over the $50 price limit ($65 a night on Campspot) but kept as a gateway park, 11 km from "
            "downtown Oklahoma City"),
    12650: UNDER.format(66),
    12660: UNDER.format(59),
    12675: UNDER.format(55),
    12659: UNDER.format(45),
}
# (id, old, new): my 2026-10-14 CampLife evidence measured these against the wrong (C$55) line
FIX_IE = [
    (8331, "so peak rates are over the ~C$55 private gate;",
     f"so the cheapest RV site is under the ~C$69 limit for a Canadian private park (AWH {D} #4: keep);"),
    (8342, "so the serviced sites are over the ~C$55 private gate;",
     f"all under the ~C$69 limit for a Canadian private park (AWH {D} #4: keep);"),
]
PHONES = {  # id: (ours, the park's published number)
    9848: ("208-388-2323", "1-844-472-7275"),   # ours is Idaho Power's customer service line; idahopower.com park page
    11464: ("928-753-2636", "928-753-8620"),    # ours only on a 2019 event page; 2025-26 fairbooks + CampLife
    4636: ("478-294-9010", "770-680-8722"),     # resthavenrv.com + CampLife
    7765: ("409-355-2347", "713-857-2775"),     # on none of its pages; its own site + RoverPass
    5119: ("601-520-3818", "601-818-5304"),     # ours only on Campendium; its RoverPass booking listing
    7870: ("(432) 386-7312", "432-466-1011"),   # ours on Yelp; its RoverPass booking listing
    11743: ("858-509-5140", "858-525-3847"),    # ours on parkadvisor as Surf & Turf; CampLife's park record
}
RENAME = {10641: ("Joseph H. Stewart State Recreation Area", "Joseph Stewart County Park")}
OWNER = {5088: ("hipcamp", "private"), 1981: ("local", "private")}
UNLINK = {
    5088: "https://www.hipcamp.com/en-US/land/mississippi-black-river-campsite-rv-park-06yh8dm2",
    2230: "https://www.hipcamp.com/en-US/land/kansas-seidels-rv-park-kk9hk8xp",
    2231: "https://www.hipcamp.com/en-US/land/kansas-bert-s-rv-park-dw9h96zz",
}
NOTE_CUT = {5088: "  Its Hipcamp listing no longer takes bookings."}
IE_CUT = {1981: " (City of Independence)"}
IE_ADD = {
    10641: f"renamed {D} (AWH #8b) from Joseph H. Stewart State Recreation Area, the name Jackson County publishes",
    5088: (f"re-check {D} (AWH #8c): ownership hipcamp -> private; it books on its own claimed RoverPass listing, and "
           "its Hipcamp listing takes no bookings (link removed)"),
    1981: (f"re-check {D} (AWH #8d): ownership local -> private; the City of Independence's page for it answers 404, "
           "the park's own site names no government operator, and The Dyrt calls it a private facility on the "
           "grounds of a church complex"),
    2230: f"re-check {D} (AWH #8e): unclaimed 'Coming soon' Hipcamp link removed; its RoverPass listing is bookable",
    2231: f"re-check {D} (AWH #8e): unclaimed 'Coming soon' Hipcamp link removed; its RoverPass listing is bookable",
}


def add_ie(e, line):
    ie = e.get("inclusion_evidence") or ""
    if line in ie:
        return False
    e["inclusion_evidence"] = f"{ie}; {line}" if ie else line
    return True


path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(path, encoding="utf-8"))
by = {r["id"]: r for r in rows}
log = []
for i, (why, said) in DROPS.items():
    e = by.get(i)
    if e is None:
        print(i, "already dropped")
        continue
    assert e.get("ownership") == "private", (i, e.get("ownership"))
    assert not trips.campground_references(i), (i, "referenced by a trip")
    log.append({"id": i, "name": e["name"], "state": e["state"], "ownership": e.get("ownership"),
                "action": "removed", "why": f"{why} {TAIL.format(said)}"})
gone = {x["id"] for x in log}
rows[:] = [r for r in rows if r["id"] not in gone]
for x in log:
    print("drop", x["id"], x["state"], x["name"])
for i, line in KEEP.items():
    if add_ie(by[i], line):
        print("keep", i, by[i]["name"])
for i, old, new in FIX_IE:
    e = by[i]
    if old in e["inclusion_evidence"]:
        e["inclusion_evidence"] = e["inclusion_evidence"].replace(old, new)
        print("fix ie", i, e["name"])
    else:
        assert new in e["inclusion_evidence"], i
for i, (old, new) in PHONES.items():
    e = by[i]
    if e.get("phone") == new:
        continue
    assert e.get("phone") == old, (i, e.get("phone"))
    assert old not in (e.get("note") or ""), i
    e["phone"] = new
    print("phone", i, old, "->", new)
for i, (old, new) in RENAME.items():
    e = by[i]
    if e["name"] != new:
        assert e["name"] == old, (i, e["name"])
        e["name"] = new
        print("rename", i, old, "->", new)
for i, (old, new) in OWNER.items():
    e = by[i]
    if e["ownership"] != new:
        assert e["ownership"] == old, (i, e["ownership"])
        e["ownership"] = new
        print("ownership", i, old, "->", new)
for i, url in UNLINK.items():
    e = by[i]
    links = (e.get("website") or "").split("\n")
    if url in links:
        links.remove(url)
        assert links and all(links), (i, links)
        e["website"] = "\n".join(links)
        print("unlink", i, url)
for i, cut in NOTE_CUT.items():
    e = by[i]
    if cut in e["note"]:
        e["note"] = e["note"].replace(cut, "")
        print("note", i, e["note"][-90:])
for i, cut in IE_CUT.items():
    e = by[i]
    if cut in e["inclusion_evidence"]:
        e["inclusion_evidence"] = e["inclusion_evidence"].replace(cut, "")
for i, line in IE_ADD.items():
    add_ie(by[i], line)
if "--apply" in sys.argv:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dropped_2026-10-11.jsonl"), "a",
              encoding="utf-8") as fh:
        for x in log:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    print("written")
else:
    print("(dry run)")
