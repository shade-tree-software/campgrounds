---
name: project_mi_local_stage_handoff
description: "Michigan campground sweep COMPLETE — all buckets added+waterfront+inclusion; the old 'local pending' note was stale (2026-07-21)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 000f3a09-478e-409e-a145-36cc569bc967
  modified: 2026-07-21T19:56:01.512Z
---

**UPDATE 2026-07-21 — MICHIGAN IS FULLY COMPLETE.** The 2026-06-15 notes below are
STALE: the local bucket WAS completed in a later session (the DB now has 135 MI local
entries, ids 3911–4050, all waterfront-audited). All four buckets are done + waterfront
100%. The **inclusion backfill** was run 2026-07-21 (50 sequential batches, WebFetch-
primary since WebSearch was capped; Michigan.gov 403s WebFetch so state parks/SFCGs
leaned on midnrreservations + rec.gov + satellite + firsthand --AWH notes): **496/499
stamped, 0 removes, 3 reviews HELD** (not excised, pending re-verify when search resets):
3801 Langford Lake (Ottawa NF page omits it, rec.gov lists only a boat launch, note
flags 2019 closure), 3834 Highway to Haven (dead site, satellite shows urban dev),
3967 Isabella County Fairgrounds (can't rule out event-only). Nothing else outstanding.
Everything below is historical.

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
