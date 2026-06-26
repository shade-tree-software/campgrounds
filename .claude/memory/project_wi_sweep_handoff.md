---
name: project_wi_sweep_handoff
description: "WI audit status — waterfront 100% done; inclusion done for the 183 non-waterfront entries only, 165 currently-waterfront WI entries still need inclusion"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4cef485f-82b3-4807-8ce0-23e58b9248fa
---

WI waterfront audit is now **100% (348/348)** — every WI campground carries a `waterfront_evidence` string. The final 113 unaudited not-waterfront entries were swept 2026-06-26 (commit bc98165): 7 upgrades (Anvil Lake/West Point/Hoeft's → lakefront, Hi-Pines → pond, Big Bay SP → coastal woods on Lake Superior, Ottawa Lake + Yellowstone Lake → lakeview), 2 coord fixes (Hartman Creek 3276, South Trout Lake 3303). The earlier 70 were audited before this session.

WI **inclusion** audit was done the same day (commit 09d8bd3) but ONLY over the **183 not-waterfront** entries — all 183 kept, 0 removed. **Loose end:** the **165 WI entries that currently carry a waterfront value** were NOT inclusion-audited (no `inclusion_evidence`) — they still need an inclusion pass to finish WI. Find them: WI campground entries with non-empty `waterfront_evidence` but empty/absent `inclusion_evidence`.

Per [[reference_inclusion_audit]] and [[feedback_waterfront_evidence_in_json]]. Six states still have unaudited waterfront entries after WI: NE, IL, NY, TN, IN, KY (per the per-state `waterfront_evidence`-coverage scan).
