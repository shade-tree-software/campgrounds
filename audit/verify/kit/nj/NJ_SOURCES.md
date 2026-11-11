# NJ sources (p3-404, 2026-11-11)

Worked:
- NJ Outdoors `https://www.njportal.com/DEP/NJOutdoors/Park/Details?locationId=N` over plain HTTP (UA Mozilla/5.0): park listing, per-site catalog (type, TrailerLength, features incl. waterfront flag, Resident/NonResident cost), and the availability calendar JSON (ClosedSeasonal / ClosedNonSeasonal flags). IDs: Allaire 2, Bass River 3, Belleplain 4, Byrne 5, Cheesequake 6, Parvin 10, Spruce Run 12, Stephens 13, Stokes 14.
- DEP park pages `https://dep.nj.gov/parksandforests/state-park/<slug>/`: plain HTTP gets an Incapsula block; the headless browser (flock'd driver) reads them fine. Use a cloned-body textContent so hidden tabs (Camping) come through.
- DEP campground maps (`dep.nj.gov/wp-content/uploads/parksandforests/...`): 403 to plain HTTP; fetched inside the page context (fetch -> base64) after loading a DEP page.
- morrisparks.net (Mahlon Dickerson) plain HTTP 200; Morris County WebTrac `njmorris.myvscloud.com/webtrac/...` 200 (old register1.vermontsystems.com redirects there).
- monmouthcountyparks.com page.aspx?id=2522 200; fee PDF on co.monmouth.nj.us 200.
- koa.com reserve flow via the driver (koa.py); Campspot via the driver (campspot.py).

Refused / unread:
- Wayback Machine: mostly 429.
- Campspot plain-HTTP API: CloudFront 403 (driver works).
- Overpass: 406 then connection refused (imagery used instead).
