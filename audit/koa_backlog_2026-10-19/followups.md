# Follow-ups after the main quote run

## Unmatched RV Life "KOA" rows (not in koa_directory.json)
Web search 2026-10-19 says five still have live koa.com pages, so quote them by slug:
- Wapakoneta KOA Journey OH -> wapakoneta
- Allendale / West Grand Rapids KOA MI -> allendale
- Weidman KOA (Holiday; ex-Gammy Woods) MI -> weidman
- Buffalo / I-40 / Exit 143 KOA Journey TN -> buffalo
- Lava Hot Springs West / City Center KOA ID -> lava-hot-springs-city-center (the RV Life pin's 42.620,-112.012 is "West"; check the pin against 89 N Center St)

Two are no longer KOAs; vet them as ordinary private parks:
- Higgins Lake / Roscommon KOA MI -> now "Higgins Lake Campground", 3800 W Federal Hwy, Campspot slug higgins-lake-campground-roscommon-mi
- Chain O'Lakes Resort Park/KOA WI -> "Chain O' Lakes Camping Resort", 3165 Campground Rd, Eagle River, Campspot slug chain-o-lakes-camping-resort

## No-quote retries (retry.py, 2026-10-19 night)
The no-quotes were calendars that end before May 2027. retry.py re-quoted 30 of them on a Tuesday inside each
calendar (late Oct / early Nov 2026; Jan-Feb 2027 for the winter parks); gate.py and vet.py read
quotes_retry.jsonl as the last try. An off-season quote under-states a summer rate, so an over-gate one is a
firm skip, and a pass was added only with margin to spare or where the quoted night is the park's peak:
- added (decisions_06): mesa AZ (gateway), mallorytown ON (gateway), montreal-south QC (gateway), starkville MS
  $42.93, kerrville TX $46 (January), lubbock TX $48 (RV Life average $42)
- held for a 2027 quote, at the gate on an off-season night: dodge-city KS $50, cave-junction OR $49, beaver UT $49.99
- over the gate even off-season (skips): harrison, parkerstrip, colorado-river, royal-gorge, bradenton, batesville,
  brown-county, indianapolis-west, milford-lake, topeka, joplin, cooperstown, watkins-glen, canton, mount-gilead,
  sandusky, bristol, lake-conroe, fillmore, lynden, starbuck, flatwoods
- calendar closed until 2027 (retry in spring): waterloo IA, pictured-rocks MI, minneapolis-northwest MN, erie PA,
  oakdale WI, hixton WI, burney-falls CA, salem-lisbon OH, boone NC (closed 11/2/2026-4/30/2027), carbondale CO
  (nothing bookable 4/27/2027; opens later)
- woodstock NH: skip - a 3-night minimum on every night 4/30-10/17/2027, i.e. its whole season
- rusk TX: "Internet reservations are currently not available for this KOA" - no quotable rate; skip for now

## Still open
- The five unmatched slugs above all return koa.com's "Highway 404" page on the reserve form (2026-10-19), so
  they may have left the system; check each one's own web presence before treating it as a lead.
- Higgins Lake Campground and Chain O' Lakes Camping Resort: Campspot (campspot_exkoa.jsonl, 2027-06-08) puts both
  over the gate - Higgins Lake's cheapest hookup type $55.35 (only its no-hookup sites are $45), Chain O' Lakes
  $57 + a $6 online fee. Skips.
- crystal-river FL: DONE - Google Maps puts it at 28.9004,-82.5700, where newer imagery shows a new-built park
  (decisions_07, added).
