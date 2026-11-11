# p3-391 Alberta notes (2026-11-11)

Tools (copied from earlier p3 dirs): ap.sh (Alberta Parks page via curl), ralist.py SLUG PARKID out.json
(shop site list; plain curl, slow on big parks: Aspen Beach ~300 sites took 25+ min, run in background),
rasum.py out.json 'regex' (loop summary: lengths, under-23 sites, "Near Water" tags), sat2.sh / crop.py
(Esri imagery), gm.py (Google panel, under flock), cs1.py (Campspot park record).

- cs1.py / gm.py / bw.py need PYTHONPATH=/home/andrew/.cache/ekko-pw and must run WITHOUT `-I`, from the
  scratch dir (not dl/), under `flock /tmp/ekko-headless-browser.lock`. cs1 writes cs_park_<slug>.json to cwd.
- Wayback refuses (bot flag): anything needing it is UNREAD.
- sat2.sh fails at small half-widths (90-100 m) for some points; take a larger tile and crop.py it.
- The shop's "Near Water" tag is not the waterfront gate (tree fringe / trail between counts against).
- Alberta Parks shop status line: grep '(Closed|Open) (through|year)' in dl/shop_<parkId>.html.

Per entry:
- 8957 Gregg Lake: pin moved 53.52315,-117.81409; lakeview -> not waterfront.
- 8840 Island Lake, 8894 Twin Lakes: see results.
- 8831 Little Bow: lakeview marginal (loop A ~40 m from the boat basin across a road; bay 90-100 m).
- 8834 Lundbreck Falls: riverfront -> riverview (Near Water sites behind trees + riverside trail).
- 8998 Moose Lake: not waterfront confirmed; taps not potable.
- 8962 Musreau: lakeview -> not waterfront; shop parkId 330358 books only the group site, so the
  campground is FCFS.
- 9048 Pelican Point (Camrose County): books on Campspot; lakefront kept with caveat (sites 32-39).
  pelicanpointalberta.com is the community association, not the campground.
- 9026 Stavely: town page www.stavely.ca/facilities.
- 9023 Bassano: rates/season only in Bylaw 954-26 (.docx) and the campground rental-rates policy PDF;
  the campground's own web page is an empty post. FCFS per policy.
- 8955 Young's Point: Big Horn loop (sites 1-35) on the south shore ~1.5 km SE of the stored pin;
  pads 25-40 m from water behind trees + reed fringe + Alces shoreline trail.
- 8934 Brewers: power 15/30 A (stored electric 0 wrong); not waterfront confirmed (Loop D 45-90 m
  through trees from a marshy bay).
