---
name: project-canada-private-recheck
description: "2026-10-11 re-check of the 157 Canadian private-gap parks (ids 14938-15125) admitted on a site-live probe - AWH dropped 4, kept Plage Bernard with a note; 4 minimums marked, River Run closed for 2026; tools in audit/canada_recheck/"
metadata:
  node_type: memory
  type: project
  originSessionId: 697b5c76-5652-4131-bd7c-1761a58eb19c
  modified: 2026-10-12T00:22:34.147Z
---

**Done 2026-10-11, commits 63d986e..e5c2670 (5 province batches) plus AWH's calls; pushed and deployed 2026-10-11.** The 2026-10-07/08 Canada private gap admitted parks on an RV Life / Google screen plus a probe that the operator site loaded. AWH said yes to re-reading each park's own pages for closures, seasonal-only and tent-only parks after four bad entries from that pass were dropped.

**Result (`audit/canada_recheck/decisions.json`, one verdict per id):** 144 ok, 4 standing minimums marked (Cranberry 14966, Orleans 15011, Coop des Erables 15013, Lac du Repos 15048), 3 caveat note lines (Mohawk 14954 ~12% nightly, Prairie Peaks 15004 seasonal-first, Will-O-Bend 15080 lot-ownership + phone fixed to the camping line), River Run 14963 status temporarily_closed (reopens May 14, 2027 - recheck after that).

**AWH decided 2026-10-11:** dropped Waterton Springs 14988 (Google 'Permanently closed'; NCC closed it in 2017), Great Canadian Barn Dance 14991 (seasonal leased lots only, tiny homes, property for sale), 50 Small Park Resort 15090 (seasonal land-lease, no nightly RV) and Willow Cove 15094 (park-model cottages + seasonal RV only), logged in `audit/price_research/dropped_2026-10-11.jsonl`; kept Plage Bernard 15035 (traveller sites ~35-45 of ~420, ~10%) with a SEASONAL SHARE note line. So a park at the ~10% line with real nightly booking stays, with the share noted.

**Progress lives in the data:** each checked entry's `inclusion_evidence` ends `; re-check 2026-10-11: ...`; `apply.py` skips entries already carrying it.

**What the site-live probe misses (lessons):** a GoDaddy-parked domain answers HTTP 200 via a `/lander` redirect (Crowsnest Pass 14995); a site can serve an empty 200 page (Dreany Haven 15097); a JS forward to a new domain (Glacier View 15075); a directory listing that moved (Poplar Ridge 14994). Seasonal land-lease and park-model communities look like campgrounds to a probe. Google Maps' 'Permanently closed' flag caught a park closed since 2017 that still had RV Life 4*. No-website entries were re-checked under the Google-listing rule, including review recency (newest review in months).

**Quebec traveller share was recorded only where a park's own pages state it**; a full measurement (engine counts, plans, off-season imagery as in [[project_canada_no_rate_followup]]) was not done for the 44 QC parks.

**Possible next step:** the US private-gap entries admitted since the 2026-10-01 gate reversal used the same screen + probe; `audit/canada_recheck/scan.py` (plain urllib, resumable) and `bscan.py` (one-browser driver) can be pointed at them. Related: [[project_private_gap]], [[feedback_add_with_caveat_not_withhold]], [[feedback_minimum_stay]].
