# Alberta verification notes (set up in p3-371, 2026-11-10)

## Alberta Parks (ownership provincial; policy row `provincial:AB`)
- Campground page: https://www.albertaparks.ca/parks/<region>/<park-slug>/information-facilities/camping/<campground>/
  Plain curl (UA Mozilla/5.0) works. `h2t.py page.html` -> text. The page holds: advisories (top), prose
  with directions, "Season: May 15 - Sep 12", the site-type table (type / count / amps / $ / reservable
  dates / status), "Bookings Open <date>", amenity list ("Water - Pump" = non-potable hand pump with a
  boil/unsafe line; "Water - Tap" = potable; "First-Come, First-Served"), firewood line, "Information:"
  phone, "Facility Operator:", "Updated:" date, a Google `destination=lat,lng` directions point and the
  tear-sheet PDF (`grep -o 'href="[^"]*\.pdf"'`) = the campground map (pdftoppm -png -r 70, then Read).
- The directions point is often the entrance or one loop, and stored pins can be the park gate
  (Cold Lake was 1.4 km off). Always check on imagery: `python3 -I sat.py LAT LNG HALF_M out.jpg`.
- Booking engine shop.albertaparks.ca (Aspira/ReserveAmerica, contract ABPP). curl needs a cookie jar and -L
  (first hit 302s through go.aspiraconnect.com).
  `python3 -I ralist.py SLUG PARKID OUT.json` pages every site (site | loop | type | max vehicle length |
  amenities such as Pull-Through, Near Water, Water Hookup); `python3 -I rasum.py OUT.json "loop regex"`
  summarises per loop (count, length range, sites under 23 ft, pull-throughs, water-tagged).
  The details page shows "Status: Closed through <date>" = next opening day (park level on big parks).
  ParkIds met: Brazeau Reservoir PRA 330152, Castle PP 330291, Cold Lake PP 330128, Cypress Hills PP 330135
  (one parkId covers every campground in a park; filter by loop name).
- FCFS campgrounds (Beaver Flats, Buck Lake) are not on the shop site at all.
- Kananaskis: operator Kananaskis Campground Services (kananaskiscampgrounds.com/valleys/<valley>);
  Hwy 66 west of Elbow Falls closed Dec 1 - May 14; Kananaskis Conservation Pass already in the row.
- "This campground qualifies for the camping fee discount for Alberta seniors" appears on some pages
  (Buck Lake; KCS says 25% for Alberta residents 65+) - not in the policy row as of p3-371 (flagged).
- 2027 dates are not published in November; write the 2026 season with a note.
- A tear sheet covers a whole park: check which campground a margin note belongs to (the Cypress Hills
  "Sites 57-72 are 15 amp" line is not Firerock's).

## Municipal / private
- Campspot: `cs1.py SLUG CHECKIN CHECKOUT ...` (park record + availability; run in ./cs/, under flock with
  PYTHONPATH=~/.cache/ekko-pw) then `cs2.py SLUG PARKID guests0,2,0 TYPEID:IN:OUT ...`; read with
  `csav.py cs_av_*.json` and `csq.py cs_q_*.json` (sites listed/free, rig length range, back-in/pull-through,
  base price, park fees, Campspot fee). The availability `averagePricePerNight` includes fees; use
  `averagePricePerNightBeforeTaxesFeesAndDiscounts`. Park record `termsAndConditions` holds rules
  (check-in, rig age, bylaw season). An answer of `[]` = beyond the booking window.
  Slugs met: bonnyvillervpark (599), centennialparkclaresholm (4802), coronationdamcampground (4702).
- Google place (rating, reviews, phone, site): `flock ... gm.py "name town AB" ...` (several names, one browser).
- Municipal WordPress/Drupal sites: coronation.ca 403s curl but loads with `bw.py PREFIX URL...`;
  mdwainwright.ca pages are `?page_id=N` (Arm Lake 828 area, 830 rates, 832 campground; per-site lengths at
  /armlakeinteractivemap/sites.php).
- Gateways: `python3 -I audit/price_research/gateways.py lat,lng` (none within 40 km for any of this batch).
- Result writer: `w.py` (import w; w({...})) and the `ed(id, [(old,new)])` patcher in fix1.py.

## Added in p3-400 (2026-11-11)
- ParkIds met: Prairie Creek PRA 330188, Ram Falls PP 330189. Shop can answer curl with a Queue-it waiting
  room: delete the cookie jar (dl/jar_<pid>) and retry, or load it once through bw.py.
- FOESA campgrounds (Red Deer River, Seven Mile): rate column "FOESA Membership", no nightly fee, FCFS,
  phone 403-304-0456, no seniors line -> fees 0 and a policy_ref none candidate.
- OHV wording on Kananaskis/Clearwater FOESA pages: "OHV riding and staging is permitted" / "OHV off-loading
  within the campground" = staging, drop candidate. "OHVs must remain on trailers until they reach the nearby
  trail systems" (Prairie Creek) and "designated trails in the vicinity" (Racehorse) = keep-type.
- Red Deer River PRA has two campgrounds (North 14, South 50) ~0.8 km apart across the river; the DB has one.
- Ram Falls shop posts all 54 sites at 21 ft (pull-throughs too) - a FIT question, likely a default.
- Municipal: rockyford.ca 403s curl; bw.py innerText misses hidden tabs - dump page HTML (bwhtml.py) instead.
  Campspot slugs: rockyfordlionscampground (4740), rosemarymunicipalcampground (4873). Both closed in
  November; availability still shows type prices (averagePricePerNight includes Campspot's C$3).
- Private: Prairie Junction (Campspot prairie-junction-rv-resort-stettler-ab) adds a C$8 park fee per
  reservation; Prairie Peaks' availability Google Sheet reads as pub?output=csv (pubhtml empty to curl).
