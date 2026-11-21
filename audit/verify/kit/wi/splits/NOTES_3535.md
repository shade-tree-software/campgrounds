# 3535 Big Eau Pleine County Park (Marathon County, WI): split decision, 2026-11-21

**Decision: SPLIT.** 3535 keeps the West campground on its existing pin. The South campground becomes a new entry (`new_big_eau_pleine_south.json`). The changed fields for 3535 are in `parent_3535.json`.

## Sources (all read 2026-11-21 unless stated)

- **Marathon County reservation engine, parks.marathoncounty.gov.** This is a Cedar/Next.js front end, read in one headless browser under the flock. It served normally: no refusal, and it is not the refusing marathoncounty.gov. Facility data came from its Hasura GraphQL responses: title, address, description, amenities, settings, the per-venue (site) list with coordinates, descriptions and hidden flags, venue schedule exceptions, and the attached "Camping Reservations" form.
  - West: `/wausau-marathon/reservation/campgrounds/7f798887-a407-4a93-952a-98e6d5cd959a`, "Big Eau Pleine West Campground".
  - South: `/wausau-marathon/reservation/campgrounds/4a02962c-ea10-402e-bb6d-7d7dec475b89`, "Big Eau Pleine South Campground".
  - Dells (3449): `/wausau-marathon/reservation/campgrounds/8363e683-e97b-4d23-b10e-ae4521bc9f3a`, "Dells of Eau Claire Campground", 235890 County Rd Y, Aniwa.
  - Both Big Eau Pleine facilities give the address 135695 Eau Pleine Park Rd, Mosinee.
- **County unit maps** (Cedar PDFs on storage.googleapis.com/cedar-public-assets, both "Updated September 2026"). Both rendered and were read; both were then deleted.
  - South Unit: sites 47-106. The loop sits on a spur off the park road at its north end. A road runs from the loop's SE corner to a second boat launch. There is a shoreline walking trail, and a horse/walking trail to the west (a trail only, not horse camping).
  - West Unit: four loops on a road entering from the SE past the parking lot, beach, boat launch and disc golf. The group campground lies to the south. A walking trail runs between lakeside sites 30-46 and the shore.
- **Not re-fetched.** marathoncounty.gov refuses automated reads, so I did not fetch it or its Wayback copies. These quotes are cited as read by verifier u-06 on 2026-11-20 and recorded in 3535's verify_scan:
  - the park page (Wayback 2025-03-07);
  - the 2026 fee schedule (Wayback 2026-01-01);
  - the Things To Do page (Wayback 2026-10-05, "open May 1st through October 31st").
- **Elevation:** Open-Meteo, 2026-11-21.
  - West pin 370 m (unchanged). South pin 381 m.
  - Lakeside West sites 346-353 m; lakeside South sites 374-380 m; water points 346 m.
  - The DEM is a canopy-inclusive surface model. The ~30 m excess over the water at South is trees, not a bluff.

## Season lines (verbatim) — the Dells question

The engine's venue schedule exception is **identical on all three facilities** (West, South and Dells 3449):

> "Campground closed - open May 1 - Sept 30 only"

It covers 2026-10-05 to 2026-12-31, 2027-01-01 to 2027-04-30 and 2027-10-01 to 2027-12-31. South also carries 14 blank-description site closures for 2026-10-01 to 2027-04-30 and 2027-10-01 to 2028-04-30.

The "Camping Reservations" form attached to all three facilities explains the line:

> "The reservation season is May 1 - September 30 for Big Eau Pleine (BEP) and Dells of Eau Claire (DEC) while Marathon Park is May 1 – October 31. Check in/Check out times are 3pm.  BEP and DEC are open the month of October but are not available for reservations and can only be used on a first-come, first-serve basis.  Campgrounds are closed from November 1 through April 30."

Further form lines used:

> "Self-registration stays are limited to 3 nights maximum. ... Self-registrations of three nights or more with arrivals from September 30 through October 31 are not limited to a maximum of 3 nights."

> "The sanitary dump stations at Marathon Park, Dells of the Eau Claire and Big Eau Pleine are open 8 am to 8 pm daily. A $8 fee is charged. There are no water hookups at any of the campgrounds. Pressurized well systems are available throughout each campground."

> "Reservations have a 2 night minimum and a maximum of 14 nights ... Reservations will not be accepted within 3 days prior to your check-in date."

**Conclusion for AWH:** Dells does not close on Sept 30. "open May 1 - Sept 30 only" is the end of the reservation calendar. By the county's own form, Dells and Big Eau Pleine are both open May 1 - Oct 31, first-come only in October, which agrees with the Things To Do page.

3449 currently stores `season.closes: "09-30"`, quoting the engine line. By the schema's §4.1 it should probably be `season` 05-01..10-31 with `booking.season` 05-01..09-30. **I did not change 3449**, as instructed. Both Big Eau Pleine entries are written that way.

## Measurements (haversine on the engine's per-site coordinates)

- **West public-site centroid:** 44.74332,-89.85160 (44 sites with coordinates). The current 3535 pin, 44.7433,-89.8516, is 2 m from it, so it is kept.
- **South public-site centroid:** 44.73643,-89.83676 (58 sites). New pin 44.7364,-89.8368, 18 m from site 091.
- **Centroid to centroid: 1,400 m.** Pin to pin: 1,398 m. Nearest sites (West 005 to South 106): 1,122 m.
- **Own road:** Esri World_Street_Map, read 2026-11-21 with the sites overlaid, rendered.
  - Eau Pleine Park Rd forks about 44.747. The west branch ends in the West loops.
  - The east branch winds about 1 km south to the South loop.
  - The two unit maps each show their campground on its own spur. Both campgrounds share the park's single entrance road up to the fork; below it, each has its own road.
- **Separate booking facilities** on the county engine, each with its own site list, unit map and description.

The split rule is met: separate places 1.4 km apart, each on its own road. Neither campground has a part that stays with the other: the group site (44.7406,-89.8502) belongs to West and books with it.

## Imagery (Esri World_Imagery, read 2026-11-21, all rendered and viewed, then deleted)

- 44.7395,-89.8440, half-width 1,100 m: the whole peninsula under continuous forest, with wide drawdown beaches on the shores.
- 44.7420,-89.8460, 750 m, sites overlaid: the West loops under canopy at the peninsula's NW point; the South loops at the SE.
- 44.74332,-89.8516, 230 m (West) and 44.73643,-89.83676, 230 m (South): continuous canopy over both loops. Roads and pads are not resolved.
- 44.7433,-89.8533, 140 m, West sites overlaid:
  - Lakeside 030/033/034/036/041-046 sit about 45-55 m back from the tree line at the water.
  - It is continuous canopy throughout, and the county map runs a walking trail between.
  - **lakeview** (unchanged).
- 44.7356,-89.8370, 140 m, South sites overlaid:
  - Lakeside 072-082 sit about 35-40 m from the tree line and about 55 m from the water at the drawdown beach.
  - It is continuous canopy throughout.
  - **lakeview.**

Neither campground has a site on open ground within about 50 m of the water. Both calls are views, so no downgrade question arises.

## Resulting entries

| | 3535 West (kept id) | new South |
|---|---|---|
| pin | 44.7433,-89.8516 (unchanged) | 44.7364,-89.8368 |
| elevation | 370 m | 381 m |
| sites | 44 public: 001-046 less host 015 and admin 017; 029 accessible, booked by phone. All electric, 40-60 ft. | 58 public: 047-106 less admin 047/055. 048-070 electric; 099/101/103/105/106 walk-in only. 40-60 ft. |
| waterfront | lakeview: 030, 033, 034, 036, 041-046 view the flowage under canopy | lakeview: 072-082 (even numbers) view the flowage under canopy |
| fees 2026 | $28-30 | $23-28 |
| booking | after_cutoff | some_sites |

Both entries carry the same `season` (05-01..10-31, with an October first-come note) and `booking.season` (05-01..09-30). Both have `hookups.water: false`. Electric amperage is unknown, so the key is omitted.

## For AWH

1. **3449 Dells of the Eau Claire:** `season.closes` 09-30 looks wrong. The county form says it is open in October, first-come only. Suggested change: season 05-01..10-31, `booking.season` 05-01..09-30. Not changed.
2. **South electric count:** the county page (Wayback 2025-03-07) says 24 electric sites. The engine tags 22 public ones (048-070 less admin 055). `hookups.note` names the sites (048-070) and the county's 24; `sites.count` (58) follows the engine.
3. **Not run:** the `apply_split.py` dry run (no `--apply`) was refused by the permission system. I did not retry it.
