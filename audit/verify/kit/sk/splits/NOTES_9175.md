# Split 9175 - Duck Mountain Provincial Park (SK) - 2026-11-19

## Decision: SPLIT Fern; describe Selwood only

- **Fern is split out.** It is a separate place: about 2 km southwest of Pickerel Point centroid to centroid, on its own access road off Highway 57 by the park village. It runs the park's winter camping, and 11 of its 19 nightly sites take a 23-ft rig.
- **9175 stays on Pickerel Point** (Birch, Poplar and Spruce). Those loops are 0.36-0.78 km apart on one road, and the stored pin already marks them.
- **Selwood gets no entry.** It is also a separate place (2.45 km north, its own 3.3 km road), but every one of its 11 sites books a unit of 18 ft or less. It joins neither part: the parent's note describes it, and its sites are left out of the parent counts.

Files:

- `parent_9175.json`:
  - Renamed "Duck Mountain Provincial Park - Pickerel Point Campground". The pin and elevation are unchanged (51.655,-101.6095, 623 m). The pin is 71 m from S14, at the entrance hub between the loops.
  - Sites 346 (max 50, pull-through).
  - Hookups unchanged: 50 A, with water and sewer on Birch B192-B206.
  - Season closes 10-31.
  - Fees re-cut to all-electric: base $35 with a full-hookup surcharge of 14.
  - Facilities re-cut from the Pickerel Point map page. camp_store is dropped: the park's store is by Fern and the village, and Pickerel Point has only a snack bar.
  - Lakeview kept on Spruce S68-S83.
- `new_duck_mountain_fern.json`:
  - "Duck Mountain Provincial Park - Fern Campground", pinned at 51.6404,-101.6269 (the GIS centroid of the 19 sites, on F6). Open-Meteo gives 609 m, the same as the lake surface DEM.
  - 19 sites, max 32, all back-in. Only F1 and F2 are electric (15/30 A).
  - Season 05-14 to 03-14.
  - Fees: base $20 CAD with an electric surcharge of 15, plus the carried reservation fee of 12 and entrance {11,11,vehicle_day}.
  - Lakeview.

## Measurements (haversine, SKPP GIS site points)

| | centroid | points |
|---|---|---|
| Fern | 51.64044,-101.62687 | all 19 (F1-F19) |
| Birch | 51.65879,-101.61166 | 99 |
| Poplar | 51.65262,-101.60615 | 20 (every 3rd) |
| Spruce | 51.65255,-101.61142 | all 83 |
| Pickerel Point overall | 51.65562,-101.61101 | 202 |
| Group sites (Deer/Elk/Moose) | 51.65552,-101.60230 | 3 |
| Selwood | 51.67768,-101.61021 | all 11 |

Distances from **Fern**:

| To | Distance |
|---|---|
| Pickerel Point overall | **2.01 km** |
| Spruce | 1.72 km |
| Poplar | 1.97 km |
| Birch | 2.30 km |
| Nearest pair (F12 to S83) | 1.24 km |

Distances from **Selwood**:

| To | Distance |
|---|---|
| Pickerel Point overall | **2.45 km** |
| Birch | 2.10 km |
| Fern | 4.30 km |
| Nearest pair (SW10 to B33) | 1.80 km |

Inside Pickerel Point, the loops are 0.36-0.78 km apart. The stored pin is 0.13 km from the Pickerel Point centroid; that centroid falls on the beach and day-use area.

Roads (OSRM router.project-osrm.org):

- Fern to Pickerel Point is 5.9 km by road: Fern's own access (450 m) to Highway 57, 3.3 km east on the highway, 1.55 km north on the park road, then 592 m in.
- Pickerel Point to Selwood is 5.3 km, on its own 3.3 km road north from the park-road junction. It does not pass through Pickerel Point.

Elevation (Open-Meteo):

| Point | Elevation |
|---|---|
| Fern centroid | 609 m |
| Lake | 609 m |
| Birch centroid | 618 m |
| Stored pin | 623 m (624 m at S14) |
| Spruce S2/S4 | 609 m |
| Selwood | 628 m |

## Site data (parks.saskatchewan.ca SKPP parkId 290275, read 2026-11-19)

**Paging table** (381 rows; every row reads "Near Water - no"):

| Loop | Sites |
|---|---|
| Birch | 204: 77 Nightly Electric, 2 Accessible Nightly Electric, 4 Double Nightly Electric, 15 Nightly Full Service (B192-B206), 105 Seasonal Electric, 1 Accessible Seasonal |
| Poplar | 59 Nightly Electric |
| Spruce | 82 Nightly Electric, 1 Seasonal (S15) |
| Group sites | Deer, Elk, Moose |
| Fern | 2 Nightly Electric (F1-F2), 17 Nightly Non-Electric, 2 Camp-Easy yurts (Y1-Y2) |
| Selwood | 11 Nightly Non-Electric (SW1-SW11) |

- The stored count of 376 = 381 rows - 2 yurts - 3 group sites. The parent's new count is 346 (Birch 204 + Poplar 59 + Spruce 83).
- Parent nightly sites: 239, of which 207 take 23 ft+.
  - Birch nightly maximum lengths: 50 ft on 55 sites, 40 on 7, 32 on 18, 25 on 7, 18 on 10.
  - Poplar: 32 ft on 58 sites, 25 on 1.
  - Spruce: 40 ft on 6 sites, 32 on 19, 25 on 36, 18 on 16, blank on 5.
- Pull-Thru: 66 of the 99 Birch detail pages. Every Fern and Selwood site is Back-In.

**Detail pages:**

- **Fern** (every site):
  - F1-F3: 32 ft (26-32 ft class).
  - F8, F10, F11, F13, F14, F15, F17, F18: 25 ft.
  - F6, F7, F9, F16, F19: 18 ft.
  - F4, F5, F12: Single Tent only.
  - F2 is "Shaded", 15/30 A.
- **Selwood:** SW1-SW11 are all "Camping Unit up to 18ft, Single Tent", max 18. SW10 is tent only.
- **Spruce S68, S70, S74, S77, S79, S83:** 25 ft ("Camping Unit 19 to 25ft"). S72, S82 and S55 are 18 ft.

**Rate card** (sk_rate_card_2026-10-12.jsonl, posted for 6/15/2027):

| Class | Rate | Sites |
|---|---|---|
| Electric | $35 | Fern F2; Birch B6, B7, B80, B81; Poplar P4, P5; Spruce S68, S69 |
| Full service | $49 | B192, B193 |
| Non-electric | $20 | F3, F4, Selwood SW4, SW5 |

The park page's rate table, "General Season Nov 19 2026 - Nov 19 2027", gives the reduced-services rates: Non-Electric $16, Electric $31, Full Service $45.

**Park page banner:** "Power (only site 2), firewood, and outhouse toilets ... Nov 1 2026 - Mar 14 2027."

**Tourism Saskatchewan:**

- listings.csv:
  - Fall: "Contact the park ... to book a campsite in October". No loop is named. Fall services: Electric_Campsites, Portable_Toilets, Firewood.
  - Winter: "Winter camping available in Fern campground from Nov 1, 2026 - Mar 14, 2027. Book online or contact the park".
- parks.csv: Phone Number Primary is 1-306-542-5500 (Park Office).

**Park map PDF** (duck-mountain-all.pdf, 2026-04-10; 3 pages: core, Pickerel Point, Selwood):

- Core page: Fern sits on Madge Lake's south shore by Highway 57 and the park village. The cluster of symbols beside its label covers the park village area (groceries, yurt, picnic shelter, service centre, ball field, tennis), so I could not tie it to the Fern loop. Fern's facilities are therefore kept to the winter outhouses (vault_toilets).
- Pickerel Point page: service centres, a shower, washrooms, potable water, two sani dumps, laundry and a snack bar by the entrance parking.
- Selwood page: 11 sites on its own spur road, with potable water and washrooms.

## Waterfront

- **Pickerel Point: lakeview, kept.**
  - Spruce S68-S83 run down the west side of the wooded point. Pixel profiles along each site's row put the tree crowns 16-22 m west of S68, S70, S74, S77, S79 and S83, then a lighter shallow band, with open water about 25-35 m out. The flood-fill mask to deep water gave 41-55 m.
  - The canopy is continuous to the water.
  - The lake shows in the site photos from S70, S74, S77, S79 and S83 (S83_2 is taken from the bank), but not from S68.
  - S55 is about 15 m from the bay over open sand, but it is 18 ft only.
  - Birch's west row (B7-B29) is about 30-55 m from the lake through continuous forest. This was read visually on z18 at 0.37 m/px, because the water mask failed on the dark forest.
  - B29-B33 sit behind forest and a wide reed and driftwood flat on the north bay (80 m+ to water).
  - Poplar is inland.
  - The old first segment of the waterfront evidence ("satellite at 51.6387,-101.6398 ... cabins/cottages") described the village shore, not this campground. It is replaced.
- **Fern: lakeview.**
  - The sites sit behind a continuous spruce band on the south shore. Mask distances to the lake edge:

    | Sites | Distance |
    |---|---|
    | F8 | 11 m |
    | F7 | 17 m |
    | F10 | 20 m |
    | F4, F12 | 28 m |
    | F3 | 30 m |
    | F1 | 32 m |
    | F2 | 38 m |
    | the rest | 41-98 m |

  - The lake shows through the trees in photos from F2, F7, F8 and F10, and perhaps F9 and F12.
  - No site is on open ground to the water.
  - The view rests on the 23-ft-capable sites F2, F8 and F10.

## Imagery frames read (all rendered)

- Esri World_Imagery:
  - fern17 (z17, 0.741 m/px) and fern18 (z18, 0.371 m/px), with Fern points, plus the fern18 water mask
  - pp17s (z17, Pickerel Point)
  - pin18 crop (z18, pin + Pickerel Point points)
  - spr18 (z18, 0.371 m/px, all Spruce points) and its mask
  - bir18 (z18, Birch points; the mask failed, so this was read visually)
  - bn18 (z18, Birch north and west rows)
- SKPP photo contact sheets: Fern (every site with photos), and Spruce S68, S70, S74, S77, S79, S83.
- Park map PDF pages rendered: the core page (Fern area at 200 and 400 dpi, plus the legend), and the Pickerel Point page (110 dpi plus a 330 dpi crop).

All imagery, photos and the PDF were deleted after use.

## For AWH

- **Selwood** (11 sites, 2.45 km north, own road, all 18 ft or less) gets no entry. Its sites leave the parent's counts, and the parent's note mentions it. If you would rather it stay inside the parent, add 11 to the site count and restore the Selwood line in the note.
- **October camping:** the listing names no loop. I closed the parent at 10-31, as in the Blackstrap precedent. Fern's 05-14 to 03-14 season spans October either way.
- **Fern site sizes:**
  - 11 of the 19 sites take a 23-ft rig.
  - Only F1 and F2 have power. Winter power is at site 2 only.
  - Five sites take 18 ft or less, and three are tent only.
  - Fern's lakeview rests on F2, F8 and F10. F7 is 18 ft and F12 is tent only.
- **Parent fees:** base changed from $20 to $35, because every nightly Pickerel Point site is electric or full service.
- **Parent facilities:** camp_store dropped. The park's store sits by the village and Fern; Pickerel Point has a snack bar.
