# p3-409 Vermont notes (2026-11-11)

## Sources that work
- Park pages are at `https://www.vtstateparks.com/parks/<slug>`, and all of them returned 200. The old `vtstateparks.com/<park>.html` URLs now redirect.
  - Each page has a Season line, a Phone, and a camping count of "N tent/RV sites" (lean-tos counted separately).
  - Each page has an alerts box. Coolidge's carries a road warning. Jamaica's carries the 8-ton bridge limit.
- The 2026 Map & Guide PDFs (linked from each park page) carry a legend with an RV Sanitary Station symbol. Every park in this batch has the symbol except Big Deer.
  - The maps show site numbers and loops, and mark steep banks and prime sites.
- ReserveAmerica (`vtstateparks-visit.com`) campgroundDetails site lists give the following for each site:
  - type (Tent/RV or Tent Only);
  - max equipment length;
  - a Pull-Through tag;
  - a "Near Water" tag (sparse, and only a hint).
- Google pins came from gmpin.py through the shared browser lock. Nominatim was blocked. Overpass timed out.

## Recurring VT issues
- Manual seasons dated 2026-10-20 store `closes: 10-14` for "second Monday in October". That is Oct 12 in 2026 and Oct 11 in 2027. They cannot be overwritten, so each one is flagged.
- Many VT state-park entries have no phone, although every park page lists one.
- Stored site counts often include lean-tos. The page count of tent/RV sites is used instead.
- Pins tend to sit at the entrance or contact station rather than at the loops:
  - Brighton is ~360 m off, on the wrong pond.
  - DAR is ~300 m off.
  - Jamaica is ~400 m off.
  - Coolidge's Tent Loop is ~0.25 mi from the office and is unplaced.

## Per entry
- 4076 Allis: 18 tent/RV, max 35, pull-throughs; season changed to 05-22/09-07.
- 4091 Bald Mountain: changed riverfront to riverview. The river row is seasonal and sits behind a bank tree strip.
- 4080 Big Deer: 22 tent/RV; season 05-22/09-07. The dump station is unsupported (flagged).
- 4081 Brighton: 54 tent/RV, max 34; season 05-22/10-12; lakeview kept; pin move recommended.
- 4089 Campbell's Bay: changed bayview to not waterfront; season 05-01/09-30; 30 A + water; phone conflict flagged.
- 300 Coolidge: the agency's steep, narrow road warning makes it a drop candidate. Pin not placed.
- 4077 DAR: 47 tent/RV, pull-throughs; season 05-22/09-07; pin move recommended.
- 301 Jamaica: the riverbank claim was removed (only the lean-tos are on the river). Only 4 sites are over 20 ft. Bridge 8 t.
- 298 Lake St. Catherine: changed lakefront to lakeview (conifer belt, ~40-45 m); the creekfront claim was removed.
- 14369 Millbrook: drop candidate. The price is $50.46 for 2027, and the operator advertises ATV trail access. Mostly seasonal.
- 297 Molly Stark: 23 tent/RV, max 34, T16 pull-through.
- 359 New Discovery: 38 tent/RV, max 45. Its pull-throughs are horse sites only.

The apply.py dry run printed 12 results and 12 note rewrites, with no "!!".
