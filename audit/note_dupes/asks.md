# Asks for AWH from the note read-through

- 15 Lily Bay, 17 Sebago Lake: the --AWH opener "Recommended by Grok as one of the best campgrounds in Maine." reads like bookkeeping (where the lead came from); move to curation_note?

- **1922 (Mark Twain NF, Chadwick area)** — the note says "open year-round"; the Season chip says Mar 1 – Nov 30, derived from the recreation.gov booking calendar (284 days observed). The calendar may show only the reservable window rather than the open season, so the note was left as it is. Which is right?

- **Season chips worked out from the rec.gov calendar may be booking windows** (pattern, not a single entry): several Chequamegon-Nicolet NF loops (3341, 3344, 3359 "closes Sep 7"; 3386 "closes Sep 25") have notes saying they are open to mid/late October. Sep 7, 2026 is Labor Day, so the chip may mark when reservations end rather than when the campground closes, like 1922 above. The notes were kept. Is a closer look at `season` values derived from the calendar worth doing?

- **4481 Green Acres (Clarkrange TN)** — the note says "21 full-hookup sites (water, 30/50A electric, sewer)" and also "No on-site water." The hookups chip says full hookups. The second sentence may mean there is no drinking water to fill up from. It was left as it is.

- **Booking "not reservable" vs RIDB (46 entries, pattern)** — Stony Point (5579) said not reservable / FCFS, but a dated recheck AND RIDB's catalog both showed it bookable on recreation.gov, so it was corrected. A scan found 45 more whose `booking.reservable: false` came from note prose while RIDB's per-site catalog (trip_data/ridb_campsites.json) marks 3+ RV sites reservable. Not changed: some notes said explicitly "not reservable on recreation.gov" (e.g. 3323 Ada Lake), and the catalog's per-site flag may not mean the facility takes bookings. The facility-level reservable flag or the availability calendar would settle it. Worth a pass? Ids: 3323, 3330, 3343, 3347, 3356, 3746, 5183, 5255, 6427, 6434, 6478, 6505, 6511, 8021, 9463, 9502, 9517, 9560, 9890, 9936, 9937, 9952, 9957, 9960, 9968, 9975, 10047, 10048, 10050, 10051, 10331, 10690, 10977, 11868, 11905, 11908, 12001, 12057, 12070, 12086, 12155, 12156, 12169, 12272, 12387, 13272

## rec.gov calendar seasons that are really reservation windows (chunk 030)
The season phase read opens/closes off the recreation.gov availability calendar, which only
sees the RESERVABLE window. Where the entry's own note says first-come the rest of the year
or open year-round, I set `season.year_round` (9949 Devils Garden, 12020 Furnace Creek,
12058 Ackerman, 10193 Sunset Falls). A scan of calendar-derived seasons with off-season
FCFS found only those plus 5508 Williams Narrows (closes Sep 22, note silent; left). The
Chequamegon loops above look like the same artifact. A wider pass would re-read every
calendar-derived season against the agency's stated season — want one?
