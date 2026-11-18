# SK notes p3-521 (2026-11-18)
- SKPP loop filter: POST campgroundDetails.do with `contractCode=SKPP&parkId=N&loop=<loopId>&lookingFor=&campingDate=&lengthOfStay=` (loop ids are the <option value> of select#loop); paging campsitePaging.do&startIdx=10.. keeps the filter in the cookie session. Total in span#resulttotal_dr_top. Rows appear twice per page (dedupe by siteId). Tools: tools/sk_table.py SLUG PARKID OUT.json LOOPID... ; tools/sksum.py; tools/skd.py (details: 'Key: <strong class=attrval>' incl. GIS Latitude/Longitude) - ~0.7 s/site on 2026-11-18.
- Table amenity icon alt 'Full Hookup - no' appears on Nightly Full Service sites that DO have water+sewer per detail page (K1): trust the detail page.

## Lesson (rr.json)
- sk_table.py whole-park pass + per-loop passes duplicate rows: dedupe by site id before counting (rr.json had 607 rows for ~303 unique).
- satzp z18 often "Map data not yet available" in northern SK (Meadow Lake); z17 works.
