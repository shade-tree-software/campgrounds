"""The Hipcamp link pass, 2026-10-14: python3 -I hipcamp_apply_2026-10-14.py [--apply]

AWH 2026-10-14 #8: "Remove dead or unclaimed hipcamp links."  hipcamp_links_2026-10-14.py read every Hipcamp link
in campgrounds.json (74 links on 74 entries) against Hipcamp's sitemap and each listing's own page record
(hipcamp_links_2026-10-14.json): 58 are live and bookable, 16 are dead - 10 asleep and 1 an unpublished draft, all
11 imported by Hipcamp and never claimed by the park (isExternal), and 5 gone (the link redirects to Hipcamp's state
index). A further 12 entries say in their note that they book on Hipcamp but carry no link: 6 have a live listing
(3257, 5630, 7882, 10137, 12721, 12750) and are left alone, and 6 have none.

What happens to an entry that loses its Hipcamp channel follows the standing rules:
- the live web presence rule (AWH 2026-09-08): no working site and no active booking listing means exclude, and a
  dormant Hipcamp listing or an unclaimed directory page doesn't count; with AWH 2026-10-14 #5, "keep if (published
  prices on regular website and phone number) or active booking site, drop otherwise";
- the price limit (AWH 2026-10-14): an entry priced over $50 a night is dropped unless an exception is in place or
  it is near a gateway (gateways.py: 40 km of a 1M+ metro's downtown, a national park entrance or a listed
  attraction).
Each entry was searched for another channel first (its own website, RoverPass, Campspot, CamplinQ, Pitchup, the
Hipcamp sitemap under another id). The pages read are in awh_calls_2026-10-14/ (hc_sites*.txt, hc_verify.txt,
hc_happycamp.txt). hc_sites.txt and hc_sites2.txt were read before fetch1.py learned to drop HTML comments, so
Liberty Haven's commented-out rate table shows in them as if it were live text; hc_verify.txt is the re-read. Drops
are logged to dropped_2026-10-11.jsonl like the earlier passes.

Edited notes are re-scanned afterwards (extract_fields.py --dump, then audit/note_scan/apply_absent.py --rescan),
so the note-derived booking.platform "hipcamp" goes with the sentence it came from.
"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import trips  # noqa: E402
D = "2026-10-14"
LIVE = (f"AWH 2026-09-08: no working site and no active booking listing means exclude; AWH {D} #5: 'keep if "
        "(published prices on regular website and phone number) or active booking site, drop otherwise'")
OVER = (f"AWH {D}: over the price limit, drop unless we have an exception in place or they are near major gateway "
        "points")
TAIL = "(Hipcamp link pass, read 2026-10-14; {})"
ASLEEP = "its Hipcamp listing is asleep, imported by Hipcamp and never claimed by the park (isExternal)"
GONE = "its Hipcamp listing is gone (the link redirects to Hipcamp's {} index)"
DROPS = {
    1204: (f"no live web presence: {ASLEEP}; no website, booking site or other listing found", LIVE),
    1314: (f"no live web presence: {GONE.format('Ohio')}; no website or booking site found, only directory pages "
           "(RV Life, The Dyrt, Campendium)", LIVE),
    1746: (f"no live web presence: {ASLEEP}; Facebook only, no website or booking site found", LIVE),
    3887: (f"no live web presence: {ASLEEP}; no website or booking site found (reservations by phone, per camper "
           "reviews)", LIVE),
    3910: (f"no live web presence: riverroadrvpark.net now forwards to an unrelated content-farm page "
           f"(searchandhelp.com); {ASLEEP}; its RoverPass and CamplinQ pages are unclaimed directory listings", LIVE),
    4251: (f"no live web presence: {GONE.format('North Carolina')}; no website, booking site or other listing found",
           LIVE),
    4474: (f"no live web presence: {GONE.format('Tennessee')}; Facebook only", LIVE),
    5125: (f"no live web presence: {ASLEEP}; its RoverPass listing is gone (the link redirects to RoverPass's Wiggins "
           "index) and its own domain, wigginscampground.com, has lapsed", LIVE),
    6973: (f"no live web presence: {ASLEEP}; Facebook only", LIVE),
    10160: ("no live web presence: its Hipcamp listing is an unpublished draft, imported by Hipcamp and never claimed "
            "(isExternal); its RoverPass listing is gone (the link redirects to RoverPass's Kanarraville index) and "
            "no website was found", LIVE),
    12465: (f"no live web presence: {ASLEEP}; campsitepros.com answers 404 and Harvest Hosts lists the park closed all "
            "year; no phone on record", LIVE),
    14231: (f"no live web presence: {GONE.format('Maryland')}; no website or booking site found, only directory pages "
            "(Campendium, ParkAdvisor) and the pinecliffresort.net content farm", LIVE),
    5319: ("no live web presence: greensquietacre.com is a bare booking form (no rates, phone, address or description "
           "of the sites) whose card payment is wired to a Stripe test key, and the Hipcamp listing its note named is "
           "gone; no other booking site found", LIVE),
    7877: ("no live web presence: trianglervpark.com answers 403 Forbidden (the Wayback Machine's last good capture, "
           "with rates and (806) 433-5671, is from 2025-07-14), and its Hipcamp page is an unclaimed 'Coming soon' "
           "listing", LIVE),
    4798: ("over the price limit: $65 a night with electric on the park's rates page (campcentralrvparks.com/rates); "
           "nearest gateway Walt Disney World, 59 km", OVER),
    7547: ("over the price limit: $60-70 daily on the park's rates page (happycamprvpark.com/rates); nearest gateway "
           "Houston, 72 km", OVER),
}
# (id, old link, new link or None)
LINKS = [
    (3380, "https://www.hipcamp.com/en-US/land/wisconsin-eagle-view-rv-camp-9mxhn5zw", None),
    (5301, "https://www.hipcamp.com/en-US/land/arkansas-grassy-road-cabins-and-rv-camping-06yhpdq5",
     "https://app.fireflyreservations.com/reserve/property/GrassyRoadCabinsandCamping"),
    (11558, "https://www.hipcamp.com/en-US/land/arizona-liberty-haven-ranch-ozxhdelp", None),
]
NOTES = {  # id: (old note, new note); a note that names a Hipcamp channel is rewritten whole
    3380: ("Small private campground at W16270 Cty Rd D, ~8.5 mi east of Chetek (Rusk County). 24 full-hookup sites "
           "(30/50 amp) plus a few overnight/pull-through sites; sites 12/13/15 are daily transient ~$40/night FHU. "
           "Off-lake (lakes nearby, not on water). Opens ~end of April. Booking by phone/email; also on Hipcamp. "
           "23-ft fits. Coords are RV Life's approximation - verify precise pin. (RV Life 5.0 star, $$). --Claude",
           "Small private campground at W16270 County Road D, about 8.5 miles east of Chetek (Rusk County), between "
           "the Chetek and Island Chain of Lakes but not on the water. 24 full-hookup sites (30/50 amp), most of them "
           "seasonal, plus 3 overnight sites and one pull-through; the daily sites are 12, 13 and 15, at $40 a night "
           "with tax. Restrooms, hot showers, coin laundry and Wi-Fi. Opened for 2026 on April 30. Reserve by phone "
           "or email; credit cards aren't accepted. A 23-ft rig fits. The map pin is RV Life's approximation. RV "
           "Life 5.0 stars, $$. --Claude"),
    5301: ("Privately owned 23-acre property near the Buffalo National River at Marshall (8597 AR-27). 10 full-hookup "
           "RV sites with 20/30/50 amp water/sewer, level gravel pads; plus 8 tent sites, 2 cabins, bathhouse, "
           "stocked fishing pond. Booked via Hipcamp and Airbnb. --Claude",
           "Privately owned 23-acre property near the Buffalo National River at Marshall (8597 AR-27). 10 full-hookup "
           "RV sites with 20/30/50 amp water/sewer, level gravel pads; plus 8 tent sites, 2 cabins, bathhouse, "
           "stocked fishing pond. RV sites start at $45 a night, booked online through the park's Firefly "
           "reservations page. --Claude"),
    11558: ("Small camping area on a 175-acre private desert ranch in Morristown, between Wickenburg and Phoenix. 4 RV "
            "hookup sites (water + 30-amp) plus open dry-camping/boondocking space with water available; graded "
            "desert-ranch road access, drive-in. Booked via Hipcamp or direct. --Claude",
            "Small camping area on a 175-acre private desert ranch in Morristown, between Wickenburg and Phoenix. 4 "
            "RV hookup sites (water + 30-amp) plus open dry-camping/boondocking space with water available; graded "
            "desert-ranch road access, drive-in. Reserve by phone after checking the ranch's online availability "
            "calendar; its website posts no current rates. --Claude"),
    2858: ("Small RV park / glampground on a 40-acre homestead in the Pine Ridge badlands near Crawford and Fort "
           "Robinson, backing to the Oglala National Grassland. A handful of full-hookup back-in/pull-through sites "
           "(30/50 amp); call ahead, few spots. Seasonal (roughly mid-May to mid-October). Also listed on Hipcamp. "
           "--Claude",
           "Small RV park / glampground on a 40-acre homestead in the Pine Ridge badlands near Crawford and Fort "
           "Robinson, backing to the Oglala National Grassland. A handful of full-hookup back-in/pull-through sites "
           "(30/50 amp); call ahead, few spots. Seasonal (2026: May 15 to October 17). --Claude"),
    5114: ("Secure gated facility within Starkville city limits offering a small number of overnight full-hookup RV "
           "slabs (13x50 concrete, 50-amp, water, sewer, picnic table & fire pit), popular for Mississippi State "
           "ballgame weekends. 24/7 gated access. Reservable online; also bookable via Hipcamp.",
           "Secure gated facility within Starkville city limits offering a small number of overnight full-hookup RV "
           "slabs (13x50 concrete, 50-amp, water, sewer, picnic table & fire pit), popular for Mississippi State "
           "ballgame weekends. 24/7 gated access. $40 a night; call or text to reserve."),
    7234: ("City of Quitman park (27 ac); ~20 back-in RV sites with electric/water (some cable TV), dump station, "
           "playground/splash pad. Reservable (Hipcamp) or call the city. Named for TX Gov. J.S. Hogg. --Claude",
           "City of Quitman park (27 ac); 20 back-in RV sites with electric, water and cable TV, dump station, "
           "playground/splash pad. Nightly and monthly sites are reserved through the city's application forms, or "
           "call the city. Named for TX Gov. J.S. Hogg. --Claude"),
}
FEES = {  # id: (fees, provenance)
    3380: ({"nightly_low": 40, "nightly_high": 40, "currency": "USD", "checked": "2026",
            "note": "Daily full-hookup sites (12, 13 and 15) $40 a night, tax included; seasonal sites by quote. The "
                    "park opened for the 2026 season on April 30. Read 2026-10-14."},
           {"source": "https://www.eagleviewrvcampllc.com/ ('Sites 12, 13, 15 are daily sites.'; 'Daily - $40 per "
                      "night full hook-ups*'; '* All rates include tax'; 'Seasonal - Call or email for prices'), read "
                      "2026-10-14", "checked": D}),
    5301: ({"nightly_low": 45, "currency": "USD", "checked": "2026",
            "note": "Full-hookup RV sites (20/30/50 amp) start at $45 a night; electric tent sites from $30 and "
                    "primitive tent sites from $22. The page gives no year. Read 2026-10-14."},
           {"source": "https://www.grassyroadcamping.com/rv-tent ('Enjoy wide, level full-hookup RV sites with "
                      "20/30/50 amp service, water, and sewer'; 'Starting at $45 per night.'), read 2026-10-14",
            "checked": D}),
    5114: ({"nightly_low": 40, "nightly_high": 40, "currency": "USD", "checked": "2026",
            "note": "Overnight RV parking with 30/50-amp, water and sewer: $40 daily, $180 weekly, $280 bi-weekly, "
                    "$500 monthly. The page gives no year. Read 2026-10-14."},
           {"source": "https://www.morelandstorageunits.com/overnight-rv-camping-and-parking ('Overnight RV parking "
                      "includes a 30 and 50 AMP breaker, sewage, and water hookups.'; 'daily - $40'; 'weekly - "
                      "$180'), read 2026-10-14", "checked": D}),
}
IE = f"re-check {D} (AWH #8, Hipcamp links)"
IE_ADD = {
    3380: (f"{IE}: dead Hipcamp link removed (asleep, imported by Hipcamp and never claimed); the operator's site "
           "posts the daily rate ($40 with tax) and 715-642-1391, so it stays (#5)"),
    5301: (f"{IE}: Hipcamp listing gone, link replaced by the park's Firefly booking page; its own site posts 'Starting "
           "at $45 per night' and 919-922-1030, so it stays (#5)"),
    11558: (f"{IE}: dead Hipcamp link removed (asleep, imported by Hipcamp and never claimed); libertyhaven.com is live "
            "with (623) 640-7880 and an availability calendar but posts no current rates (its old rate table is "
            "commented out of the page) - kept pending AWH's call on phone-only websites"),
    2858: (f"{IE}: no Hipcamp listing exists, so the note's 'Also listed on Hipcamp' is gone; its own site books "
           "online and posts 308-665-2592"),
    5114: (f"{IE}: no Hipcamp listing exists, so the note's Hipcamp booking claim is gone; its own page posts $40 "
           "daily and 662-769-4892 (call or text)"),
    7234: (f"{IE}: no Hipcamp listing exists, so the note's Hipcamp booking claim is gone; quitmantx.org/parks takes "
           "nightly and monthly RV applications and posts (903) 763-2223"),
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
for i, old, new in LINKS:
    e = by[i]
    links = (e.get("website") or "").split("\n")
    if old in links:
        links[links.index(old)] = new
        links = [x for x in links if x]
        assert links, i
        e["website"] = "\n".join(links)
        print("link", i, old.rsplit("/", 1)[-1], "->", new)
for i, (old, new) in NOTES.items():
    e = by[i]
    if e["note"] != new:
        assert e["note"] == old, (i, e["note"])
        e["note"] = new
        print("note", i, e["name"])
for i, (fees, prov) in FEES.items():
    e = by[i]
    if e.get("fees") != fees:
        assert not e.get("fees"), (i, e.get("fees"))
        e["fees"] = fees
        e.setdefault("provenance", {})["fees"] = prov
        print("fees", i, fees.get("nightly_low"), fees.get("nightly_high"))
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
