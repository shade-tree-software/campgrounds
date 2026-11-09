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

## Follow-up, not an ask: note vs RIDB hookups (chunk 049)
- 13686 Putah Canyon: the note says "some RV sites have electric for an extra fee"; `hookups.electric: 0` was derived from the RIDB catalog 2026-10-20 (every RV-bookable site typed NONELECTRIC). Per the trust-rec.gov rule the field stands; the note sentence was left as is. Worth one look at the concessionaire's page to see whether the electric is a paid add-on RIDB doesn't model. **2026-11-08: it is ('Power Hook-ups (when available) $15'); electric now unknown with a hookups note, note sentence cut.**

## Answered by AWH 2026-11-08
- Grok openers (15, 17): move to curation — done.
- Calendar-derived seasons: yes, run a pass against each agency's stated season.
- The 45 RIDB "not reservable" conflicts: yes, check against rec.gov's facility flag and availability calendar.
- (round 2) 179: --AWH "Recommended in _Where_Should_We_Camp_Next?_ by Stephanie Puglisi." reads
  like sourcing, like the Grok lines; move it to curation? (16's Grok line was moved, per the 15/17 answer.)
- (round 2) 246: --AWH "Several primitive RV sites right on the French Broad River" vs the Sites
  note's two (26, 28), which Campspot showed unbookable. Keep the note as is?
- (round 2) 236: kept the --Claude "DWR bars camping within 300 ft of a lake or boat ramp" line
  although booking.note says it: the note's "including one on the lake" would read as a camp spot without it.
- (round 2) 1773: note keeps "RV Life ~9/10" with no Rating chip (stars missing from rating).
- (round 2) 2101: note's site counts (~80 W/E incl. 10 FHU + 13 E-only, ~154 primitive) vs the
  Sites note (79 W/E, 10 FHU, 2 E-only, 147 primitive); which is right?

## Round 2, chunks 008-021 (2026-11-08) — all left as they were
- 4100: "No hookups per official reservation page" contradicts the later "Correction 2026-10-12" segment, the 30A chip and the Fees note (30-amp on the five RV/Trailer sites). Cut that sentence and move the correction framing to curation?
- 4859: note says "RV Life 8.3*/35 reviews", but no Rating chip shows.
- 5016: note says 14 pads with electric/water; Fees note says 12 sites; chip shows 14.
- 8834: note has 29 powered / 17 unserviced; Fees note has 26 / 14.
- 8889: note has 80 unserviced / 24 powered, ~May 1-Oct 14; Fees note has 79 / 21 (15/20-amp), May 8-Oct 4.
- 8998: note "Open May-Oct" (Season note agrees) vs Fees note May 14-Sep 8.
- 10653 Deschutes River SRA: note says A-Loop first-come Dec-Mar, Season note Nov 1-Mar 31; note calls B-Loop "primitive RV/tent", Fees note says primitive = tents only.
- 13086: note says "22-38" 20-amp sites; Sites note says 22.
- 13534 Alma RV Park: note 28 of 38 seasonal + 9 transient; Booking note 9 transient, the other 29 seasonal.
- 14222: note "sewer sites are limited"; Sites note counts 76 of 137 with sewer.
- 14367: note and Sites chip say RV sites to 45 ft; Fees note says max 30 ft.
- 14621 Lum Park: note says no weekly-or-longer rates; Fees note gives weekly $330.
- 14983 Cedar Cove: note says tent sites $40; Fees note prices 2-way sites at $40.

## Answered by AWH 2026-11-08 (round 2) — applied
- 179: keep the Puglisi book line visible (a published recommendation is significant).
- 246: drop the --AWH "several primitive RV sites" wording — done.
- 4481: drop what contradicts the published source — "No on-site water." cut (operator: "Our
  full hook-up sites provide water, electric, and sewer services"); hookups now sourced to it.
- Main note vs group note: the group note wins when it is the more recent read. All 13 were
  (notes in place by Jun 11-Oct 9 per their derived provenance; group reads Oct 10-Nov 5):
  2101, 4100 (correction story to curation_note), 5016 (sites 12, MDWFP page), 8834/8889/8998
  (sites + season from the Alberta Parks camping table), 10653, 13086, 13534, 14222, 14367
  (max rig 30 ft, ResNexus), 14621, 14983 — conflicting text cut.
- 11369 Spillway (season follow-up): rec.gov over the note — max rig 32 ft; the FS "16 foot"
  is not credible. Note's 25-42 ft cut.
- 10073 Anderson Cove: answered with the source (chip = rec.gov calendar = FS peak season;
  FS also lists FCFS Nov-Dec and a winter non-peak season). **AWH: year-round, booking.season 04-24..10-31 — done.**
