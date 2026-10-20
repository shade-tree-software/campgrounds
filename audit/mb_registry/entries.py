#!/usr/bin/env python3
"""Correct Manitoba Parks booking facts against the 2026 operating-dates list (2026-10-20).

    python3 -I audit/mb_registry/entries.py [--apply]

Manitoba's 2026 Operating Dates PDF gives every campground a "Reserve a site beginning / until"
pair, or none. Read against it and against the goingtocamp catalog (manitoba.goingtocamp.com
/api/resourceLocation, whose per-location resource categories say whether CAMPSITES are rented
or only group sites), eight entries had the wrong answer, all derived from sweep note prose:
seven claimed reservations that Manitoba does not take, and Camp Morton's campsites, recorded as
first-come, are reservable. Each note is rewritten to say what the list says. Falcon Creek (9363)
is on neither list and is held for AWH; its unsupported booking claim is removed meanwhile.
Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CG = os.path.join(ROOT, "campgrounds.json")
SRC = ("https://www.gov.mb.ca/sd/pubs/parks-protected-spaces/operating_dates.pdf (2026); "
       "manitoba.goingtocamp.com resource locations")
PROV = {"source": SRC, "checked": "2026-10-20", "method": "manual"}
FCFS = {"reservable": False, "fcfs": "always"}

FIX = {
    9322: (FCFS, "Small Manitoba provincial park in the Porcupine Hills boreal forest, ~18 km W of Birch River on PR 365, on Bell Lake. 8 unserviced drive-in sites, boat launch, playground and picnic area; good walleye/pike fishing. First-come, first-served: Manitoba's 2026 operating dates list Bell Lake campsites (May 15-Sept 20) with no reservation dates, and it is not in the reservation system. --Claude"),
    9325: ({"reservable": True}, "Manitoba provincial park on the Lake Winnipeg shore 8 km N of Gimli on PR 222. 19 drive-in campsites suitable for tents/trailers/RVs, plus 14 family cabins and 6 yurts; water hookups, dump station, toilets, beach access. Campsites, cabins and yurts are all reservable through the Manitoba Parks Reservation Service (2026: May 15-Sept 19; campground open to Sept 20). --Claude"),
    9331: (FCFS, "Small Manitoba Parks campground on Singush Lake in Duck Mountain PP (east of the main lakes off PR 367); basic sites with a short access road to the lake shore and a boat launch. Drive-in RV access confirmed on satellite. First-come, first-served: the 2026 operating dates list Singush campsites (May 15-Oct 12) with no reservation dates. --Claude"),
    9334: (FCFS, "Manitoba Parks campground (~50 well-treed basic/non-electric sites) on Iskwasum Lake at a wide section of the Grass River, in Grass River PP near Cranberry Portage. No power/water/sewer hookups; solar gravity-fed showers, dump, boat launch/dock, swimming beach, playground. Drive-in RV access. First-come, first-served: the 2026 operating dates list Iskwasum campsites (May 15-Oct 12) with no reservation dates. --Claude"),
    9335: (FCFS, "In Grass River Provincial Park on Reed Lake, ~74 km N of The Pas off Hwy 39. 58 unserviced drive-in sites (no hookups; generator use OK), water fill and sani-dump station, boat launch, beach, fish-cleaning station, playground. First-come, first-served: the 2026 operating dates list Reed Lake campsites (May 15-Sept 7) with no reservation dates. --Claude"),
    9336: (FCFS, "In Grass River Provincial Park on the south shore of Simonhouse Lake, ~75 km N of The Pas. 50+ unserviced drive-in sites (no hookups), the park's accessible beach, boat launch, playground, solar showers, sani-dump. First-come, first-served: the 2026 operating dates list Gyles campsites (May 15-Sept 7) with no reservation dates. --Claude"),
    9355: (FCFS, "Max Lake Campground in Turtle Mountain Provincial Park — a small basic (unserviced) drive-in campground on Max Lake, offered on a daily or seasonal basis; fire pits, near swimming and trails, dump station in the park. Campsites are first-come, first-served (2026: May 8-Sept 13, no reservation dates); only the group-use area is reservable. --Claude"),
    9358: (FCFS, "Manitoba Provincial Park in the Porcupine Hills boreal forest on Whitefish Lake near Birch River. About 81 non-electric (basic) sites for tents and RVs/trailers to ~30 ft; washrooms, water taps, dump station, beach and boat launch. First-come, first-served: the 2026 operating dates list Whitefish Lake campsites (May 15-Sept 20) with no reservation dates. --Claude"),
    9363: (None, "Basic campground set in forest near the Falcon Lake townsite and golf course in the Whiteshell, just off the Trans-Canada Highway. CAVEAT (2026-10-20): no campground of this name is on Manitoba Parks' 2026 operating dates, its reservation system or the Whiteshell campground maps, and the pin shows a small loop of cabins and trailers rather than the 'wooded loops' described; whether it is a public campground at all is unconfirmed. --Claude"),
}

cg = json.load(open(CG, encoding="utf-8"))
for e in cg:
    if e["id"] not in FIX:
        continue
    booking, note = FIX[e["id"]]
    print(e["id"], e["name"], e.get("booking"), "->", booking)
    e["note"] = note
    if booking is None:
        e.pop("booking", None)
        e.get("provenance", {}).pop("booking", None)
    else:
        e["booking"] = dict(booking)
        e.setdefault("provenance", {})["booking"] = dict(PROV)
if "--apply" in sys.argv:
    with open(CG, "w", encoding="utf-8") as f:
        json.dump(cg, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("written")
