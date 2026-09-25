---
name: reference_local_gap_measurement
description: Local (county/city/regional) campground gap MEASURED 2026-09-25 via OpenStreetMap - roughly a third of OSM-visible local campgrounds are missing, by far the largest remaining gap
metadata:
  type: reference
---

Measured 2026-09-25 with `audit/local_gap_osm.py` (record: `audit/local_gap_2026-09-25.json`).
**Result: of the local-government campgrounds OpenStreetMap can see, roughly a third or more
are not in the database** - Minnesota 9 of a 14-candidate sample were real misses (64% of 56
unmatched, vs 63 matched -> ~36% missing); Ohio the same shape. PA and TX samples were small
but pointed the same way. Scaled over 2,512 local entries that is **several hundred to 1,000+
campgrounds** - an order of magnitude beyond the state (~1-2%, [[reference_state_gap_measurement]])
and federal ([[reference_ridb_gap_pipeline]]) gaps.

**Instrument:** OSM `tourism=camp_site|caravan_site` in the state whose operator/owner/name reads as
local government (county, city, township, metroparks, park district, watershed/conservancy
district...), matched to ANY entry within 1.5 km (4 km with a shared name token). Overpass's main
endpoint 504s under a statewide query - the script retries and alternates mirrors.

**The unmatched list is candidates, not misses** - metroparks backcountry/tent sites, group
camps, fairgrounds and trail-association camps come through; judge before counting. It is also
a LOWER bound on the pool: a local campground with no operator tag and no "County"/"City" in its
name is invisible, and Ohio's MWCD had 3 misses OSM did not tag as local at all.

**What the misses look like:** not obscure. Burlington Bay (City of Two Harbors, 136 full-hookup
sites), Tappan/Seneca/Charles Mill/Leesville (Muskingum Watershed Conservancy District - we hold
3 of its 9 campgrounds), Pierz City Park (38 W/E sites), Swift Falls County Park (rigs to 45 ft).
Small-town city parks and county parks with 5-40 electric sites dominate in the Midwest.

**Detection for a sweep should be per state from several sources**: this OSM pass, the county
websites (Minnesota counties publish per-campground pages), watershed/conservancy districts and
metroparks, and the state tourism directory - not RV Life ([[reference_local_campground_method]]
was RV-Life-based and is why the gap exists).

**MN swept 2026-09-25** (commits 1102e1b, 48b16cb): all 56 unmatched OSM candidates judged, 26 added (13318-13343), 27 excluded, 3 duplicate nodes. Record: audit/local_gap_mn_decisions.json — the per-state template for the next ones. Yield ~46% of candidates; most no's are primitive county canoe-trail camps with no published size. Write each verdict into the decisions file AS you judge it — a context reset lost 20 verdicts once and they had to be redone.

**OH swept 2026-09-25** (commit d31918d): 11 added (13344-13354), 18 excluded; record audit/local_gap_oh_decisions.json. OSM's local-TAGGED pool was nearly useless in Ohio (20 unmatched, almost all metroparks tent/backcountry sites). What worked: (1) read EVERY unmatched OSM campsite by name, not just local-tagged ones; (2) **match the Good Sam directory against the DB** (goodsam_discounts.Algolia + walk, `campground.address.stateCode:"XX"`; ~1 min, free) - its PUBLIC_PARK rows with no entry nearby were 7 of the 11 adds. Good Sam coords can be wrong (Winton Woods pinned on a high school): take the pin from satellite. mwcd.org / reserve.mwcd.org 403/405 every scripted fetch; cite MWCD text from search excerpts. The same Good Sam match surfaced ~100 unmatched PRIVATE Ohio campgrounds (KOAs and Jellystones among them), so the private gap is NOT "probably fine" - measure it.

**Eastern states swept 2026-09-25, ME → FL (17 states, one commit + push + deploy PER STATE, as AWH asked):** 36 adds, ids 13355-13382 (MA 2, RI 1, NY 4, NJ 1, PA 4, WV 3, NC 1, GA 3, FL 9; ME/NH/VT/CT/DE/MD/VA/SC none). Records: audit/local_gap_<st>_decisions.json + the running audit/local_gap_east_log.jsonl. The eastern local gap is SMALL (VA/MD/SC county campgrounds were already held); the Midwest-sized yield does not repeat on the seaboard. Lessons:
- **Read every unmatched OSM name** (`audit/local_gap_unmatched.py --state XX`, caches Overpass under trip_data/osm_campsites/); local-TAGGED OSM caught almost none of the real adds. A mirror can return a truncated answer (PA: 34 vs 1,017 elements) - sanity-check the count.
- **Florida water management districts are the `local` precedent** (Cotton Lake/NWFWMD, Istokpoga/SFWMD): NWFWMD's nwfwater.com roster gave 8 RV-capable reservable sites. SJRWMD/SWFWMD/SRWMD campsites NOT yet rostered.
- The same listing exposes other gaps, logged as `state-gap`/`federal-gap`/private notes in each decisions file: **NY state coverage is thin** (DEC Rogers Rock, Luzerne, Forked Lake, Alger Island, Moose River Plains; OPRHP Buttermilk Falls absent - NY holds only 102 state entries); NH Deer Mountain, VT Maidstone, NJ High Point; NPS C&O Canal drive-ins (MD) and 4 VA USFS campgrounds; private gaps large in ME (~150), NJ (~60, only 19 NJ entries total), NC (~120), FL (~250).
- Common local exclusions on the seaboard: seasonal-dominated town campgrounds (Bulwagga Bay 100/150 seasonal, Monitor Bay seasonal-only fees), residents-only (Mullin's Head, Alverthorpe), 4WD outer-beach (Suffolk's Shinnecock East/Cupsogue/Montauk, Sandy Neck), tent-only county parks (Mauch Chunk, Mill Creek, Lake Mills), no live web presence (Jonesport, Santway, Paden City).
- Next: move WEST (AL, TN, KY, OH-done, MI, IN...). The Midwest is where the gap is big.
