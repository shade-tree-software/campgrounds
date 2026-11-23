# 5751 Pickerel Lake Recreation Area: split the East Campground from the West Campground (2026-11-22)

## Decision
SPLIT. The East Campground becomes its own entry (`new_pickerel_east.json`, one entry). The id stays on the West
Campground: the stored pin (45.5022,-97.2803) was already inside it, 39 m from its RV-site centroid.
`parent_5751.json` re-cuts the kept entry and moves the pin to that centroid.

`trips.campground_references(5751)` returned `[]`, so no trip references the entry. The id stays on the
campground the pin marks.

## Why it passes the split rule
- **Distance (measured):** haversine over the engine's per-unit coordinates, using web-bookable RV sites only
  (no hosts, cabins or the group shelter).
  - West Campground (loop 83): 34 sites, centroid 45.50232,-97.27984.
  - East Campground (loop 82): 29 sites, centroid 45.48415,-97.26246.
  - Centroid to centroid: **2,432 m**. The nearest pair of sites across the two (13E and 44E) is **2,211 m** apart.
  - The verifier's hint (45.4842,-97.2624) matches the East centroid.
  - GFP's park "GPS Coordinates" (45.48555,-97.24813) are 1,128 m east of the East centroid, near the East
    entrance. They are not used as a pin.
- **Separate places, each with its own road:**
  - West is on the lake's wooded north shore. Its own road runs from 446th Ave / 130th St past its own entrance
    booth and dump station (GFP West map).
  - East is on the east shore, across the lake. Its own entrance booth is on the east side by Hwy 6, and its road
    winds about 2 km west past its dump station and fish-cleaning station to the loops (GFP East map). Read off
    the 1,500 m overview imagery too.
  - GFP publishes two separate maps, "PICKEREL LAKE WEST CAMPGROUND" and "PICKEREL LAKE EAST CAMPGROUND". The park
    page says "2 campgrounds with 65 campsites".
- Both campgrounds are on one engine facility (facID=47) but in separate loops (83 West, 82 East). The rec.gov
  exception is not needed: the distance rule alone is met.

## Sources (all read 2026-11-22, plain curl with UA Mozilla/5.0, no bot walls)
- **GFP park page**, https://gfp.sd.gov/parks/detail/pickerel-lake-recreation-area/:
  - Rates: "Campsites - electrical: $30 per night", camping cabins $60, modern cabins $150. No non-electric rate.
  - "Open: Year-round. Between Oct. 1 and April 30, showers, flush toilets and other water systems may be closed
    ... Vault toilets usually remain open."
  - "2 campgrounds with 65 campsites, 7 camping cabins, and 1 modern cabin"
  - "Located 10 miles north of Waubay off US Hwy 12"; nearest town Grenville.
  - Phone 605.910.4515; reservations online or 1.800.710.2267. Amenities list.
- **GFP maps** (both rendered at 110 dpi and read; PDFs deleted after use):
  - https://gfp.sd.gov/userdocs/pickerel_w_cg.pdf (ArcGIS Pro, modified 2024-06-28). Sites 1E-41E, cabins 1-4,
    modern cabin, host V1. Restroom/shower by 1E, vault toilet by 24E, water hydrants, playground, picnic shelter,
    dump station by 38E. Entrance booth on the road from 446th Ave; swim beach and boat ramp at the NW day-use area.
    This older map prints the phone as 605.910.4465.
  - https://gfp.sd.gov/userdocs/pickerel_e_cg.pdf (ArcGIS Pro, 2025-03-17). Sites 44E-72E, cabins 5-7, host V2.
    Restroom/shower by V2, vault toilets by 51E and 64E, water hydrants, playground. Dump station, fish cleaning,
    boat ramp, boat wash, kayak launch, swim beach and fishing pier. Entrance booth on the east side.
    Phone 605.910.4515.
- **Go Outdoors SD engine**, https://reservations.gooutdoorssouthdakota.com/FacilityDetails.aspx?facID=47. Parsed
  `var sitesHashMap`: 83 units (74 active).
  - **Loop 83 (West):**
    - 34 ReservableOnline RV sites 1E-41E. These numbers are absent: 4E, 15E, 21E-23E, 39E, 40E.
    - Pull-thrus 16E (115 ft), 20E (135 ft) and 35E (90 ft); the rest are back-ins.
    - All "Amp Service: 50", $30. MaxEquipLength 45-135 ft.
    - Also: cabins C1-C4 ($60), modern cabin MC ($150), group shelter PS ($20), and host V1 ("Host Site", not
      online).
  - **Loop 82 (East):**
    - 29 RV sites 44E-72E, all "Back-In Campsite", "Amp Service: 50", $30. MaxEquipLength 55-85 ft (85 at 62E).
    - The 75-ft values on 59E/61E/64E/70E/72E sit among varied neighbours (55-85) and were not needed for the max.
    - Also: cabins C5-C7 ($60) and host V2 (not online).
  - Loop 153 holds 9 inactive equipment-rental units. No unit carries BlackoutDateRanges.
  - 63 sold sites plus hosts V1 and V2 = GFP's 65.
- **Engine reviews**, https://reservations.gooutdoorssouthdakota.com/FacilityReviews.aspx?facID=47 (read 2026-11-22):
  - Several 2026 reviews (5/20, 5/29, 6/10 and an undated West one) report tree branches overhanging the roads and
    sites in both campgrounds that scrape camper roofs, sides, vent covers and AC units. This is put in both notes
    as a reviewer caveat. No agency statement and no posted clearance, so it is not a drop.
  - A 7/22/2026 review mentions "gorgeous lake views" without naming a campground, so it was not used.
- campgroundviews.com was looked at: an aggregator with no reviews and a wrong GPS. Not cited.
- **Open-Meteo elevation:** West centroid 573 m, East centroid 571 m, overview centre 574 m, old pin 574 m.

## Imagery (Esri World_Imagery export via audit/verify/kit/mn/tools/satpts.py, unit points plotted)
Every frame rendered, and all were deleted after use.
- **Overview, 1,500 m half-width, centred 45.4932,-97.2711:** West at the lake's north shore and East on the east
  shore 2.4 km SSE, across open water. East's own road winds in from the east.
- **West Campground:**
  - 220 m frame: a branching loop of gravel pads. The north rows face the lake.
  - 110 m frame (0.24 m/px): pad ends of 27E, 29E, 31E, 33E, 34E and 36E sit ~11-20 m from the canopy edge over
    the water. A continuous belt of shore trees runs between them and the lake, with grass under the trees but no
    open apron.
- **East Campground:**
  - 200 m frame (0.44 m/px) and 110 m frame: the west rows face the lake. 49E is ~20 m from the water, 51E ~21 m,
    48E ~38 m, 56E ~31 m and 57E ~35 m, all behind a continuous wooded shore belt. The east loop (59E-72E) sits
    further inland.

## Waterfront calls
- **West: lakeview** (unchanged). North rows 27E-36E have a filtered view through a continuous shore tree belt.
- **East: lakeview.** Rows 48E-58E look through 20-38 m of shore woods, read the same way as Roy Lake East (5742).
  This is the weaker of the two calls: no site photo confirms the view. If AWH wants a confirmed view for a
  20-m wooded fringe, it would go down to not waterfront.

## Re-cuts on the kept entry (parent_5751.json)
- **Name:** "Pickerel Lake Recreation Area (West Campground)".
- **Location:** moved 39 m to the RV-site centroid. **Elevation:** 573 m.
- **Rewritten for the West Campground alone:** waterfront_evidence, inclusion_evidence and note.
- **Sites:** 63/135/pull_through true becomes **34/135/true**. The pull-thrus and the 135-ft site are all West.
- **Hookups (50 A) and facilities:** values unchanged, provenance re-sourced to the West map and loop.
- **Unchanged:** website (the GFP park page plus facID 47 is still the best page), phone 605.910.4515, rating,
  season, booking and fees. Provenance for season, booking and fees was rewritten for the West Campground.

## New entry (new_pickerel_east.json)
- "Pickerel Lake Recreation Area (East Campground)", pinned at 45.48415,-97.26246, elevation 571 m, ownership
  state.
- 29 RV sites, 85 ft max, no pull-thrus, 50 A, full facilities, year-round season with the winter-water note.
- Booking and fees are the same park-wide GFP facility and schedule as 5751: 23 + $7 electric = the $30 every
  East unit prices at.
- RV Life rating not copied: the listing is park-level. Absent means unknown.

## For AWH
- East's lakeview rests on imagery of a 20-38 m wooded fringe, the Roy Lake East precedent (see above).
- Both notes carry the 2026 reviewers' warning about overhanging branches. Several of those reviews are from the
  same reviewer; the West one is separate.
- The West map (2024) prints 605.910.4465. The park page and East map (2025) say 605.910.4515, which is kept on
  both.
- West's 20E pull-thru is listed at 135 ft in the engine (also the stored max). It is kept as the engine's figure.
