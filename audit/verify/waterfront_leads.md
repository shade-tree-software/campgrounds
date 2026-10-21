# Waterfront re-audit leads from phase 7

A verifier's source (operator page or booking engine) claims water access that differs from
the stored `waterfront`. Per the curation doc's rule #7 that triggers the gate, both ways; a
booking-engine tag alone decides nothing. Work these with the full waterfront procedure.

- **806 Loraine Campground, Harold Parker SF (MA)** — stored "not waterfront" (--AWH). ReserveAmerica
  tags 14 sites in loop "Sites 59-90" Waterfront; RV-capable STANDARD sites 61, 63, 69, 71, 75,
  77, 81, 83, 87 (25-40 ft). Still open: the stored pin (42.6056,-71.1003) is in empty woods and
  Google's "Lorraine Park Campground" pin (42.6106,-71.0907) shows no loop either; mass.gov and
  the RA catalog both refuse plain HTTP. Needs the DCR campground map. AWH's call stands meanwhile.
- **252 Bear Creek Lake SP (VA)** — see asks.md #6 (DCR: A18 is tent-only; RV loops away from the lake).

## Resolved 2026-10-21 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **861 Hyner Run** not waterfront -> creekside (DCNR map + RA per-site tags, canopy case);
  **128 Promised Land** lakeview -> lakefront (FHU site 136 only; note says so); **14272 Penn's
  Creek** not waterfront -> creekside (z19 satellite: pads ~15 m from the bank); **647 Douthat**
  not waterfront -> lakeview (DCR Lakeside site map + satellite: 19 sites across the loop road from
  the north shore; pin moved onto that loop; --AWH note kept, dated --Claude line added).
- Downgraded: **757 Black Pearl Farms** riverfront -> not waterfront (AWH: the waterfront RV
  site is gone; RV sites are Farm View/Blue View, riverside sites tent-only); **1184 Stony Mountain** lakefront -> not waterfront (operator: the one lake site is a
  tent site; transient loops 100+ m back; pin moved onto the loops; low confidence - a site map
  could reverse it); **1048 Milton Loop** riverview -> not waterfront (continuous tree band);
  **590 Jekyll Island** coastal woods -> not waterfront (operator: "There are no waterfront
  campsites"; salt marsh and the beach road lie between, not the campground's own forest).
- Stand, evidence refreshed: 863 Sizerville, 78 Kooser, 619 Keystone (--AWH), 14316 Riverbank,
  13088 River Run, 1186 Whispering Winds, 1173 Moyer's Grove, 14277 Fire Pit (the creek claims
  are canopy-hidden with no per-site source, so they stay down).
- Closed, existing evidence stands: 860 Fowlers Hollow, 835 Hills Creek, 862 Lyman Run,
  127 Tobyhanna, 558 Laurel Hill.
- **924 Cape Charles KOA** (p3-16): KOA's page says "waterfront RV camping"; the --AWH firsthand
  note ("partial bay view, but none are directly on the beach") keeps bayview.
