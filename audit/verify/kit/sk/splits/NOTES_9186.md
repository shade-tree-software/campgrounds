# Split 9186 - Makwa Lake Provincial Park (SK) - 2026-11-19

## Decision: SPLIT Mewasin and Jumbo Beach (Jumbo Beach marginal)

- **9186 stays on Stabler Point**, including its Full Service pod. That pod is 0.42 km from the main loops, on the same road. The stored pin already marks Stabler Point: it is 39 m from S51 and 112 m from the Stabler centroid.
- **Mewasin is split out.** It is clearly a separate place:
  - 3.17 km centroid to centroid;
  - its own road south toward Exner Lake;
  - 4.5 km by road.
- **Jumbo Beach is split out.** It is marginal on distance but has its own entrance:
  - 1.12 km centroid to centroid, across the bay;
  - the nearest sites (J9 to S108) are only 0.70 km apart;
  - its loop road joins the Loon Lake / Hwy 26 road at both ends, separate from the Stabler Point park road;
  - 5.8 km by road.

  It meets "roughly 1 km+ with its own entrance", but only just. **AWH may prefer to keep it in 9186.** If so:
  - drop it from `new_makwa_lake_mewasin_jumbo_beach.json`;
  - add 16 sites to the parent;
  - add a non-electric base of $20 (electric surcharge 15, full_hookup 29);
  - the parent stays not waterfront unless Jumbo's J1/J2/J6 carry it.
- Mewasin's two parts are one campground. The west arm (M13-M25) and the east loops (M1-M12, M26-M36) are 0.36 km apart on one road, either side of the beach.
- The group site (Stabler Point - Group) is not counted anywhere.

### Files

`parent_9186.json`:

- Renamed "Makwa Lake Provincial Park - Stabler Point Campground".
- Pin and elevation are unchanged (54.0308,-109.2062, 523 m; Open-Meteo still gives 523).
- Sites: 227, max 40 ft, pull-through.
- Hookups: 50 A, with water and sewer on the 15 Full Service sites.
- Facilities: showers, flush toilets, potable water and dump.
- Season: 05-14 to 09-30.
- Fees: base $35 CAD with a full_hookup surcharge of 14. Every nightly Stabler site is electric or full service. The fees note is dropped: its $4 October discount is moot because Makwa has no fall camping.
- Still not waterfront, now with its own evidence.
- New note, curation_note and per-group provenance. The rating is untouched.

`new_makwa_lake_mewasin_jumbo_beach.json` holds two entries.

Mewasin ("Makwa Lake Provincial Park - Mewasin Campground"):

- Pin 54.0021,-109.2162, on M11 (the site nearest the centroid, 52 m); 527 m.
- 36 sites, 25 of them nightly; max 40 ft; pull-through (M6, M19).
- Non-electric, potable water.
- **lakeview**.

Jumbo Beach ("Makwa Lake Provincial Park - Jumbo Beach Campground"):

- Pin 54.0336,-109.1909, at the centroid (5 m from J8); 528 m.
- 16 nightly sites, max 40 ft, no pull-through.
- Non-electric, potable water.
- **lakefront with a caveat**: J1, J2 and J6.

Both new entries carry:

- reservation_fee 12 and entrance {11, 11, vehicle_day};
- base $20 CAD;
- booking: reserveamerica, fcfs never;
- season 05-14 to 09-30.

## Measurements

Distances are haversine between SKPP GIS site points.

| | centroid | points |
|---|---|---|
| Jumbo Beach | 54.03356,-109.19085 | all 16 |
| Mewasin | 54.00201,-109.21700 | all 36 (east 23: 54.00199,-109.21504; west 13: 54.00205,-109.22048) |
| Stabler Point (main) | 54.03006,-109.20679 | 76 (every 4th) |
| Stabler Point - Full Service | 54.02610,-109.20765 | 4 (SF1, SF5, SF9, SF13) |
| Stabler overall | 54.02986,-109.20683 | 80 |

Distances to Stabler Point:

| From | Centroid to centroid | Nearest sites | Stored pin to centroid |
|---|---|---|---|
| Jumbo Beach | 1.12 km | 0.70 km (J9 to S108) | 1.05 km |
| Mewasin | 3.17 km | 2.62 km (M5 to SF9) | 3.28 km |

Jumbo Beach to Mewasin is 3.90 km.

Roads (OSRM router.project-osrm.org, from the stored pin):

- To Jumbo Beach: 5.8 km. Out the Stabler park road, east to the park office road, onto the Loon Lake road / 2 Avenue, then into the Jumbo loop.
- To Mewasin: 4.5 km. Out the Stabler road, then south 2.1 km on the Exner Lake road.

Elevations (Open-Meteo):

| Point | Elevation |
|---|---|
| Stored pin | 523 m |
| Stabler at 54.0307,-109.2068 | 531 m |
| Mewasin, M11 | 527 m |
| Mewasin centroid | 523 m (lake level) |
| Jumbo Beach centroid | 528 m |

## Site data

Source: parks.saskatchewan.ca SKPP parkId 290500, read 2026-11-19.

- The paging table has 280 rows. Every row reads "Near Water - no".
- Detail pages were fetched without a cookie jar: all 16 Jumbo, all 36 Mewasin, and 80 Stabler sites (every 4th, including SF1/5/9/13). The fetch was stopped at 132 detail pages.

| Loop | Sites |
|---|---|
| Jumbo Beach | 16 Nightly Non-Electric |
| Mewasin | 25 Nightly + 11 Seasonal Non-Electric |
| Stabler Point | 146 Nightly Electric + 4 Accessible Nightly Electric + 62 Seasonal Electric |
| Stabler Point - Full Service | 15 Nightly Full Service |
| Stabler Point - Group | 1 Group Non-Electric - Medium |

Maximum equipment length on nightly sites:

| Loop | 40 ft | 32 ft | 25 ft | 18 ft |
|---|---|---|---|---|
| Jumbo Beach | 9 | 3 | 3 | 1 (J3) |
| Mewasin | 13 | 7 | 5 | 0 |
| Stabler Point | 16 | 64 | 61 | 9 |
| Full Service | 10 | 4 | 1 | 0 |

- Mewasin's seasonal sites: 40 ft x8, 32 ft x2, 25 ft x1.
- Amps: 21 Stabler rows offer 15/30/50 A and the rest 15/30 A. The Full Service sites have water and sewer.
- Rates for 6/15/2027 (sk_rate_card_2026-10-12.jsonl): non-electric $20 (J1, J2, M5, M6), electric $35, full service $49. The park page's current "General Season" table shows the reduced-services rates: $16, $31 and $45.

## Waterfront

The water distances were measured with a water mask on Esri z17 tiles (0.70 m/px; z18 tiles are not available here). The rule was tuned to the dark water at Mewasin. Every frame below rendered and was viewed.

**Stabler Point: not waterfront** (the stored value, kept).

- Frames: s17/smask (4x4 tiles) and se17/semask (east lobe).
- The peninsula is under continuous canopy to the shore.
- Nearest sampled sites to the water: S202 43 m, S51 50 m, S72 54 m, S206 59 m, S76 60 m.
- Photos of S51, S72, S76, S202 and S206 show forest only, with no water.
- The open shore is the day-use beach in the bay and the launch cove.
- Caveat: only every 4th site was sampled. Unsampled neighbours of S202 and S51 sit in the same rows under the same canopy.

**Mewasin: lakeview.**

- Frames: m17, mw17, and mw17n with its mask (mwmask). The west arm sits under continuous canopy.
- Distances to the water: M15 22 m, M13 24 m, M17 24 m, M19 32 m, M21 34 m, M23 36 m, M25 42 m. The east loops are 38-112 m back.
- Photos (contact sheets for M11-M25, both rendered):
  - the lake shows through trees from M13, M15 and M21, with glimpses from M25;
  - none of these sites is on open ground to the water.

**Jumbo Beach: lakefront, on the few-sites rule.**

- Frames: j17 with its mask (jmask), and j15 for context (the lake is about 1 km wide there; the highway runs on the east side).
- Distances to the water range from 7 m (J9) to 39 m (J1).
- Photos (four contact sheets, J1-J16, all rendered):
  - J1 #1: open gravel to the bank, lake beyond.
  - J2 #1 and J6 #2/#3: open ground to the lake.
  - J3 #1: open to the lake, but J3 books 18 ft only.
  - J4, J5, J10, J14 and J16: the lake through trees.
  - The rest face forest.
- The value rests on J1 (40 ft), J2 (25 ft) and J6 (32 ft). The note names them.

## Other sources

- **Park map PDF:** https://saskparks.tourismsaskatchewan.com/media/media-library/pdfs/park-downloads/makwa-lake/makwa-lake-all.pdf (7 pages, dated 2026-04-10).
  - Core page: the three campgrounds; the sani dump by the golf course on the Stabler road.
  - Page 2: Jumbo Beach and Mewasin layouts and symbols.
  - Page 3: Stabler Point, with two accessible service centres, washrooms, water, beach, boat launch, fish cleaning shelter and ski docks.
- **Park page:** https://parks.saskatchewan.ca/camping/makwa-lake-provincial-park/r/campgroundDetails.do?contractCode=SKPP&parkId=290500.
  - Amenities: showers, modern washroom, sewage disposal, drinking water.
  - Makwa Lake is not in the winter-camping list.
- **Tourism SK data** (parks.csv, listings.csv): phone 306-837-2410 (Park Office); Fall "Not Available in Fall"; Winter "Not Available in Winter".
- No --AWH text exists on 9186, so there was nothing to carry or withhold.
- Site photos and GIS points come from the SKPP detail pages. Imagery is from Esri World_Imagery.
- No source refused.
