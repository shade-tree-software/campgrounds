# 5719 Oahe Downstream Recreation Area: split Campground 3 from Campgrounds 1 and 2 (2026-11-22)

## Decision
SPLIT. Campground 3 becomes its own entry (`new_oahe_downstream_cg3.json`, one entry). The id stays on
Campgrounds 1 and 2. The stored pin (44.4330,-100.3890) sat inside them, 55 m from their combined RV-site
centroid. `parent_5719.json` re-cuts the kept entry and moves the pin to that centroid.

Campgrounds 1 and 2 stay together. They are adjoining loops on one road system: loop centroids 362 m apart,
nearest sites (1E and 130E) 55 m apart. GFP draws them on one map ("Campgrounds 1 & 2").

`trips.campground_references(5719)` returned `[]`, so no trip references the entry.

## Why it passes the split rule
- **Distance (measured):** haversine over the engine's per-unit coordinates, using web-bookable RV sites only
  (no hosts, cabins, shelters or lodge pads).
  - Campground 1 (loop 68): 58 sites, centroid 44.43454,-100.39121.
  - Campground 2 (loop 69): 99 sites, centroid 44.43181,-100.38873.
  - Campgrounds 1+2 together: 157 sites, centroid 44.43282,-100.38964.
  - Campground 3 (loop 70): 41 sites, centroid 44.42355,-100.38859. The verifier's 44.42357,-100.3882 is
    essentially the same point.
  - Campground 3 to Campgrounds 1+2: **1,034 m**. To Campground 2 alone: 918 m. To Campground 1 alone: 1,240 m.
  - The nearest pair of sites (86E and 205E) is 505 m apart, straight across the river channel.
- **Separate places, each with its own road:**
  - Campground 3 is south of the Missouri River channel that runs below Oahe Dam's stilling basin. The channel is
    about 200 m wide.
  - No road or bridge inside the park crosses that channel. Campground 3's own road runs along the channel's south
    bank from SD-1806 at the south end of the river bridge. The park's single dump station is at that junction.
  - Campgrounds 1 and 2 are reached by the main park road, from the entrance by the dam north of the channel.
  - By road the two sides are about 3 km apart (read off imagery, not measured on a route).
  - GFP publishes a separate map for each side ("Campground #3 Map" and "Campgrounds #1 and #2 Map").
  - The seasons differ. Campground 3 is open year-round. Campgrounds 1 and 2 close Nov 15 through the last Friday
    of March for the bald eagle roost.
- Every unit is on one engine facility (facID=41), so the rec.gov exception doesn't apply. The distance and
  own-road rule is met: just over 1 km centroid to centroid, with a channel and a separate road between.

## Sources (all read 2026-11-22, plain curl with UA Mozilla/5.0, no bot walls)
- **GFP park page**, https://gfp.sd.gov/parks/detail/oahe-downstream-recreation-area/:
  - Rates: electric $30, camping cabins $60, modern cabins $120-150, group lodge $150.
  - Season: "Open: Year-round. Campgrounds 1 and 2 closed to camping Nov. 15 through the last Friday of March for
    bald eagle winter roosting. Day-use area and campground 3 remain open year-round. Between Oct. 1 and April 30,
    water systems may be closed."
  - Size: "3 campgrounds with 205 campsites, 8 camping cabins, 4 modern cabins, and group lodge".
  - Location "5 miles north of Fort Pierre on Highway 1806". Phone 605.223.7722.
  - Amenities list. Reservations online or at 1.800.710.2267.
- **GFP maps**, each ArcGIS Pro 2.9.5, created 2024-05-15. Each was rendered and read, then deleted.
  - https://gfp.sd.gov/userdocs/ods_overview.pdf: all three campgrounds, the stilling-basin channel, roads,
    and the dump station at the south end of the SD-1806 bridge. The south-west corner was re-rendered at 300 dpi
    to place the dump station.
  - https://gfp.sd.gov/userdocs/ods_cg1_2.pdf: site numbers, restroom/showers, vault toilet, water, hosts V1-V3.
  - https://gfp.sd.gov/userdocs/ods_cg3.pdf: site numbers 163E-205E (no 192E or 193E), cabins C1-C8,
    restroom/showers, vault toilets, water, hosts V4-V6, the playground and the horseshoe pit.
- **Go Outdoors SD engine**, https://reservations.gooutdoorssouthdakota.com/FacilityDetails.aspx?facID=41. Parsed
  `var sitesHashMap`: 224 units.
  - **Loop 68 (Campground 1):**
    - 58 RV sites, 1E-60E (7E and 13E absent). All "Back-In Campsite", Amp 20/30/50, $30.
    - MaxEquipLength runs 44-76, with 76 at 31E.
    - Hosts V1 and V2 are not sold online.
  - **Loop 69 (Campground 2):**
    - 99 RV sites, 61E-161E. 132E is absent, and 131E is listed but not sold online, so excluded.
    - All back-ins, 20/30/50, $30. MaxEquipLength runs 48-73.
    - Host V3 is not sold online. Its 75 ft looks like the engine default.
  - **Loop 70 (Campground 3):**
    - 41 RV sites, 163E-191E and 194E-205E. The only pull-thru is 164E, at 138 ft (its Online Content agrees).
    - The back-ins run 49-70 ft. All 20/30/50, $30.
    - Also: cabins C1-C8 ($60), group shelter PSH3, and hosts V4 to V6, which are not sold online.
  - Loop 71 holds the group lodge plus 4 lodge pads, not sold online. Loop 72 holds modern cabins C-A to C-D and
    PSH1.
  - 198 RV sites are sold online, plus 6 hosts and 131E, which makes GFP's 205.
    - The stored provenance said 57+99+41=197. Loop 68 actually has 58.
  - No unit carries a blackout range. The engine does not show the CG1-2 winter closure.
  - Per-site photos (rackcdn ImageURL) for 194E, 195E, 197E and 201E-205E were downloaded and read, then deleted.
- **Open-Meteo elevation:**
  - Campgrounds 1+2: centroid 450 m (loop 68 448, loop 69 446). The old pin read 449.
  - Campground 3: centroid 440 m. 205E reads 434, 201E 441.
  - Lake Oahe water above the dam: 488 m.

## Imagery (Esri World_Imagery export via audit/verify/kit/mn/tools/satpts.py, unit points plotted)
Every frame rendered (checked visually). Files deleted after use.
- **Whole park, 1,100 m half-width (2.4 m/px), at 44.4285,-100.3895:**
  - Campgrounds 1 and 2 sit under cottonwoods between the main river and the stilling-basin channel.
  - Campground 3 sits south of the channel. The channel is about 200 m wide.
  - The old pin is in Campground 2's north part.
- **Roads, 650 m half-width (1.4 m/px), at 44.4300,-100.3985:**
  - The SD-1806 bridge over the channel.
  - Campground 3's road running SE along the south bank from the bridge's south end.
  - Campgrounds 1 and 2's park road on the north side.
- **Campground 3, 450 m half-width (1.0 m/px):** the loop, the cabin row along the bank, and the channel about
  200 m wide.
- **Campground 3 north row, 120 m half-width (0.27 m/px), plus a 2x enlargement of the 201E-205E corner.**
  Distances from the pads to the riprap-edged bank:
  - 205E: about 20 m, over open lawn.
  - 204E: about 32 m.
  - 203E: about 44 m, past tree clumps.
  - 201E and 202E: about 60-70 m.
- **Campground 3, 194E-198E and C1-C3, 110 m half-width (0.24 m/px).** Distances from the pads to the bank:
  - 196E: about 13 m.
  - 194E: about 14 m.
  - 195E: about 15 m.
  - 197E: about 21 m, over open lawn.
  - 198E: about 27 m, behind trees.
  - The cabin road is behind (south of) these pads, so no road lies between the pads and the water.
- **Campground 2 east side, 200 m half-width (0.44 m/px):**
  - 100E-105E sit about 96-99 m from the river.
  - Between them and the water are a continuous cottonwood canopy, the park road, a day-use parking lot and the
    swim beach.
- Engine per-site photos:
  - 195E and 194E: the gravel pad opens onto mown lawn, and the river is right past it.
  - 205E: open lawn and a few cottonwoods to the water, which is about 20 m off.
  - 197E and 204E: open lawn with scattered trees, the water close beyond.
  - 201E and 202E: the water is farther, through trees.

## Waterfront calls
- **Campgrounds 1 and 2: not waterfront** (unchanged). The nearest sites are about 100 m from the river behind
  canopy, a road, a parking lot and the swim beach. The campgrounds are below the dam, so there is no lake value.
- **Campground 3: riverfront.**
  - 194E-197E, 204E and 205E sit about 13-32 m from the bank of a ~200 m-wide river channel.
  - The ground between is open, unused lawn with scattered trees, and no road or day use lies between.
  - Confirmed by legible imagery plus the engine's official per-site photos.
  - The campground is below Oahe Dam, so it is judged on the Missouri River, not the reservoir.
  - The note names the sites, under the few-clear-sites rule (AWH 2026-11-10).

## Re-cuts on the kept entry (parent_5719.json)
- **Name:** "Oahe Downstream Recreation Area (Campgrounds 1 and 2)".
- **Location:** moved 55 m to the RV-site centroid. **Elevation:** 450 m.
- **Sites:** 197 / 75 ft / pull_through true becomes **157 / 76 ft / pull_through false**.
  - The 75 ft came from host V3.
  - The pull-thru is Campground 3's 164E.
- **Season:** year_round true becomes **opens 03-26, closes 11-14**.
  - 03-26 is the widest reading of "through the last Friday of March", which falls on March 26 in 2027.
  - The season note quotes GFP.
- **Rewritten:** waterfront_evidence, inclusion_evidence and note. No --AWH text was present.
- **Provenance refreshed (values unchanged):** facilities, hookups and booking.
  - The dump station is on park property, on the Campground 3 side of the bridge. That is said in the
    facilities provenance and the note.
- **Unchanged:** website, phone, rating (RV Life 4.5/$$ is a park-level listing; it stays on the kept entry), fees
  and hookups (50 A).

## New entry (new_oahe_downstream_cg3.json)
- "Oahe Downstream Recreation Area (Campground 3)", ownership state.
  - Pin 44.42355,-100.38859 (the RV-site centroid). Elevation 440 m.
- 41 RV sites, max 138 ft (pull-thru 164E), pull_through true, 50 A.
- Facilities: showers, flush and vault toilets, potable water, and dump (the park's station at the start of its
  road).
- Season: year_round, with a note on the Oct-Apr water shutoff.
- Booking: the engine facID=41.
- Fees: 23 + $7 electric (every loop 70 RV unit is $30), the same shape as 5719.
- No rating copied: the listing is park-level and was not looked up for this campground.
- Waterfront riverfront, with 194E-197E, 204E and 205E named in the note.

## For AWH
- **Campground 3 rises from the stored not waterfront to riverfront**, on imagery plus the engine's site photos.
  Six sites (194E-197E, 204E, 205E) are 13-32 m from the river over open lawn. The rest sit back or inside the
  loop.
- **Campground 3's max_rig_ft is 138**, the engine's MaxEquipLength for pull-thru 164E (its Online Content agrees).
  It is real engine data, not the 75 default, but it is unusually large. The longest back-ins are 70 ft
  (194E-205E).
- **Is 1,034 m centroid to centroid enough?** It is just over the ~1 km line, and only 918 m to Campground 2
  alone. The channel with no crossing in the park, the separate road (~3 km by road), the separate GFP map and
  the different winter season are what make Campground 3 a separate place.
