# p3-502 (WI) working notes - 2026-11-16

Result files written (audit/verify/results/): 3491 3458 3522 3468 3557 3591 3578 3542 3452.
No result file: 3460 (own pages refuse - Cloudflare), 3524 (operator domain NXDOMAIN, archive offline, village site 403).
apply.py dry run on the nine: 9 results ready, 9 note rewrites, no "!!".

## 3491 Adams County Castle Rock Park
197 site pages read (adamscountyparks.com engine). Daily+Weekly 61 / Seasonal 59 / Yearly 71 -> ~31% nightly -> "Mostly seasonal" note.
Lakefront -> lakeview: premium sites 89-95 (~43.9094,-89.9405) are inland of the paved loop road. $27-35 2027 + $10 fee. Google 4.6/472.

## 3458 Avoca Lakeside Park
Village page: $30/$35, phone booking. Directory-only values cleared (count 105, 50A, season, dump). Lake ~250-300 m N behind houses: not waterfront. Google 4.5/77.

## 3522 Babcock (Dane)
Closed for 2027 (US-51 reconstruction), reopen 2028. $38 + $10 admin; $2 military. Yahara channel 15-20 m behind trees: not waterfront. reservation.danecountyparks.com NXDOMAIN -> reservedane.com.

## 3468 Brigham (Dane)
23 sites (8 electric). Pin move 43.0271,-89.8191 -> ~43.0275,-89.8157 (~290 m). Phone null -> 608-224-3730. Website parks-lwrd -> danecountyparks.com/park/Brigham.

## 3557 Chain-O-Lakes (Phillips)
$30 FCFS. Lakeview kept (20B behind 30-40 m tree belt). Google 4.5/19.

## 3591 Evergreen (Wausaukee)
Campspot 403 today; Oct capture: ~30/38 nightly, $29-43 + $4. Not waterfront. GS park true. Google 4.6/29.

## 3578 Harbour Village Resort (private) - DROP CANDIDATE
"SITES START AT $70/NIGHT"; GS false (MEMBERSHIP_PARK); no gateway in 40 km. Condo sites for sale (test 5). Google 4.2/639.

## 3460 Little Sand Bay - NO RESULT
townofrussellwi.gov + townofrussell.org: Cloudflare "Just a moment" 403. Not retried.
Imagery: loops ~100-200 m SW of pin 46.9458,-90.8868; Lake Superior beach ~145-250 m N, only park roads/ballfield between -> likely `coastal walk` (stored not waterfront), unverified.
Google 'Little Sand Bay Campground' 4.3/216, phone 715-779-5338 (stored 715-779-5233).

## 3524 Melrose City Park - NO RESULT
melrosewisconsin.com NXDOMAIN; Wayback availability none, CDX "Temporarily Offline". melrosewi.gov/recreation-park 403.
One PDF from melrosewi.gov returned 200 in the same command (Newest-Parks-Reservation-Form-Updated-5-12-26.pdf): lists shelters, ball diamond, pool - no camping; Village Hall (608) 488-3191.
Inclusion evidence aggregator-only (ParkAdvisor). Google lookup returned a "Results" list (4.7/12 at 303 Clark St - not confirmed as the park).

## 3542 Morris-Erickson (Chippewa)
27 per-site pages (2-28) all Book Now; pads 34-64 ft. $20 + $7 electric (50A all sites), $7 res fee.
Terms PDF me_terms_4-9-25: "three-night minimum, fourteen-night maximum per reservation", 10 days ahead; caretaker sells unreserved sites nightly FCFS -> drop-candidate flag (standing minimum) for reviewer.
Lakefront -> lakeview: only site 9 has its own dock; others across picnic area/beach (day use). Pin = boat launch, loop ~150 m W.
Season May 1 - Oct 31 (closed 11/1). Google 4.6/76.

## 3452 North Wood (Wood)
99 per-site pages + group: 76 x 50/30/20A, 23 non-electric (mostly tent/no pad; 82, 83 fit all campers). Waterfront: Yes on 63-67 only, ~20-32 m from Lake Manakiki (11 ac), grassy bank w/ scattered trees -> lakefront kept with caveat.
2027 $23/$28/$31, off-season $20/$25, $10 fee. Reservations required, same-day OK, 3-night holiday min, 14 max. Closes Oct 31 noon (last night Oct 30). Google 4.6/494.
Stored fee provenance cited Dexter page ($40 = Dexter S&W).

Leads: none - Chippewa's Otter Lake (3573) and Pine Point (3503), Wood's Dexter (3558) and South (3597) are already in the DB.
