---
name: project_sd_sweep_handoff
description: South Dakota sweep COMPLETE — all buckets added+audited+committed (171 entries, ids 5709-5879)
metadata:
  type: project
---

**South Dakota is a COMPLETE clean sweep** (finished 2026-07-01). SD had 0 prior entries, so unlike most states there are NO legacy unaudited loose ends — waterfront and inclusion are both 100%.

Added **171 entries, ids 5709-5879** (170 SD + 1 NE), across 5 commits:
- state/GFP (59, 5709-5767) — Custer State Park units, GFP State Recreation Areas, Missouri River reservoir SRAs (Oahe/Sharpe/Francis Case/Lewis & Clark/Belle Fourche), eastern glacial-lake parks.
- federal (28, 5768-5795) — Black Hills NF (Sheridan Lake South, Pactola, Deerfield complex Dutchman/Whitetail/Custer Trail, Roubaix, etc.), USACE (Left Tailrace, Cold Brook), NPS Elk Mountain (Wind Cave), Custer Gallatin/Buffalo Gap NG.
- private (49, 5796-5844) — 39 private RV parks + reclassifications (8 local, 1 state SD Fairgrounds, 1 federal Cedar Pass).
- local (35, 5845-5879) — county/city parks; no star/price gate.

**Ownership totals:** state 59, federal 30, private 40, local 42.

**Waterfront audit 100% (171/171):** 41 dry entries marked from research pin; 130 water-adjacent run through the full gate → **53 upgrades** (21 lakefront, 22 lakeview, 4 riverfront, 4 riverview, 2 creekside), 4 coord fixes. The Missouri River reservoirs were the crux. Per-entry proof in `waterfront_evidence`.

**Inclusion audit 100% (171/171):** folded into the add stage — every entry carries `inclusion_evidence`. Notable skips: membership parks (Rushmore Shadows, Hart Ranch), closed (Cottonwood Springs/2026, Roosevelt Events Center, Sunrise Wasta), equestrian (Willow Creek Horse Camp, Hay Creek Ranch), under-23ft (Sage Creek 18ft), day-use-only (Wrinkled Rock), group-only (Sheridan Northside), workforce (Wiste), faith retreat (Broom Tree), unconfirmed (Ipswich, Butter Butte, Oacoma Flats).

**One NE entry:** id 5771 Cottonwood @ Lewis & Clark Lake is physically in Nebraska (south of the 43rd parallel), came through the SD RV Life pull, recorded as state NE. Audited → lakefront.

SD authorities used: GFP park pages `gfp.sd.gov/parks/detail/<slug>/` + Camp SD reservation portal (`campsd.gooutdoorssouthdakota.com` / older `reservations.gooutdoorssouthdakota.com/FacilityDetails.aspx?facID=<id>` — facIDs proved unreliable across agents, so the GFP park page is the authoritative primary website). See [[project_mi_local_stage_handoff]] and other state handoffs for the sweep method; RV Life Algolia key came from the SD park page HTML.
