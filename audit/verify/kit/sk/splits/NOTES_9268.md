# Split 9268: Palliser Regional Park (SK), 2026-11-19

## Decision

**No split.** Rusty's Coulee Marina (the South Campground) is at a separate place: it is on its own
road, about 2.8 km from the North campground. On its own, though, it fails long-stay test 4. Let's Camp
sells **14 of its 143 numbered sites by the night (9.8%)**, which is under 1 site in 10. The rule
(curation doc, "Long-stay, seasonal and residential parks", test 4) puts a part like that inside the
parent, so it stays in 9268. The entry is unchanged and no parent or new-entry JSON was written.
The stored note already describes both campgrounds and the marina's 14 nightly sites.

The call is marginal. One more nightly site at the marina (15 of 143, 10.5%) would clear test 4,
and the split would then go ahead on distance and road. Re-check if a later Let's Camp list sells more
sites there.

## Measurements

The sites have no GIS points (this is a regional park, not SKPP), so each loop was placed on Esri
World_Imagery against the park's own maps and its centre read from pixels (the frames are listed below).

| South loop (map name) | Sites (park map 2024 = Let's Camp SVG map) | Loop centre |
|---|---|---|
| Pelican Point | 901-925 (25) | 50.86755,-106.93573 |
| Walleye Cove | 601-644 + 620A (45; LC map has 614-2 for 644) | 50.86592,-106.93532 |
| Meadowlark Mesa | 1-22 (22) | 50.86375,-106.94072 |
| 700s, upper loop (store, showers) | 701-730 (30) | 50.86268,-106.94085 |
| 700s, lower loop (launch side) | 731-737, 740-750, 753, 754, 754A (21) | 50.86127,-106.94015 |
| **South, site-weighted** | **143** (+ Group Camping 4) | **50.86448,-106.93816** |

- North campground centre (estimated over its loops on imagery): 50.88816,-106.95262. The stored pin
  is 50.8883,-106.9542, on the north campground.
- **Centre to centre: 2,822 m.** The stored pin is 2,878 m from the South centre. The nearest ends
  (the North's Sunshine Coulee, the 500s, near 50.8878,-106.9479, and the north tip of Pelican Point,
  near 50.8678,-106.9364) are about 2.4 km apart.
- Roads: the North map has the park's Entrance Gate by the Mainstay Inn, with "To Marina Road"
  running south from it. The South map's "To Park Gate" points up the same road. Marina Road runs
  north-east to south-west between Pelican Point and Walleye Cove and ends at the store and launch.
  The two campgrounds share the park gate but not their roads, so the place test **passes** (own
  road, well over 1 km apart). Only the nightly share stops the split.

## Nightly share (the deciding test)

Source: the Let's Camp API, read 2026-11-19 (`/api/camps/palliser-regional-park`; sites at
`/api/camps/5f0646cea4c64c001103d8f2/sites`). It returns 81 online-bookable sites, none of them
adminOnly. The camp's SVG map draws every site in the park, but only these 81 can be booked.

- **South nightly sites (14):** 601-607 (50 A full hookup, 56 ft pads, max RV 50 ft, Walleye Cove's
  west row along Marina Road) and 704, 705, 712, 717 and 722 (30 A full hookup, max 50 ft), plus 706
  and 707 (30 A full hookup, max 40 ft). These last seven are all on the 700s upper loop.
- **South total: 143 numbered sites.** The park's South Campground map (Palliser_South_2024.pdf) and
  the Let's Camp map agree on that count (the verifier's ~146 was an estimate).
  14/143 = 9.8%; 14/146 would be 9.6%. Either way it is under 10%.
- saskregionalparks.ca/park/palliser (read 2026-11-19): "All campsites at Rusty's are full hook up and
  are both seasonal and reserve". It gives no count for the marina. The park-wide figure is "200
  year-round seasonal sites and 100 reserve sites", against 81 sold online. No source shows the other
  ~19 "reserve" sites at the marina. The online list is the only count there is.
- North for comparison: 67 nightly sites (11-16, 101-153, 301-330, 508-543 as listed), out of about 230.

## Waterfront (the parent's open lead from p3-523)

- waterfront_leads.md p3-523 left 9268 at `lakeview` on the strength of nightly sites 329-330, with the
  instruction "drop to not waterfront if photos show no lake through the belt".
- I read each site's Let's Camp photo (one per site; contact sheet rendered and viewed). 329 shows a
  trailer on grass hemmed in by leafy trees. 330 shows an empty grass and dirt pad under trees, with
  thick shrubs. **Neither photo shows the lake.**
- **For the reviewer:** this supports moving 9268 to `not waterfront` under that lead. I made no change
  because no split was made. One photo per site, with an unknown facing direction, is thin, so I
  report the downgrade rather than applying it.
- South, for the record (not an entry): on imagery the 740-749 row of the lower 700s loop faces the
  marina arm. All of those sites are seasonal. None of the 14 nightly sites is on the shore: 601-607 sit
  inland on Marina Road, and 704-722 are on the inner upper loop.

## Imagery frames read (all rendered and viewed)

Esri World_Imagery export via `audit/private_gap_browser/sat.py`:
- ov: 50.8770,-106.9480, 2.2 km half-width (whole park; both campgrounds and the road between).
- south: 50.8655,-106.9405, 350 m (Meadowlark Mesa block, Walleye Cove, community centre). The hint's
  50.8650,-106.9400 lands on the water of a bay west of the campground.
- south2: 50.8630,-106.9355, 450 m (Walleye Cove, the marina docks, the 700s loops).
- s700: 50.8618,-106.9405, 220 m (both 700s loops, store, launch, boat-trailer lot).
- pelican: 50.8668,-106.9365, 220 m (Pelican Point loop north-west of Marina Road, Walleye Cove south-east).
- north: 50.8880,-106.9530, 400 m (North campground, pool, beach, golf course).
- The two park map PDFs were rendered to PNG and viewed. The images and PDFs were then deleted.

## Sources (read 2026-11-19)

- https://www.palliserregionalpark.com/ (home: "At the top of the valley, a short drive inside the park
  gate, is Rusty's Coulee Marina ... seasonal and reserve camping is available here"), /maps/ (North
  Campground 2023 PDF, South Campground 2024 PDF), /rates-reservations/rates/, /rates-reservations/reservations/,
  /seasonals/ (Policy #003-22 seasonal sites: application, waiting list), /marina/, /entrance-gate/.
- Let's Camp API (camp + sites + the camp's SVG map, res.cloudinary.com/letscamp u9rc4yay3eygpouhrrjf).
- https://saskregionalparks.ca/park/palliser/
- Esri World_Imagery (frames above).

## For AWH

- The South campground meets the separate-place rule (2.8 km, own Marina Road) but sells only 14 of
  its 143 sites by the night (9.8%), so it stays inside 9268. One more nightly site would flip the call.
- The p3-523 lakeview lead: the photos of 329 and 330 show no lake, which supports `not waterfront`
  for 9268. Left for the reviewer.
