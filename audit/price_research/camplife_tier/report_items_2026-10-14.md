# CampLife tier-only pass, 2026-10-14: what each batch raised

ASK / HOLD / DROP? / REAUDIT? need AWH; DONE / NOTE / FLAG are changes already made, kept for the record. The pass covers the 88 tier-only entries whose website links camplife.com (camplife_tier_2026-10-14.jsonl, read by audit/private_gap_browser/camplife_api.py); batch numbers carry on from the RoverPass pass (21-24).

A CampLife booking is recorded as booking.platform "operator": CampLife is software the park runs as its own reservation system. That settles batch 22's FLAG; 7391 Beeville keeps "roverpass", which still takes its bookings.

## batch 25
- ASK/DROP? 1265 Cutty's Sunset Camping Resort OH: 470 sites, 'Weekend and seasonal camping options available', 'Trailers Currently For Sale', and only 37 sites sold online. Priced $61-76 from its own 2026 rates page; CampLife took no date, as the park is open May 1 to October 15. Keep or drop?
- ASK/DROP? 1312 Blue Water Campground OH, UNPRICED: 209 sites, and its home page says to 'reserve a seasonal or weekend lot'. CampLife sells 12 sites and takes bookings from January 1, and no page posts a rate. Keep or drop?
- ASK/DROP? 1977 Timberlake Campground MO and 2064 Sunny Sites Campground MO have no web page, only Facebook, and are priced from dated RV Life camper reports: Timberlake $35 (8/2025, 7/2026), Sunny Sites $25-28 (7-10/2026). Sunny Sites' main building and cabins were still being built in September 2026. Keep both?
- ASK 1977 Timberlake's phone: the entry has 573-898-2077; RV Life's park record gives 314-226-7146. Kept the entry's.
- REAUDIT? 1981 Campus RV Park MO, ownership local: the city's page for it answers 404, the park's own history says the Swope family sold the mansion grounds to the RLDS Church in 1923, and reviewers call it church-run or private.
- NOTE once-a-stay charges, read from the one-night and two-night quotes: 1227 East Fork WV $6 (its cancellation policy names it), 1256 Baylor Beach OH $8 and 1980 Mozingo Lake MO $10 (its own page names a $10 booking fee) are stored as reservation_fee. 1476 Top-A-Rise NY's $3 is treated as CampLife's per-reservation charge, like the usual $3.50, and not stored. 1347 West Boggs IN's $9.00-9.32 varies with the rate, so it isn't stored; its fee note names the charges its policies list.
- NOTE 1256 Baylor Beach: the range runs from CampLife's October quotes ($39.20-47.20, the off season's 20% off, extra persons included) to the park's in-season $59 for full hookups.
- NOTE 1823 Harmony Ridge NJ: CampLife asked for 2 nights on every date read, October 2026 to June 2027, while its own page asks 2 on regular weekends and 3 on Memorial Day, July 4th and Labor Day weekends. booking.min_stay records both, and the note dates CampLife's. Priced $60, $30 per adult.
- NOTE priced from the parks' own pages: 1265 Cutty's and 1282 Loveberry's, closed on every date CampLife was read, and 1347 West Boggs, whose quotes carry the varying charge above.
- NOTE field fixes: 1265's count 500 becomes 470 (its About page) and its booking platform roverpass becomes operator (its only booking link is CampLife). Counts dropped: 2064's 15, from an undated Facebook post written before its pull-throughs were built (reviewers stayed on sites 16-22 in 2026), and 1977's 40, on no page of the park's.
- DONE wrong-park links: 1977 Timberlake MO linked CampLife's Timberlake Campground in Brandon MS, and 2064 Sunny Sites MO linked Sunny's Campground in Wauseon OH. Each website is now the park's Facebook page, the booking group is removed (nothing takes bookings online), and inclusion_evidence carries a dated re-check.
- DONE builder: CampLife site types named "Shelter" are skipped; Mozingo sells its picnic shelters as sites at $35-75 a day.
