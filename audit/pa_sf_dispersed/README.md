# PA state forest reservable campsites: gap and adds (2026-10-10)

AWH asked for the public PA dispersed sites we were missing that can be booked
online. DCNR's designated state forest campsites are booked one site at a time
on ReserveAmerica (`pennsylvaniastateparks.reserveamerica.com`, one "park" per
forest), so the whole inventory is enumerable.

Pipeline, in order:

1. `enumerate.py` lists every site of the 18 forest parks and saves each
   `campsiteDetails.do` page's "Key: value" lines to `ra_sites.jsonl` (730 sites; the policy boilerplate repeated on 90%+ of pages is stripped from the committed copy;
   resumable; plain urllib works).
2. `gap.py` matches each site to an existing PA entry by siteId in
   website/inclusion_evidence, else the nearest entry within 250 m (1.5 km for a
   recreation-area campground) and writes the unmatched ones to `gap.json`.
   Before the adds: 661 unmatched.
3. `build.py` applies the gate per site and clusters the survivors within 1 km
   per forest (AWH chose one entry per 1 km cluster over one per site or one per
   loop). Writes `candidates.json` and `excluded.json` (every dropped site with
   its reason).
   - The gate: Drive-In, an RV or Trailer category, Max Vehicle Length >= 23 ft.
   - Also dropped on site-page text: tent-only, equine-only in summer (Yellow
     Snake), hang-gliders only in summer (Hyner), ATV riders only in summer
     (Susquehannock), "tent and small RV", 4WD/4x4 required or recommended,
     and camper trailers not recommended.
   - The Bald Eagle forest-wide "some roads require 4WD" line is a note caveat,
     not an exclusion.
4. `water_elev.py` adds Open-Meteo elevation and the distance to the nearest
   USGS NHD stream, waterbody or river area within 300 m. Overpass 504'd on
   nearly every query, so it switched to NHD.
5. `sat.py <first_site_id> out.jpg [half_width_m]` draws an Esri crop with every
   site of the cluster dotted. Half-width 150 sometimes gets an HTTP 500 from
   the export; 130 works.
   - Every cluster with water within 150 m was looked at, plus the four with a
     pond at 150-300 m.
   - Calls are in `waterfront.json` (via `wf_add.py`).
6. `apply.py` appends the entries. It writes fees and booking (the DCNR state
   forest roadside rates), hookups none, `dump: false`, sites
   count/max_rig_ft/pull_through, `season.year_round` where every site says
   "Open year round", and `policy_ref: "none"`.

Result: 244 sites in 156 entries, ids 15183-15338.

- 2 entries are creekside: Young Womans Creek Oxbow 025 and 023/024 Shingle
  Branch. The agency's per-site text there reads "Streamside campsite along Left
  Branch", and NHD puts the creek 7 m and 25 m away.
- The Right Branch "Streamside" sites (026/027, 028 Bull Run) stay
  `not waterfront`. The imagery is legible there and shows a road or wooded
  buffer.
- After the adds, `gap.py` leaves 393 unmatched sites. Every one of them is in
  `excluded.json`.
