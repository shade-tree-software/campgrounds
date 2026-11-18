# Split: 3291 Interstate State Park (Polk County, WI), 2026-11-17

## Decision: SPLIT
- 3291 keeps the **North campground** (sites 1-40): `parent_3291.json`. The existing pin is on it, and it is the electric/shower campground the entry's data mostly describes.
- The **South campground** (sites 41-85) becomes a new entry: `new_interstate_south.json`.
- Apply: `python3 -I audit/verify/kit/wi/splits/apply_split.py 3291 new_interstate_south.json [--apply]`. A dry run printed 3291 North and a new id 15708 South.

## Sources (all read 2026-11-17)
- DNR camping page https://dnr.wisconsin.gov/topic/parks/interstate/recreation/camping:
  - "two campgrounds and a primitive group camp"; "a total of 82 family campsites".
  - "The north campground is open May 1 through Oct. 31. The south campground and group camp are open throughout the year."
  - "Shower facilities are available in the north campground for registered campers. There is a dump station across the road from the Ice Age Center."
  - "The south campground is available for hike-in, tent camping only from Nov. 15 through April 30. There is parking available outside of the south campground gate."
  - "No refunds will be issued for RV/motorized campers who make reservations for the south campground from Nov. 15 through April 30."
  - "Water is available at the Ice Age Interpretive Center when the center is open."
- DNR North campground map (https://widnr.widen.net/s/smhxtqhncp/interstate_north-campground-map, PDF from the Widen preview, rendered):
  - Sites 1-40 with no 10, 21 or 22 = 37.
  - E on 1-9, 12-14, 16-20, 26-29, 31-36 = 27 electric.
  - 24 and 25 walk-to; 32E accessible.
  - Shower building, flush toilets, vault toilet, drinking water.
  - Layout: a loop, a spur to 37-40 ending in a turnaround, and a road north to 23-25.
- DNR South campground map (https://widnr.widen.net/s/5zcp7xjr5d/interstate_south-campground-map, rendered):
  - Sites 41-85 = 45, one long loop.
  - Legend: vault toilets, drinking water, recycling only. No E marks.
- DNR park map PUB PR-256M 2025 (https://widnr.widen.net/s/zdklkb2rz7/interstate_mapgeopdf, rendered):
  - North Campground north of US 8 beside the St. Croix.
  - South Campground SW of Lake O' the Dalles, south of Dalles Creek.
  - The park road from the Hwy 35 entrance serves both. The North road leaves it by the Pothole Trail lot and runs under US 8; the South road leaves it at the lake's outlet.
- OSM API (api.openstreetmap.org /api/0.6/map, two small bboxes; not Overpass), used for geometry:
  - North loop: service ways 208035751, 300590918, 300726275, spur 208035750. Entrance 208035752 runs from Park Road at 45.40006,-92.64727.
  - South Campground polygon 1570084613; loop way 21553742; access 793320361 runs from 45.39241,-92.65754, the Dalles Creek bridge at the lake outlet.
  - Dalles Creek 59937420; St. Croix 34461747 / 1496540967.
- Open-Meteo DEM: South pin 45.3895,-92.6639 = 221 m. North pin 45.4036,-92.6484 = 214 m (unchanged).
- DNR fees: the camping FAQ gives no per-site rates ("Site rates are visible when you select the site").

## Measured distances (haversine)
- Site-area centroids: North (loop + 37-40 spur nodes) 45.40362,-92.64774; South (loop nodes) 45.38945,-92.66386. **2.02 km apart.**
- North loop alone to South: 2.02 km.
- Nearest North road node to nearest South loop node: **1.77 km**.
- Kept pin 45.4036,-92.6484 to the South pin 45.3895,-92.6639: 1.98 km.
- Each campground has its own spur road. The two spurs leave the park road **1.17 km apart**: North at 45.4001,-92.6473 (445 m long, under US 8); South at 45.3924,-92.6575 (541 m long).
- **Meets the rule** (~1 km+, own road). The verifier's "~1.7 km" matches the nearest-road gap, not the centroids.
- The old pin is 52 m from the North site-area centroid, on the loop's west side. Kept.

## Imagery (all rendered and checked)
Esri World_Imagery export with my own lat/lng grid overlay (EPSG:3857):
- 45.398,-92.655 hw 1300 m: the whole park.
  - The first try used imageSR 4326 and the grid came out wrong, because the server pads a non-square bbox. Redone in 3857; no evidence comes from the bad frames.
- 45.4040,-92.6482 hw 300 and 45.4038,-92.6485 hw 160: the North loop in woods north of the US 8 bridge.
  - The St. Croix's east bank is ~40-55 m west of the loop's west road, with a continuous canopy strip between.
- 45.3915,-92.6615 hw 300, 45.3925,-92.6585 hw 550 and 45.3895,-92.6636 hw 230: the South area. The summer canopy hides the loop.

Esri Wayback 2016-04-13 (release 9598, WV02, leaf-off), z18:
- 45.3895,-92.6639: the South loop is plainly visible, running WSW-ENE with two toilet buildings. It matches the DNR map and OSM.
  - The Dalles Creek channel is ~70-90 m north of the north road, through woods.
- 45.4037,-92.6482: the North loop and its grass opening.
  - The river bank to the west is treed, with no open ground between the sites and the water.

## Waterfront
- **North: not waterfront** (unchanged).
  - The west-side sites (30-36) are roughly 30-55 m from the St. Croix through a wooded bank strip, so they are not on open ground.
  - A filtered summer view is possible. Only GoingToCamp's site photos could show it, and that site refuses.
  - Default down. **AWH may want to look:** riverview is plausible for 30-36 if the site photos show the water.
- **South: not waterfront.**
  - Dalles Creek is ~70-90 m north through woods.
  - The St. Croix is ~200 m west.
  - Lake O' the Dalles is ~600 m NE, past the park road.
- The old note said the South campground lies "by the Lake O' the Dalles swimming beach". That is wrong: the beach is on the lake's east shore, ~1.2 km from the South loop. The new notes drop it.

## Field notes
- North:
  - `sites` 37.
  - `facilities`: showers, flush toilets, vault toilets, water, dump. The dump is the park station by the Ice Age Center.
  - `season` 05-01..10-31.
- South:
  - `sites` 45.
  - `hookups.electric` 0: the map has no E marks and no electric legend item.
  - `facilities`: vault toilets, water, dump (the park station, as in the Sidie Hollow precedent). Showers are left absent, and the group note says registered campers use the North showers.
  - `season` 05-01..11-14 (RV season), with a note on winter tent-only camping.
- **Fees:** 3291 keeps the 2026-10-10 GoingToCamp range of $18-36. Its note now says this is park-wide and not split by campground. **South gets no fees**: its own rates are unread, and GoingToCamp refuses.
- **Hookups on 3291 are unchanged** (electric 50, derived from old note prose). The amperage is unverified.
- `booking` is unchanged on 3291. South has none, because the state:WI policy row covers it.
- **RV fit at South:** GoingToCamp's 54 RV-capable sites park-wide exceed North's 35 drive-in sites, so at least 19 South sites take RVs. Per-site lengths are unread. The DNR does not single South out for small rigs, so no caveat.
- No rating or discounts on the entry, so there is nothing to divide.

## Not done / refused
- wisconsin.goingtocamp.com: on the refusal list; not tried by any route.
- No other site refused. No browser started. No git commands.
