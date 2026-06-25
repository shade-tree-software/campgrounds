---
name: reference_inclusion_audit
description: "Inclusion (validity) audit — verifies an entry is a real drive-in RV campground, separate from the waterfront audit"
metadata: 
  node_type: memory
  type: reference
  originSessionId: ef827276-a332-4f0b-940c-edb10b3a783c
---

The **inclusion audit** verifies each `campgrounds.json` entry is a real, currently-operating, drive-in RV campground fitting a 23-ft rig — catching cabins-only / tent-only / day-use-only / hike-in / group-only / membership / residential-seasonal / closed / under-23ft entries that slipped in during early less-rigorous passes. It is SEPARATE from the waterfront audit (which only checks the `waterfront` value + pin/elevation and does NOT re-vet validity). Built 2026-06-24 after Canoe Creek SP (a cabins-only PA park, "does not have a campground" per DCNR) was found in the DB.

- Instructions: `audit/inclusion_audit_instructions.md` (subagent gate). Apply: `audit/apply_inclusion_audit.py <results.json>`.
- Durable record: the **`inclusion_evidence`** JSON field (non-empty == validity-audited & confirmed keep), analogous to [[feedback_waterfront_evidence_in_json]]'s `waterfront_evidence`.
- Verdicts: `keep` (stamped with inclusion_evidence) / `remove` (reason category) / `review` (uncertain). The apply script stamps keeps and REPORTS removes/reviews — it never auto-deletes; a human reviews the remove list before excising (excise the `{ }` block by id; check `trip_data/` for `campground_id` refs first).
- KEY discipline: **operator/agency/reservation-system authority is primary; aggregators (snoflo, camperalerts, campscanner, thedyrt summaries, camping.org) routinely INFLATE cabin-only/day-use parks into "RV sites"** — never keep on an aggregator alone. For PA state parks: DCNR "Stay the Night" page + ReserveAmerica `campgroundDetails`/`campsiteDetails` (per-site type + Max Vehicle Length). For federal: recreation.gov per-site. Use satellite only as a cross-check.

**PA is the pilot — 100% inclusion-audited (2026-06-24).** Of 169 PA campgrounds, 11 removed: 5 cabins/day-use/tent-only state parks (Canoe Creek, Bendigo, Buchanan's Birthplace, Gouldsboro, Reeds Gap), 3 state-forest sites capping at 20ft (Carvolth, Forbes Laurel Mtn 002, Forbes Mt Davis 006), 1 hike-in (Weiser Halderman H4), 1 defunct/misattributed (E8 Bridge Camp), 1 unconfirmable FCFS (Patterson SP). 158 remain, all stamped. Note: the waterfront audit's ad-hoc DAYUSE-FLAG mis-flagged Little Buffalo SP (a real 43-site RV campground) — verification caught it; trust the operator authority, not a single agent's satellite read. Other states are NOT yet inclusion-audited.
