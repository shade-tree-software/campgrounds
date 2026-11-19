# Split 9164 - Buffalo Pound Provincial Park (SK) - 2026-11-19

## Decision: SPLIT into three

The park has three campground areas at separate places:

- **NW group:** Maple Vale, Shady Lane A/B and Trails End, on one campground road at the north-west end.
- **EVL group:** Elmview, Lakeside and Valley, by the beach, pool and boat launch.
- **Lower Chalet:** A and B, on their own spurs off the main park road by the Lower Chalet visitor centre, south-east of EVL.

The groups are 2.4-5.2 km apart, centroid to centroid. Within each group the loops are adjacent and share a road, so they stay together.

**Id 9164 stays on the NW group,** the larger one (181 of 273 sites). Its pin moves 2.88 km. The old pin, 50.5947,-105.4126, sat in the boat-launch lot by Valley and Elmview, not on sites.

**Lower Chalet stands alone.** The hint said it is "probably not worth an entry", but it passes the rule: it is 2.38 km from EVL on its own spurs, and it shares only the main park road. It also passes the criteria: 18 reservable sites take a 23-ft rig (32-40 ft). It needs a caveat: the sites are grass with no pads, there is no power, and the loops sit by the water treatment plant. See For AWH.

### Output files

**`parent_9164.json`** (kept entry, the NW group):
- Name: "Buffalo Pound Provincial Park - Maple Vale, Shady Lane and Trails End Campgrounds".
- Pin: 50.6104,-105.4475, on nightly site S18 (Shady Lane A), 146 m from the group centroid. Open-Meteo gives 534 m.
- Sites: 181, max 40 ft, pull-through (T62).
- Hookups: 50 A (M51-M57, M61, M62), water false, sewer false. Only the seasonal S35F and S57F have water and sewer.
- Facilities: showers, flush toilets, potable water, camp store. Laundry and dump are left absent.
- Season: 05-14 to 10-31.
- Fees: $35 / $35 CAD, every nightly site being electric.
- Waterfront: **lakefront** (S40, S42, T13).
- Rating and website are unchanged.

**`new_buffalo_pound_elmview_lower_chalet.json`** holds two entries. The first, EVL:
- Name: "Buffalo Pound Provincial Park - Elmview, Lakeside and Valley Campgrounds".
- Pin: 50.5925,-105.4131, on Valley V5F. Open-Meteo gives 531 m.
- Sites: 65, max 50 ft, pull-through (V2F, V10F).
- Hookups: 50 A, water and sewer.
- Facilities: showers (at the beach building), flush toilets, water, dump.
- Season: 05-14 to 03-14.
- Fees: $35 base plus a full_hookup surcharge of 14.
- Waterfront: **lakeview**.

The second, Lower Chalet:
- Name: "Buffalo Pound Provincial Park - Lower Chalet Campground".
- Pin: 50.5816,-105.3883, on LCB-19. Open-Meteo gives 521 m.
- Sites: 27, max 40 ft, no pull-through.
- Hookups: electric 0, no water or sewer.
- Facilities: potable water.
- Season: 05-14 to 09-30.
- Fees: $20.
- Waterfront: **not waterfront**.

Both new entries carry fees.reservation_fee 12 and entrance {11,11,vehicle_day}, plus the same booking, website and phone as 9164.

## Measurements (haversine, SKPP GIS points for every site, 276 detail pages)

| | centroid | points |
|---|---|---|
| NW group | 50.60983,-105.44568 | 181 |
| EVL group | 50.59408,-105.41505 | 65 (yurts excluded) |
| Lower Chalet | 50.58054,-105.38888 | 27 |
| Maple Vale / Shady Lane A / Shady Lane B / Trails End | 50.60478,-105.44019 / 50.60867,-105.44691 / 50.61285,-105.44586 / 50.61306,-105.45033 | 59 / 20 / 39 / 63 |
| Elmview / Lakeside / Valley | 50.59470,-105.41643 / 50.59759,-105.41586 / 50.59219,-105.41286 | 34 / 7 / 24 |
| LCA / LCB | 50.57956,-105.38939 / 50.58176,-105.38823 | 15 / 12 |

Between groups:
- **EVL-NW:** 2.78 km centroid to centroid (nearest pair 1.72 km). The hint's ~2.4 km was short.
- **EVL-LC:** 2.38 km (nearest pair 2.00 km).
- **LC-NW:** 5.17 km (nearest pair 4.26 km).
- **Old pin:** 186 m to the EVL centroid, 2.88 km to NW, 2.30 km to LC.

Within groups, the loops stay together:
- **NW:** Maple Vale-Shady Lane A 642 m, Shady Lane A-B 471 m, A-Trails End 544 m, B-Trails End 316 m. Maple Vale-Trails End is 1.17 km, but Shady Lane lies between them on the one campground road. The Maple Vale map shows the road "To Shady Lane and Trails End Campground".
- **EVL:** Elmview-Lakeside 324 m, Elmview-Valley 376 m, Lakeside-Valley 637 m.
- **LC:** LCA-LCB 259 m.

## Site data (parks.saskatchewan.ca SKPP parkId 290170, read 2026-11-19)

The paging table has 285 rows. Every site also has a detail page (276, det2), giving GIS points, Allowed Equipment, Max Length, amps, water/sewer, access, surface and category. Every row reads "Near Water - no".

| Loop | Sites | Hookups | Max length / allowed equipment | Fits a 23-ft rig |
|---|---|---|---|---|
| Elmview | 34 NE + 2 yurts | 15/30 A | 18 on 21 sites, blank on 13; at most "Camping Unit up to 18ft", some tent/van only | 0 |
| Lakeside | 7 NE | 15/30/50 A | L1-L3 at 50, L4-L7 at 40 | 7 |
| Valley | 18 nightly FS + 6 seasonal FS (V9F, V11F, V13F, V17F, V19F, V22F) | 17 at 15/30/50 A; water and sewer Y | 20-40 (V12F at 20) | 17 nightly |
| Maple Vale | 56 NE + 3 accessible | 15/30 mostly; 15/30/50 on M51-M57, M61, M62; 15 A on 11 | up to 40 (M11) | 43 |
| Shady Lane A | 16 NE + 4 seasonal | 15/30 A | 15-25 | 4 nightly |
| Shady Lane B | 7 NE (S30-S42, even) + 30 seasonal E + 2 seasonal FS (S35F, S57F) | 15/30 A | 25-40 | 7 nightly |
| Trails End | 54 NE + 1 accessible + 8 seasonal | 15/30 A | 25-40; T62 Pull-Thru | 55 nightly |
| Lower Chalet A | 15 NNE | none | LCA-1/2 at 35, LCA-3 to LCA-7 at 32, LCA-15 at 25; LCA-8 to LCA-14 tent/van only | 8 |
| Lower Chalet B | 12 NNE | none | LCB-18 to LCB-20, 26, 27 at 32; LCB-21 to LCB-25 at 40; LCB-16/17 tent/van only | 10 |

- **Lower Chalet details:** "Site Surface: Grass" on all 27. LCB area note: "Non-electrical sites located adjacent to the Buffalo Pound Water Treatment Plant."
- **Totals:** 181 + 65 + 27 = 273, which matches the stored count. Not counted: Rankins group, pavilion, swimming lessons and the yurts.
- **Rates:** the rate card (jsonl 2026-10-12) shows E $35, FS $49, NNE $20. The live park rate table shows the reduced-services rates, E $31 and FS $45.
- **Tourism SK listings.csv:**
  - Fall: "Contact the park ... to book a campsite in October", with Fall Services "Electric_Campsites, Pit_Toilets, Portable_Toilets, Firewood".
  - Winter: "Winter camping available in Elmview campground from Nov 1, 2026 - Mar 14, 2027", with electric campsites only.
  - Yurts: open until Oct 13.

### Park map PDF (buffalo-pound-all.pdf, 2026-04-10, 4 pages, all rendered)

- **Core Area:** sani dump by Elm View and the entry gate; showers and change room at the beach and pool beside Lakeside.
- **Campgrounds page:** showers and service centres in Trails End and Shady Lane B.
- **Maple Vale page:**
  - an accessible Service Centre, washrooms, potable water and grey-water disposal;
  - groceries and a telephone at the entrance junction ("To Park Entrance and Store").
- **Lower Chalet A & B page:** washrooms and potable water in the loops; the visitor centre and food at the Lower Chalet building.
- **Laundry** appears only at park level and is not placed on any map.

## Waterfront

The water is Buffalo Pound Lake, a reservoir. I measured to the high-water edge: the sand or beach line, or the vegetated fringe.

- **NW: lakefront**, upgraded from lakeview with a caveat naming the sites.
  - **S40** (nightly, 32 ft): about 23 m to the sand edge across open mown grass.
  - **S42** (nightly): about 39 m across open grass with scattered single trees.
  - **T13** (nightly, 40 ft): about 22 m across open grass to a narrow tall-grass strip at the water. The T13 photos show open grass to the lake.
  - The other shore-side nightly sites look through shrubs or trees:
    - T11 and T16 over low shrubs;
    - T15 behind a thicket about 28 m deep;
    - S30 and S32 behind a patchy shrub fringe 20-25 m out;
    - S34, S36 and S38 through trees.
  - The other shore sites are seasonal. Maple Vale and Shady Lane A sit 300 m+ up the slope.
- **EVL: lakeview.**
  - Lakeside L1-L7 are 23-32 m from the water behind a continuous band of shoreline trees (z18 and its 2x crop).
  - The photos show the lake through the trees from L1, L2, L6 and L7.
  - Valley is 170 m+ from the shore, with woods and the boat-launch lot between: inland.
  - Elmview is south of the park road: inland.
- **Lower Chalet: not waterfront.**
  - LCB is about 150 m from the lake, with the main park road, woods and the water treatment plant between.
  - LCA is about 350 m back, in woods.
  - The photos of LCA-1 and LCB-21, 22, 23, 25 and 26 show no lake.

## Imagery frames read (all rendered)

- Esri World_Imagery, each with SKPP GIS points plotted:
  - ov15 (z15 overview with the old pin)
  - nw16 and nw16b (z16, the whole NW group, all 181 points)
  - slb18 (z18, 0.37 m/px, the Shady Lane B shore)
  - te18 (z18, the Trails End shore)
  - evl17 (z17, EVL)
  - ls18x2 (2x crop of z18 at Lakeside)
  - lc17 (z17, Lower Chalet)
- SKPP site photos:
  - T13 (2 photos)
  - the S30-S42 posts
  - Lakeside L1-L7
  - the sh_LC contact sheet (LCA-1, LCB-21/22/23/25/26)
- Park map PDF: pages 1-4 rendered to PNG, with a crop of the core area.

## For AWH

- **Lower Chalet stands alone.** It meets the rule and the criteria, but the hint doubted it was worth an entry.
  - It is 27 non-electric sites on grass, with no pads and no showers, beside the water treatment plant.
  - It has 18 sites at 32-40 ft. It is kept with the caveat.
  - If you would rather not list it, drop the second entry in the new file. The parent is already cut to the NW group, so Lower Chalet would then be in no entry.
- **Lower Chalet season:** I closed it at 09-30, because the October and winter services list electric campsites only. This is an inference, not a statement about the loop.
- **Lakefront upgrade on NW:** it rests on S40, S42 and T13.
  - The SKPP photos of the S30-S42 posts still say "Site Occupied By Seasonal Camper".
  - The booking site lists them "Looking For Category: Nightly".
  - If those sites go back to seasonal, T13 alone carries the call.
- **Elmview winter camping:** this is the park's only winter camping, and every Elmview site books for at most an 18-ft unit or a tent or van. A 23-ft rig therefore cannot book a winter site here, although EVL's season runs to 03-14.
- **Laundry:** it is listed park-wide but not placed on any map, so it is now absent on all three entries (the old entry had laundry true).
- **Dump station:** it is on the EVL entry only. The NW group has grey-water disposal stations but no sani dump.
- **Stored count:** 273 is confirmed (181 + 65 + 27).
