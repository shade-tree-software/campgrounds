# 4392 David Crockett State Park (TN) - split decision

**Decision: SPLIT.** Two campgrounds ~1.74 km apart, each with its own road off the park road, its own bathhouse(s), dump station, host site and playground:
- **4392 kept → "David Crockett State Park - Campground 2"** (sites 46-97, year-round, hilltop). It's the larger (52 of 96 sites) and matches the stored `season.year_round`; the stored pin (35.25793,-87.35422) was 669 m from it and 1,228 m from CG1. No trip references 4392 (`trips.campground_references(4392) == []`).
- **New → "David Crockett State Park - Campground 1"** (sites 1-45, no 29; seasonal; on Shoal Creek).

## Measurements
- CG1 centroid: mean of the 44 site positions on the official campground map, georeferenced to the bathhouse (35.2487,-87.34851) → 35.2479,-87.34857. Pin 35.24770,-87.34830 is on the loop by the creek row (inside the site cluster).
- CG2 centroid: centre of the three loops in Esri z18 at 35.2597,-87.3612 → 35.25966,-87.36128 (pin).
- Haversine CG1-CG2 centroids: **1,744 m** (the task's hint points: 1,807 m).
- Elevation (Open-Meteo): CG1 pin 251 m, CG2 pin 306 m. (3DEP: CG1 pads ~242.6-245 m, CG2 ~290 m. Open-Meteo's coarse DEM reads high in CG1's narrow creek valley; written per the rule.)
- 3DEP transects east from CG1's creek row (bare-earth lidar):
  - Site 24 (lat 35.24754): pad 242.6 m; water surface 240.6 m from ~17 m to ~31 m out; bluff rises from ~35 m.
  - Site 22 (lat 35.24799): water from ~14-18 m (a 2.3 m drop).
  - Site 25 (lat 35.24724): water from ~9 m.
  - Site 20 (lat 35.24838): water from ~27 m. Not counted, because its official photo shows the stone wall and bluff with no water.
  - The channel is ~15 m wide, under 30 m, so the call is **creekside**.

## Waterfront
- **CG1: creekside, sites 22-25** (upgraded from the stored "not waterfront", which judged the old in-between pin).
  - Evidence: the official per-site map places 22-25 between the loop road and Shoal Creek, the official reservation photos of 22, 23, 24 and 25 each show the pad ending at a rail with water just beyond, and the lidar above.
  - Not counted: 26-27 (wooded, no water in photo), 13-21 (stone wall/bluff), and the inner-loop sites.
- **CG2: not waterfront.** Wooded hilltop, and neither the imagery nor the official map shows water near any loop.

## Sources (all read 2026-11-24)
- https://tnstateparks.com/parks/david-crockett/camping (the stored /parks/campground/david-crockett redirects here). Key quotes:
  - CG1 "sits along Shoal Creek and is open March 1 - November 3".
  - CG2 "features paved campsites ... open year-round".
  - "Campground 1 has 32 campsites with 30-amp electric and 12 campsites with 20-30-50 amp electric. Campground 2 has all 20-30-50 amp electric hookups."
  - Bathhouses with hot showers; a dump station.
  - Office 931-903-2323.
- Official campground map: https://tnstateparks.com/sites/default/files/2025-10/David_Crockett_Campground_web.png (rendered, read).
- https://reserve.tnstateparks.com/david-crockett/campsites, Calendar View (plain POST, no captcha). Every site's attributes and nightly price for two weeks from 2026-11-25, 2027-01-12, 02-24, 03-16, 05-25, 06-29, 09-01 and 10-27, plus the site photos for 16, 20 and 22-27.
  - CG1 sells 11/25-11/30/2026, shows nothing 12/1/2026-2/28/2027, and sells from 3/1/2027 through at least 11/10/2027.
  - CG2 is priced and bookable on every winter night read.
- Imagery: Esri World Imagery, all frames rendered and read:
  - ov15 (35.2533,-87.3548, z15)
  - cg1_17 (35.2472,-87.3483, z17)
  - cg1_18 (35.2475,-87.3485, z18)
  - cg2_17 (35.2595,-87.3613, z17)
  - cg2_18 (35.2597,-87.3612, z18)
  - Official site-photo contact sheet (rendered).

## Re-cut groups
- **CG2 (4392):**
  - hookups 50/water/no sewer
  - sites 52, max 57 ft, all back-in (pull_through false, sourced)
  - showers/flush/dump
  - year_round
  - fees $38-65
  - booking reservable (now manual provenance)
  - `rating` left untouched (park-level RV Life)
- **CG1 (new):**
  - hookups 50/water/no sewer
  - sites 44, max 70 ft (site 24), pull-throughs 22-25
  - showers/flush/dump
  - season 03-01..11-30, with the page/calendar conflict in season.note
  - fees $32-65
  - Booking/reservation fee/tax/discounts are left to the state:TN policy row.
- The old note (both campgrounds) and inclusion_evidence were replaced per campground. No --AWH text existed on 4392.

## For AWH
1. CG1 waterfront upgraded to creekside (sites 22-25 named).
2. CG1 season: the page says closes Nov 3; the engine sells through Nov 30. I wrote 03-01..11-30 with a season.note.
3. The kept id moved to CG2 (the larger campground, year-round).
4. Minor: per the park page, the restaurant closed 2026-06-30 and the museum is closed for repairs from 2026-11-23. Neither is written to the entries.
