# p3-483 Vermont notes (2026-11-16)

## Sources / tools
- Park pages https://www.vtstateparks.com/parks/<slug> all 200 (lake-carmi, quechee, woodford, branbury, emerald-lake, fort-dummer). /fees: RV/Tent $20 res, $38 non-res, prime +$2.
- tools/ra.py <slug>-state-park <parkId> out.json: full RA site list via plain HTTP (campgroundDetails + campsitePaging startIdx), types/lengths/Near Water.
- RA season: campgroundSeasonDates.do?contractCode=VT&parkId=N gives 2027 Start/End (End = last night).
- RA site photos: /webphotos/VT/pid<park>/sid<siteId>/0/540x360.jpg
- Map & Guide PDFs: /sites/stateparks/files/documents/<Name>%20Map%20Guide.pdf (Fort Dummer = Ft%20Dummer).

## Per entry
- 4082 Lake Carmi: 138 tent/RV (132 RV), max 40; lakeview confirmed (filtered, T010-016, T101-105); phone ''->802-933-8383; season 05-21/09-12 (2027); pin OK (Area A); Rt 236 detour alert.
- 4097 Hazen's Notch: operator site Mod_Security 406 (refusal) -> NO result file. Google 4.5 (17); phone 802-744-6612 matches.
- 4090 Kenolie: operator site HTTP 500; RoverPass claimed listing read; imagery 2024-04-23 ~100 seasonal trailers -> mostly seasonal, keep with note.
- 4094 Meadowcrest: 20 sites, 30A, $40 +9% tax, ~65% nightly, not waterfront kept.
- 4088 Prouty: Premier booking site list (44 RV online of map 0-81, 13 tent, 1 cabin), rates $55/$65/$70/$75, lakeview kept (59-63 ~50 m behind bike path + public beach).
- 4070 Quechee: not waterfront, /parks/quechee.
- 204 Woodford: lakefront -> lakeview; pin move ~570 m to ~42.8862,-73.0372; phone 802-447-7169.
- 4075 Branbury: lakeview -> not waterfront (T13-T17 70-110 m behind day-use lawn); count 36.
- 299 Emerald Lake: pin move ~400 m (approx) ~43.2785,-73.0080; phone 802-362-1655.
- 615 Fort Dummer: pin move ~300 m (approx) ~42.8222,-72.5648; phone 802-254-2610; website -> /parks/fort-dummer.
- 4083 Winhall Brook: riverfront -> riverview (N20-N24, S69-S75 behind bank trees; photos show no water); max 60 -> 40; season 05-21/10-11; pin move ~360 m to ~43.1607,-72.8072.
- Overpass: main 406; one try at a mirror stopped before use - no OSM data used.
- apply.py dry run (10 ids): no '!!'.
