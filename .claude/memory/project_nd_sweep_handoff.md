---
name: project_nd_sweep_handoff
description: "North Dakota sweep COMPLETE — all 4 buckets added+audited+committed+pushed (174 entries, ids 5880-6053)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 28dfddfb-bc19-4a4e-802d-8b193b941500
---

**North Dakota is a COMPLETE clean sweep** (finished 2026-07-01). ND had 0 prior entries, so like SD there are NO legacy unaudited loose ends — waterfront and inclusion are both 100% (every entry carries `waterfront_evidence` + `inclusion_evidence`). Pushed to master.

Added **174 entries, ids 5880-6053** from 247 RV Life ND candidates, across 5 commits (4 add + 1 audit):
- **state/GFP-equivalent (21, 5880-5900)** — ND state parks via `parkrec.nd.gov` + reserveNDparks (`reservendparks.com/Web/#!park/<PlaceId>`; citypark API `reservend.usedirect.com/RDR/rdr/fd/citypark`). 24 RVLife state/dnr cands → 21 keep, 3 skip (Fort Seward=historic-fort glamping; Lonetree WMA=dispersed/undefined; Shelvers Grove=closed since ~2004 Devils Lake flooding). Reclassified in-place: Mirror Lake/Hazen Bay/Doyle/Sheep Creek→local, Schnell Ranch→federal(BLM).
- **federal (19, 5901-5919)** — NPS Theodore Roosevelt NP (Cottonwood/Juniper), USACE (Downstream/Garrison, Mel Rieman+Eggerts+E.Ashtabula/Lake Ashtabula, Hazelton+Beaver Creek/Oahe, E.Totten Trail/Audubon, Douglas Creek Bay/Sakakawea), USFS Dakota Prairie Grasslands (CCC, Buffalo Gap, Summit, Burning Coal Vein, Wannagan, Magpie, Sather Lake, Bennett, Hankinson Hills). 2 skips = Grand Forks AFB & Minot AFB FamCamps (military, not publicly bookable). Many RVLife "national"-tags corrected to USFS grassland.
- **private (35, 5920-5954)** — 99 commercial → 36 after price≤2 & star≥4 gate → 35 keep, 1 skip (Big Country/Williston=monthly-only Bakken workforce). 9 reclassified commercial→local (General Sibley, Butte View, Patterson Lake, Red River Valley Fair, Lakeside Marina, LaMoure County Mem, Lake Hoskins, McGregor Dam, Lake LaMoure). Prairie Knights casino kept as real 16-site RV park.
- **local (99, 5955-6053)** — 103 city/county cands → 99 keep, 4 skip (North Park New Salem=dup of private North Park; Grays Landing=unconfirmed/only-real-one-in-TX; Parkhurst Recreation Center=dup of Parkhurst/Pipestem; St.Thomas City Campground=residential monthly/yearly only). No star/price gate for local-gov. Tobacco Gardens reclassified local→private (owner-run resort on COE land). Includes many county reservoir/dam rec areas.

**Ownership totals:** local 111, private ~26, federal 20, state 16.

**Waterfront audit 100% (174/174):** 48 pure-dry marked from research pin; 126 water-adjacent run through the full satellite/rec.gov/per-site gate (16 audit batches ~8) → **50 upgrades** (16 lakefront, 4 riverfront, 1 creekside, 22 lakeview, 7 riverview), 9 coord fixes. USACE reservoir sites confirmed via rec.gov per-site "Lakefront" flags (Beaver Creek 5909, E.Totten Trail 5910). Prairie county dam/reservoir peninsulas earned lakefront via the open-apron rule (Sheep Creek 5899, Silver Lake 5976, Sweet Briar 5983, Brewer 6006, Kota Ray 6026, Lake Tschida/Rimrock 6025, Warsing 6013, Tolna Dam 6051, Trenton 6052, McGregor 5951, Parshall Bay 6046, New Town Marina 6038, Tobacco Gardens 6044); Lazy Fish 5940 (Jamestown Res beach row); riverfront = Willowood 5971, Sandager 5990, Mouse River Park 6000, Dickey 6042. Missouri-River state parks/loops resolved to view tiers (Fort Lincoln/Rough Rider riverview; Lewis&Clark/Sakakawea SP/Ft Stevenson/Icelandic lakeview) — set back beyond the ~50m bound.

ND authorities: `parkrec.nd.gov` + reserveNDparks; rec.gov for USACE/NPS; `fs.usda.gov/r01/dpg` for Dakota Prairie Grasslands; `ndtourism.com` + county/city sites for local. RV Life Algolia key came from `campgrounds.rvlife.com/campgrounds/north-dakota` HTML. See [[project_sd_sweep_handoff]] for the identical fresh-state method; [[feedback_sequential_sweep_agents]] (ran all research + audit agents one-at-a-time).
