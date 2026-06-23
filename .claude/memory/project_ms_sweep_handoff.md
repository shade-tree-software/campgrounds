---
name: project_ms_sweep_handoff
description: Mississippi sweep progress — state/federal/local DONE+committed+audited; private bucket (66 gated) pending
metadata: 
  node_type: memory
  type: project
  originSessionId: 12985b82-ef0d-4f32-b017-68712a884846
---

Mississippi campground sweep (started 2026-06-23). Git log is the authoritative progress record; this is the summary.

**DONE + committed + waterfront-audited:**
- **state** (ids 4996-5030, 35 added): MDWFP state parks + State Fishing Lakes + Grand Gulf; 2 excluded (Great River Road SP day-use, Lake Charlie Capps WMA). 3 locals folded in (Archusa, Kemper, Shepard).
- **federal** (ids 5031-5056, 26 added): USACE Sardis/Enid/Grenada/Arkabutla + Tenn-Tom (Vicksburg & Mobile districts), USFS NF lakes (Choctaw/Turkey Fork/Chewalla/Clear Springs/Marathon), NPS Natchez Trace (Jeff Busby, Rocky Springs). 11 excluded (tent-only, primitive <=20ft, equestrian, aggregation artifacts, day-use, military FamCamps, Davis Bayou dup id 378).
- **local** (ids 5057-5079, 23 added): PHWD + Pearl River Basin Dev. District + Pearl River Valley Water Supply District (The Rez) water parks, county/city parks. 6 excluded. Fulmers→private, Simpson County Lake→state corrections applied.

**PENDING — private bucket (last):** RV Life commercial bucket = 205 (after gov-name-scan removed to local). Gate (price_level<=2 AND star_rating>=4, non-membership) → **66 candidates**. Detection file: `/tmp/ms_all_rvlife.json` (RV Life Algolia app H0LPZK92QJ, park index, MS via insideBoundingBox). Vet each per inclusion criteria (real transient RV campground, not seasonal/residential/workforce/club/membership; dead-website strike), pin + elevation + waterfront-audit. Same per-state pipeline as [[feedback_sequential_sweep_agents]] (run agents one at a time).

**MS-specific notes:**
- MDWFP reservations moved to `reserve.mdwfp.com` — but it's an Angular SPA serving the same shell for every path, so per-park deep links can't be verified; used the official `mdwfp.com/parks-destinations/park/<slug>` (and `/fishing-boating/lakes/<slug>`) pages as the website (verified real). The old `mississippistateparks.reserveamerica.com` domain is DEAD (DNS fail).
- PHWD park pages live at `sites.google.com/phwd.net/phwd/<slug>`.
- "Water Park" in MS = regional water-district park (PHWD / Pearl River Basin DD / The Rez) = `local`. Many operators sell explicit "waterfront" vs "inland" booking tiers — a strong waterfront lead.
- USACE reservoirs (Arkabutla/Enid/Grenada/Sardis) are under heavy winter/repair drawdown — audit measures to high-water/beach edge, not the drawn-down waterline (many earned lakefront on open aprons).
