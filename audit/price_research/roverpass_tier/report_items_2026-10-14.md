# RoverPass tier-only pass, 2026-10-14: what each batch raised

ASK / HOLD / DROP? / REAUDIT? need AWH; DONE / NOTE / FLAG are changes already made, kept for the record. The pass covers the 347 tier-only entries whose website links roverpass.com (roverpass_tier_2026-10-14.jsonl, read by audit/private_gap_browser/roverpass_api.py); batch numbers carry on from the Campspot pass (1-20).

## the listing survey
- 55 of the 347 listings take bookings through RoverPass. They are priced in batches 21-24.
- ASK the other 292. 285 are directory listings nobody has claimed ("Claim my Campground", "Last Updated: 11/15/2024"), whose rate tables aren't the operator's. 3 are claimed, on RoverPass's own reservation system, with booking switched off: 7669 Morgan Shady TX, 7429 Camp Pecan Bayou TX, 7701 Pecan Springs TX. 4 listings are gone: 5326 Mulligans AR, 7488 Deer Crossing TX, 7909 West End TX, 8141 Glenwood NM. Mulligans and Glenwood link nothing else, so they now have no web presence in the database at all.
  Proposal: drop an unclaimed RoverPass link (and a "Coming soon" Hipcamp one) from website whenever an entry is touched; price the ~176 that have an operator site from their own pages; for the ~115 with no operator presence, use a dated 2024+ camper report only, or flag them under the live-web-presence rule.

## batch 21
- UNPRICED 2026 Outback RV Park MO and 2231 Bert's RV Park (Pratt) KS: bookable on RoverPass, but neither lists a rate. Outback's website is its RoverPass link alone.
- ASK 2230 Seidels RV Park and 2231 Bert's RV Park (Pratt) KS: their Hipcamp links are unclaimed "Coming soon / Verify your listing" pages. Remove them?
- REAUDIT? 3375 Sweet Minihaha WI: the park lists "Waterfront — Along water edge" and "Fish from the banks of the Sugar River within the campground"; the audit says not waterfront.
- NOTE 2661 Rifle Mountain Park CO: priced $30 from the city's fee table ($20 with an annual pass). RoverPass takes bookings but is closed until 2027-03-31 and sells only 3 months ahead, so it showed no rate. Phone kept at the city's 970-665-6400 (RoverPass lists 970-665-6563).
- NOTE operator page below RoverPass, ranges span both: 1737 Ruffit $40 with electric, $20 without, vs $55; 3238 Crossroads $50 plus tax vs $53 (and a $3 reservation fee); 3375 Sweet Minihaha $43-55 vs $50-60.
- NOTE minimums that aren't the RV sites': 1278 Back 40's "Two night minimum stay" is its Cozy Cabin's; 4634 Dublin's "2 Nite Minimum" is for Passport America stays. 3375 Sweet Minihaha's 2-night weekend minimum (its RoverPass rules) is marked in booking.min_stay.
- NOTE field fixes from the parks' own pages: 1521 Lake Chalet count 17 -> 67 (17 was its 30/50-amp water sites); 2879 4 Seasons count 43 -> 38; 1737 Ruffit max_rig_ft 65 -> 40 and pull_through true -> false (its one RV rate is back-in, 32-40 ft sites); 4090 Kenolie max_rig_ft 70 -> 40; 3375 Sweet Minihaha sewer dropped (no RV rate carries it). Counts no page states dropped: 1737 (120), 1982 (46), 3238 (34).
- NOTE 1521 Lake Chalet and 4090 Kenolie: RoverPass's rates there include tax, and the fee notes say so.
- DONE 3488 Marsh Park: website gains the campground page of its vendor, Three Guys & a Grill, where the rates are. 1982 Osage Prairie gains its phone, 417-667-2267.

## batch 22
- REAUDIT? 5088 Black River Campsites MS: RoverPass ticks "Waterfront" and puts the campground "on a meadow surrounded by a river, a pond, a farm, and a forest"; the audit says not waterfront.
- ASK 5088 Black River Campsites MS: ownership is hipcamp, but its Hipcamp listing says "Not currently accepting bookings on Hipcamp" and it books through RoverPass. Reclassify as private?
- ASK 5119 Stargaze Haven MS: RoverPass gives the phone as 601-818-5304; the entry has 601-520-3818. Kept the entry's.
- NOTE 5818 Bulldog Creek SD: RoverPass's October dry-camping cart priced the Sturgis Rally product, which carries a $15 mandatory spot fee, so that fee is left out of the note. Rally sites (August 6-16 in 2026) are booked by phone or email at $800-1,250 a week; the fee note says so.
- NOTE operator page vs booking channel, ranges span both: 7380 Bay City Holiday $50 on its own page vs $49; 7382 Bay RV $40-55 on its own page vs $45-55; 7391 Beeville $48 on CampLife, where its own domain now forwards, vs $35 on RoverPass. 7401 Blue Dog is priced $45-50 from its own rates page, because RoverPass sold no RV site on any date.
- NOTE 6033 Little Yellowstone ND: priced $20-25 from the county's page, because RoverPass offered no site on any date read. The season stays at the county's May 1-October 31, although RoverPass's calendar opens on April 16. The count is the county's 34; RoverPass says 35.
- NOTE 5990 Sandager Park ND: the $10 low end is first-come primitive camping on the grass, open to campers. The 2020 city page linked as its website still says every site is first come, first served; the hookup sites now have to be reserved.
- NOTE field fixes: counts no page states, dropped: 4833 (70), 5088 (5), 5119 (27, its street number on Duanes Loop), 6758 (10, given only by TravelOK). 5831 Camping 109: year_round false (from "seasonal") dropped, as RoverPass sells January nights; military discount added from its rules. 4833 is run by the non-profit Northeast Florida Equestrian Society, not a concessionaire. 7391 Beeville: good_sam, military and passport_america come from its RoverPass listing's "Discount Clubs" alone. The park isn't in Good Sam's directory.
- FLAG for the CampLife pass: 7391 Beeville's own domain forwards to CampLife's booking page, and booking.platform has no camplife value. The CampLife pass needs a decision on what to record there.
- DONE 4833 Jacksonville Equestrian Center: the dead /services/rv-reservations/ link is replaced by /rv-reservations/. 7391 gains https://www.beevillervpark.com/. Phones filled in for 6779 Tumbleweed (580-273-2054), 7365 Apache Park and Trail (469-325-6075) and 7401 Blue Dog (806-336-2024).
