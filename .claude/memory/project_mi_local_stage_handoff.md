---
name: project_mi_local_stage_handoff
description: "Where the Michigan campground curation stands and what the local stage still needs (handoff across machines, 2026-06-15)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 000f3a09-478e-409e-a145-36cc569bc967
---

Michigan curation as of 2026-06-15: state, federal, and private sweeps are DONE and committed (all pushed). Remaining: the **local** stage, which is the last MI category.

Committed so far (git log is the authority — grep these):
- "Add 64 MI federal campgrounds (Manistee/Huron/Hiawatha/Ottawa NFs) + 3 SFCGs" + its waterfront audit
- "Add 105 MI private campgrounds (commercial sweep) + 1 federal" + "Audit all 106 MI private/federal waterfront designations"
- "Add 16 MI local campgrounds reclassified from the private sweep" (ids 3911-3926) — these locals are written with placeholder `waterfront: "not waterfront"` and are **NOT yet waterfront-audited**. Their per-entry water-body leads are in that commit message.

MI local stage TODO (continue here):
1. **Waterfront-audit the 16 already-added reclassified locals** (ids 3911-3926) using `audit/waterfront_audit_instructions.md` + `audit/apply_waterfront_audit.py`. Leads are in the "Add 16 MI local..." commit body (e.g. North Park=Lake Huron, Gladstone Bay=Little Bay de Noc, Scottville=Pere Marquette R, Old Orchard=Foote Pond). Several are strong on-water/coastal candidates.
2. **Full MI local RV Life sweep** not yet done: pull `park_type` in {county, city, regional} for MI (RV Life Algolia app H0LPZK92QJ, index `park`, key inline in any park-page HTML), PLUS a gov-keyword name-scan of the commercial bucket for county/township/municipal/regional/borough mislabels. `park_type == dnr` is STATE (already swept), not local. Do NOT apply the ≥4★/≤$$ gate to local — include any confirmed local-government drive-in RV campground, record the RV Life star/price in the note. See [[reference_local_campground_method]].
3. Dedupe new local finds against the DB (the 16 above are already in, so the sweep's existing-DB dedup will skip them). Add, then waterfront-audit (fold the audit into the sweep per the standard), then commit.

MI campground counts after the local-reclass commit: ~359 campgrounds (179 state, 72 federal, 105 private, 19 local). The repo is a solo data repo; commit to master, user pushes.
