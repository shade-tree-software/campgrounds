---
name: reference_state_gap_measurement
description: How to measure a state agency's campground gap from its own booking portal, and the 2026-09-21 answer — ~1-3%, far below the SD data point
metadata:
  type: reference
---

The state face of the non-RV-Life gap was measured 2026-09-21 on OH, FL and MN:
**2 real misses across 230 entries (0.9%)**, or 2.4% pooled with SD's earlier 5 of 59.
Extrapolated over 2,202 state-ownership entries that is **roughly 20-55 campgrounds** —
against the federal gap's 334 known rows. See `audit/state_gap_2026-09-21.json` for the
per-candidate verdicts and `[[project_remaining_work_map]]` for what it displaced.

**Match FACILITY by facility, never park by park** — this is the rule the first run got
wrong. A place may hold several campgrounds (Paul Bunyan State Forest holds Mantrap Lake,
which we have, and Gulch Lake, which we did not), so a park-level name match swallows the
ones you are looking for. And a park's coordinate is sometimes the agency's ADMIN address:
ReserveOhio pins Muskingum River SP at an office 35 km from its Ellis Lock #11 campground,
so distance-only matching reported entry 1018 as a gap. The first pass published "3 misses,
1.3%" on that false positive. A generic facility name ("CAMP", "Group Camp", "Family
Campground") must be corroborated by position or it matches nothing — Long Key's facility
is literally "CAMP", and Lafayette's "Family Campground" matched a park 300 km away.

**Method — `audit/state_gap_portal.py`.** A state whose booking portal runs on US eDirect
publishes its whole park list keylessly: `<base>/rdr/fd/citypark` (parks with coordinates)
and `<base>/rdr/fd/facilities` (what is bookable at each). Diff the parks against our
entries by name-token overlap + haversine, then keep only the unmatched parks that have a
camping facility. Judge those by hand.

- **The facility NAME is the classifier; `FacilityType` is uniformly 2 and worthless.**
  "Ellis Lock #11 Campground" vs "Adams Lake Day Use Area" vs "MILTON MARINA A DOCK".
- **Most unmatched parks are not misses.** FL listed 161 parks, 102 unmatched — museums,
  springs, preserves, fishing piers — and only 2 had any camping. Skipping the facility
  classification would have turned a 0% state into an apparent 130% one.
- Known portals: `ohiordr`/Ohiordr, `floridardr`/FloridaRDR, `mnrdr`/MinnesotaRDR.
  **California has LEFT the platform** (`calirdr.usedirect.com` no longer resolves), and
  ReserveAmerica/Aspira states publish no clean park list, so this does not generalise to
  all 48 ([[reference_usedirect_deep_reservation_links]]).

**The finding that matters is WHERE the misses are.** Both sit outside the flagship
reservable park system — they are state FOREST campgrounds — and SD's five were Lakeside
Use Areas. The flagship state park systems
are essentially fully covered. So when a state is worth checking, check its *secondary*
categories — forests, parkways, lakeside/wildlife areas — not its headline parks.

**Two blind spots keep a 0 from being a clean bill of health:** the portal only sees what
the agency takes RESERVATIONS for (Ohio's six state-forest campgrounds are FCFS and absent
entirely — checked by hand, all horse or hunter camps bar the two held), and a second
division may run a second portal (Florida Forest Service is not in ReserveFlorida).
MN's state forests carry 0,0 coordinates, so they can never match and always surface.

Related: [[reference_rvlife_index_has_gaps]], [[reference_ridb_gap_pipeline]],
[[feedback_absent_is_not_unknown]].
