---
name: project_ne_sweep_handoff
description: "NE audit status: waterfront 100% (219/219); inclusion done for the 139 non-waterfront entries only; 80 currently-waterfront NE entries still need inclusion"
metadata: 
  node_type: memory
  type: project
  originSessionId: c6cdddcb-a27f-4cae-b56c-67eb1f09f570
---

NE (Nebraska) audit progress as of 2026-06-29:

**Waterfront audit: 100% COMPLETE (219/219).** The 105 NE non-waterfront entries
that lacked `waterfront_evidence` were forward-audited (satellite + per-site/agency
gate) and committed (`35065fd`). 9 upgrades, 2 coord fixes:
- lakefront: 2768 Arnold Lake RA, 2825 Pibel Lake RA, 2845 Walnut Creek RA
- riverfront: 2885 Scenic Park (South Sioux City, Missouri R.)
- riverview: 2790 Cody Park (North Platte; coord-fixed to floodplain)
- lakeview: 2820 Neligh Park, 2835 Stanton Lake Park, 2862 Lakeshore RV Park (low)
- creekside: 2818 Mill Race Park/Atkinson (low)
- coord fix only: 2807 Holdrege (pin was on downtown tracks → stays not waterfront)

**Inclusion audit: done for the 139 NON-waterfront entries only** (ids in 2669-2887),
all 139 **keep, 0 removals** (committed `b3a54ae`). NE is heavily public — state
NGPC SRAs/WMAs/parks + many municipal/city-park campgrounds + private RV parks;
nothing failed inclusion. 2 low-confidence keeps (still real): 2675 Bowman Lake SRA,
2780 Bruning Dam RA.

**REMAINING: ~80 currently-waterfront NE entries still need inclusion** (same pattern
as [[project_in_sweep_handoff]] / [[project_wi_sweep_handoff]] — the user's "all
non-waterfront" request only covered non-wf entries). To finish NE inclusion, run
`audit/inclusion_audit_instructions.md` over the NE entries whose waterfront !=
"not waterfront" and that lack `inclusion_evidence`.

Method per [[reference_inclusion_audit.md]] / [[feedback_waterfront_evidence_in_json]];
ran agents one-at-a-time per [[feedback_sequential_sweep_agents]]. Both NE commits
not yet pushed as of handoff.
