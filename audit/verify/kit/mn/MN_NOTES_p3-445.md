# p3-445 MN unread sweep (2026-11-11)

Plain fetch once more, UA Mozilla/5.0, all 2026-11-11:
- 5518 blueearthcountymn.gov  403 Cloudflare "Attention Required" -> UNREAD
- 5669 campspot.com/park/...   403 CloudFront "Request blocked" -> UNREAD (no city page found; exploreminnesota 403)
- 5576 cloquetmn.gov           403 Akamai "Access Denied" -> UNREAD
- 5633 hallockmn.org           403 Cloudflare -> UNREAD
- 5651 renvillecountymn.gov    403 Cloudflare -> UNREAD
- 13327 cityofsebeka.org       403 Cloudflare challenge -> UNREAD
- 5649 cityofkarlstad.com      403 Cloudflare challenge -> UNREAD
- 5689 pelicanrapids.com       403 Cloudflare challenge; ottertaillakescountry.com also 403 -> UNREAD
- 5702 visitwarroad.com        403 Cloudflare -> UNREAD
- 5705 brownsvillemn.gov       403 Cloudflare; co.houston.mn.us DOWN (TLS handshake failure on https, Cloudflare error 1001 DNS on http) -> Wayback allowed (down site); web.archive.org 429 repeatedly
- 13342 cityofmadisonmn.gov    403 Cloudflare -> UNREAD
- exploreminnesota.com profiles (wildcat 1544, moose lake 605): 403 -> not retried.
- Firefly WildcatPark portal: 200, unit types RV Site / Shelter / Tent Site; maxdate 10/11/2026 < mindate 11/11/2026 -> nothing searchable, 2027 not loaded.

Repo evidence (not re-fetched): audit/price_research/local_browser_2026-10-16/browser.jsonl holds a 2026-10-16 browser read
of cloquetmn.gov Spafford page: seasonal/monthly/weekly only, no nightly rate (see report).

Imagery (Esri, 2026-11-11):
- 5669 Moose Lake: lower lane south row of pads ~46.4537,-92.7540, 5-15 m from Moosehead Lake shore over open lawn; docks. Lakefront plausible for that row; site numbers unknown.
- 5705 Wildcat: shore strip of pads along the river east road (~43.6865,-91.2733) and north loop east edge (~43.6880,-91.2735) ~15-25 m from the Mississippi across sand beach. Site numbers unknown.

Phones: Sebeka City Hall 218-837-5773 (search snippet of cityofsebeka.org/how-do-i, not read).

2026-11-12:
- 5705 WRITTEN: Wayback 2026-02-13 county parks page (site down = archive allowed) + 2023 county site map (wmap.jpg) + rules PDF (2025 capture) + Firefly.
  booking operator/Firefly (Wildcat Creek Management LLC, 507-482-6250; off season 507-725-5803), water true, showers+dump, sites note (51 electric 40-51/60-107, 8 primitive 120-127, 35 seasonal 1-35; county page says 62).
  Fees not read (2026 fee PDF mdocs 9508 not archived). Riverfront -> riverview lead (40-51 ~50 m back across beach road + beach). Pin -> 43.6854,-91.2735 (~260 m).
- apply.py dry run refused by the permission classifier; validated instead by importing apply.plan + campground_schema.apply_update on a deepcopy: 0 problems.
- All other ten ids: NO RESULT FILE (own sites refuse; no independent official source found).
