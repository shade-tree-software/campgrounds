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
