# WI notes p3-485 (first WI batch)
## Sources (for later WI batches)
- Rusk County Parks: parks.ruskcounty.org (Konect Parks engine) answers plain curl. /parks/ home = fees ($30), season, booking rules. Per-site pages /parks/camping/<cg>/site_N/ give pad dims + electric/water + photo /parks/i/ii/l__aN.jpg. Price not shown on book_now step (needs form).
- ruskcountywi.com = Cloudflare challenge (403) - refused, don't retry.
- Esri street map (tools/street.py) shows OSM roads - handy when canopy hides loops.
## Entries
- 3593 Audie Lake DONE: $30, 15 sites 34-95 ft, 30A shared, no dump, year-round, after_cutoff 7 d; lakefront -> lakeview (sites 10-15 photos through woods). Leads: Perch Lake (Rusk) + Murphy not in DB.
- 3571 Beauford DONE: low 25->23, max 7 nights, year_round cleared. soldiersgrove.municipalimpact.com answers curl.
- 3401 Broken Bow: brokenbowcampground.com answers 406 Mod_Security 'Not Acceptable!' to curl (UA Mozilla/5.0), home and rates.htm - REFUSED, no result written. Earlier read 2026-10-16 in audit/price_research/private_2026-10-16/pages_WI.jsonl. Google 4.8 (52). Imagery canopy-blind.
- 3481 Brown County Fairgrounds DONE. browncountywi.gov answers curl (old /parks-department/camping/ redirects to /general-information/camping/); PDFs under /i/f/files/Park-Management/ fetch fine.
- 3395 Callahan DONE: callahanlakeresort.com answers curl (WordPress); rates page still 2025.
- 3396 Cedar Falls DONE: wvic.com answers curl; 2026 colour site map PNG on the site-plan page; booking online.premiercampground.com.
- 3383 DOVR DONE: dovr.org (WordPress) answers curl; Campspot not re-read.
- 3449 Dells of the Eau Claire: www.marathoncounty.gov answers Akamai 'Access Denied' 403 to curl - REFUSED, not retried; no result written. Batches after: every Marathon County park page (and its showpublisheddocument PDFs) is on that host.
- 3373 Eagle Cave DONE: eaglecave.net answers curl.
- 3478 Eagle Point DONE: cityofcumberland.net answers curl (thin page); Campspot park record via tools/cs1.py in the browser (curl 403s campspot.com, the brief's sanctioned browser recipe); park-maps.campspot.com SVG answers curl, render with tools/svgpng.py.
- 3500 Blackhawk Lake DONE: blackhawklake.com (Wix) answers curl, its pricing/map PDFs too; booking on CampLife.
- Headless browser: no browser left running (each helper launches + closes its own Chromium under flock).
