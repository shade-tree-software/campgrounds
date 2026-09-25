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
