# Split check: 3341 Franklin Lake Campground (Chequamegon-Nicolet NF, WI), 2026-11-17

## Decision: NO SPLIT
The North and South loops stay together in 3341. No `parent_3341.json` or `new_*.json` was written, and the entry is unchanged.

Why:
- **No entrance of its own.** Both loops are on the same paved road, FR 2181 (Butternut Lake Road). FR 2181 runs through the South campground, and its loop roads 2181F/G/H branch off it there. The road then continues ~430 m and ends in the North loop. The North loop has no road of its own: its sites line the last ~1 km of FR 2181. Anyone going to the North loop drives through the South campground, so the North loop fails the rule's "own entrance or road" test ("it shares the main road").
- **Distance is only at the threshold.** The centroids are 1.03 km apart. They reach 1 km only because the North loop is a 1-km string of sites along the shore. The nearest sites are 395 m apart.
- **The agency treats it as one campground.** The FS page calls it "two camping loops with a total of 77 campsites" ("37 campsites on North End; 40 campsites on South End"), with toilets and water "throughout the campground". There is one fee schedule, one office and one set of directions "to the campground".
- **It is not the booking exception.** The rec.gov search shows a single facility, 233774. The FS page does say "Franklin Lake North Campground" and "Franklin Lake South Campground" in its site tables, but they are loops of that one facility.

The curation doc's "adjacent named loops of one campground area stay one entry" applies.

## Measurements
Site coordinates come from the recreation.gov campsite search, `https://www.recreation.gov/api/search/campsites?fq=asset_id:233774`, read 2026-11-17: 76 sites (South 39, North 37). Distances are haversine.
- South centroid (sites 001-040): **45.93117,-88.99348**.
- North centroid (sites 041-077): **45.93931,-88.98702**.
- **Centroid to centroid: 1.03 km (1,033 m).**
- Nearest sites: South 017 to North 077, **395 m**.
- Distance from the South centroid to each North site:
  - South end (077, 042, 041, 076): 554-621 m.
  - East-shore sites 046-057 at the far end: 1.10-1.33 km.
- Along FR 2181 (USFS EDW roads layer, route 2181 BMP 3.20-5.88), measured from where the layer starts in the query box:
  - Entry pin: 2.37 km.
  - South campground: ~2.68-2.87 km (site 040 to site 017).
  - Gap with no sites: 0.43 km.
  - North loop: 3.30 km (site 077) to the road's end at 4.32 km (turnaround at ~45.9416,-88.9850).
- Pins:
  - The stored pin 45.9283,-88.9938 sits on FR 2181, ~100 m south of site 002 and 321 m from the South centroid.
  - The FS page's own lat/long, 45.93139,-88.99306, is 41 m from the South centroid.

## Sources (all read 2026-11-17)
- recreation.gov
  - `https://www.recreation.gov/api/camps/campgrounds/233774`: one facility, "FRANKLIN LAKE", 77 sites, 34 FCFS and 43 reservable. Directions: "Butternut Lake Road/Forest Road 2181 ... approximately 4 miles to the campground".
  - Campsite search API (above): a loop label and coordinates for each site.
  - Search API `api/search?q=Franklin Lake` (10-mile radius): only 233774 at this lake.
- FS page: https://www.fs.usda.gov/r09/chequamegon-nicolet/recreation/franklin-lake-recreation-area
  - "two camping loops with a total of 77 campsites".
  - "37 campsites on North End; 40 campsites on South End".
  - Reservable sites listed under "Franklin Lake North Campground" and "Franklin Lake South Campground".
  - Site lengths per loop; one fee table; directions "travel 4.6 miles to the campground".
  - Current Conditions: the campground is closed for the season; the boat landing is open.
- USFS EDW roads layer: `https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_RoadBasic_01/MapServer/0/query` over the box 45.927-45.945, -89.000 to -88.980.
  - 2181 BUTTERNUT LAKE ROAD: arterial, paved, 2 lanes, maintenance level 4. Its geometry runs through the South campground and ends in a turnaround at the north end of the North loop.
  - 2181F, 2181G and 2181H, "FRANKLIN CG LOOP 2/3/4", are the South campground's loop roads, all branching off 2181 at ~45.9304-45.9323.
  - 2181D is a 0.07-mile spur at 45.9268,-88.9953, south of the campground.
  - The layer shows no road of its own for the North loop.

## Imagery and maps read (each Read rendered pixels)
Site points from rec.gov were drawn on each frame with my own lat/lng grid.
- Esri World_Imagery at 45.9355,-88.9905, 900 m half-width: both loops and the shore. The North loop is a single strip of sites along the east shore. Continuous canopy hides the roads.
- Esri World_Imagery at 45.9330,-88.9930, 350 m half-width: the South campground and the gap. There are cloud patches, and the roads are not resolved under the trees. The gap between the loops is continuous forest with no visible facility.
- USGS NAIP (USGSImageryOnly), 900 m half-width: leaf-on, full canopy; no roads visible.
- USGS Topo at 900 m, 1400 m and 3000 m half-width: FR 2181 enters from the SW, passes through the South loop (the campground symbol is there) and continues NNE along the shore to the North loop.

These confirm the EDW geometry. Imagery was not needed for a waterfront call because the entry is not changing. The 2026-11-17 verifier's lakeview call (verify_scan) stands.

## For AWH
- **This is the borderline case.** The centroids meet the ~1 km measure by 33 m, but the North loop hangs off the same road at its dead end, past the South campground. If AWH wants it split anyway, the values are ready:
  - North: 37 sites (041-077), centroid 45.9393,-88.9870. All non-electric. rec.gov tags 058-077 "Lakefront".
  - South: 39 sites (001-040), centroid 45.9312,-88.9935. Electric at 001, 012-016, 018, 020, 023, 025 and 028-040.
  - A split would need its own waterfront and imagery pass for each loop.
- **Optional pin tidy-up, not made here.** The stored pin is on FR 2181 ~100 m south of the first site. The FS's own point (45.93139,-88.99306) is inside the South loop. I made no change because the task was the split decision only.

## Refusals
- **overpass-api.de refused (HTTP 406)**, so it joins the refused list.
- I then started one query to a second Overpass instance (overpass.kumi.systems). It returned nothing; I stopped it before any response and did not use it. I note it here because that was a second route to a refused service, and I should not have tried it.
- The roads came from the USFS EDW layer instead, which is the agency's own data.
- No other site refused. No browser was started.
