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

**WESTERN pass started 2026-09-27** (same per-state commit+push+deploy routine; running log audit/local_gap_west_log.jsonl + audit/local_gap_<st>_decisions.json). **EAST OF THE MISSISSIPPI IS NOW COMPLETE** (AWH 2026-09-27: stop there). Western-pass adds: AL 7 (13383-13389), TN 7 (13390-13396), KY 5 (13397-13401), IN 4 incl. Shakamak SP (13402-13405), IL 11 (13406-13416), WI 24 (13417-13440), MS 5 (13441-13445), MI 18 (13446-13463) = 81. Next, if resumed: the states WEST of the Mississippi (MN/OH/LA-east already done or partial; start with IA, MO, AR, LA). Patterns: city lakes are often SEASONAL-ONLY (Lake Mattoon, Lake Taylorville, Branch County Memorial) - check the operator page; WI/MI still yielded 18-24 each despite 135-150 local entries held (small village/township parks); Good Sam pins are often the mailing address (Coal Bluff, Warfield Point, Jack Lake, Hancock) - always re-pin from satellite. Findings:
- **The Good Sam cache had been left holding only the 17 eastern states** (3,042 rows) — gsgap.py silently printed 0 for AL. Re-fetched the whole directory 2026-09-27 (`goodsam_discounts.py --fetch`, ~20 min, 15,020 parks). If a state shows 0 public rows, check the cache's state counts first.
- The Midwest/South gap is real again (AL held 33 local, TN 12, KY 18): misses are big public campgrounds (Dauphin Island 151 sites, Smith Lake Park 219, Toqua 141), not obscure ones.
- **TN STATE-park gap is large and structural:** Tennessee State Parks has ~10 campgrounds closed for renovation at once (Big Hill Pond, Pickett, Norris Dam E/W, Pickwick main, Frozen Head, Montgomery Bell, Standing Stone to late-2026, Cove Lake through 2026, Nathan Bedford Forrest to 2027); Meeman-Shelby is open and also absent. Not added in the local pass — it's its own job (add each with a dated closure caveat per [[feedback_add_with_caveat_not_withhold]]).
- KY federal gap: Mammoth Cave's Houchin Ferry absent because RIDB lists it at lat/lng 0,0 (the RIDB gap pull silently drops zero-coordinate facilities). Hillman Ferry was first logged as missing IN ERROR - it is id 684; a Good Sam pin is often the mailing address, so search the DB BY NAME before calling anything missing.
- Good Sam PUBLIC_PARK is not proof of public ownership (Wildcat Creek KY is family-run; Fooshee Pass TN is held as private but GS calls it a Meigs County park).

**WEST OF THE MISSISSIPPI started 2026-09-28. IA: 50 adds (13464-13513)** - the biggest state yet, despite 245 local entries held. Record audit/local_gap_ia_decisions.json. **New instrument, and the best one for Iowa: mycountyparks.com's statewide Camping roster** (`https://www.mycountyparks.com/activities/Camping`, 173 park links; each park's `/Activity/Camping` page states site counts and hookups in plain HTML, scriptable with a Mozilla UA). It surfaced ~30 county campgrounds OSM and Good Sam both missed. It is IOWA-ONLY (all ~100 county links are Iowa counties) - other states need their own roster. Also found: a held entry pinned a full DEGREE off (Diamond Lake 3093) - the Good Sam name search is what caught it. Next: MO, AR, LA, then the plains (KS/NE/SD/ND/OK/TX) and the mountain west.
