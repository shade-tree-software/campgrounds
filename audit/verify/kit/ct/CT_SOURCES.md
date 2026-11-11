# CT sources (p3-406, 2026-11-11)

WORKED (plain curl, UA Mozilla/5.0):
- ctparks.com/parks/<slug> - per-park camping block: season (2026 + 2027 open/close), office phone, site count, resident/non-resident rates, amenities, pets. Slugs: hopeville-pond-state-park, lake-waramaug-state-park, pachaug-state-forest (Green Falls + Mt Misery), rocky-neck-state-park, american-legion-state-forest (Hawes), hammonasset-beach-state-park, housatonic-meadows-state-park, macedonia-brook-state-park, salt-rock-state-forest.
- ctparks.com/media/<n>/download?inline - campground map PDFs (render with pdftoppm -r 110). 407 Hawes, 422 Hammonasset, 428 Waramaug, 433 Green Falls, 434 Mt Misery, 450 Rocky Neck, 529 Housatonic, 546 Macedonia, 2470 Salt Rock (dated 2025-10-30).
- portal.ct.gov/DEEP/State-Parks/Parking-and-Camping-Fees---CT-State-Parks-and-Forests - fee table (one line per campground, resident / non-resident).
- connecticutstateparks.reserveamerica.com campgroundDetails.do?contractCode=CT&parkId=<pid> - site list (type, loop, Max Vehicle Length, Back-In/Pull-Through, Near Water); paged lister ralist.py. campsiteDetails.do?...&siteId=<id>&parkId=<pid> with a cookie jar gives Electricity Hookup amps, Water/Sewer Hookup, Full Hookup, Driveway Entry, Max Vehicle Length.
  Park IDs: 100100 Hopeville, 100101 Hammonasset, 100103 Hawes, 100105 Macedonia, 100107 Rocky Neck, 100108 Housatonic, 100110 Waramaug, 100128 Salt Rock, 100802 Green Falls.
- recreation.gov /api/camps/campgrounds/<id>, /rates, /api/search/campsites?fq=asset_id:<id> (West Thompson 233476).
- Operator sites: campcirclec.com (Circle C), highlandcampground.com (+ rates.html, rules.html, map.html).
- Google Maps reviews via rev.py under flock (helpers).
- Esri World Imagery export (sat.py).

REFUSED / UNREAD:
- nae.usace.army.mil West Thompson Lake page: 443-byte stub. Not retried with another UA (classifier refused that as bot-check circumvention). UNREAD.
- Nominatim: empty response once (not needed).
- Overpass: no results for the queries tried.
