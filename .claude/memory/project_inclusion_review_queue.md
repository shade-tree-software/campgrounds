---
name: project_inclusion_review_queue
description: "11 inclusion-audit entries left as REVIEW (unverifiable while WebSearch was capped) — re-verify in a session with web search, then stamp inclusion_evidence or remove"
metadata: 
  node_type: memory
  type: project
  modified: 2026-07-21T20:34:24.375Z
  originSessionId: 5c74c92e-2dd0-4088-bf9b-1fed68986750
---

**Open task queue: 11 inclusion-audit "review" entries to finish off.**

During the MI/FL/AL inclusion backfill (2026-07-21) the session's WebSearch budget hit
its hard cap (200/200, `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`) partway through. The
rest of the audit ran WebFetch-primary + satellite, which handled ~everything because
those states' entries carry websites — EXCEPT these 11, which have dead/missing/JS-only
sites or approximate coords and could NOT be confirmed from an authoritative page without
a search. They are **NOT problems, just unconfirmed** — none were stamped and none were
removed. Their `inclusion_evidence` field is still empty/absent.

**How to finish (new machine, new session):** `git pull` first. Ensure WebSearch works
(fresh session resets the cap, or raise `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`). Then
run each through the normal inclusion check (`audit/inclusion_audit_instructions.md`): a
WebSearch for the operator/agency + the reservation-system per-site list decides
keep/remove/review. Apply keeps with `audit/apply_inclusion_audit.py` (stamps
`inclusion_evidence`); for any `remove`, check `trip_data/` for `campground_id` refs and
get owner approval before excising (and NEVER remove an `--AWH` entry without approval —
none of these 11 are `--AWH`). Small batch (one agent, ~11 ids) is fine.

**The 11 (id · state · name · why it's unconfirmed · what to check):**
- **4944 · AL · Sun Runners RV Park** (Gulf Shores, 30.3244,-87.6906, private) —
  official domain dead (DNS ENOTFOUND). Search for current operator/booking (Campspot/
  RoverPass) to confirm it still operates as a transient RV park.
- **4949 · AL · Chief Ladiga Trail Campground** (33.9159,-85.5041, private) —
  chiefladigacampground.com is a JS placeholder, Campspot slug is a generic shell.
  Confirm real drive-in RV sites via a working booking page/reviews.
- **4950 · AL · Mulberry Creek Camp** (34.7727,-87.8985, private) — no website in DB.
  Find the operator/reservation source; confirm drive-in RV sites currently operating.
- **4952 · AL · Lakeview RV Park** (Citronelle, 31.0648,-88.3152, **local**/City of
  Citronelle) — cityofcitronelle.com/recreation 403s WebFetch. Confirm the municipal RV
  park's overnight sites (try a cached copy / Google / phone the city).
- **4985 · AL · Rosemont RV Park** (31.3033,-85.3469, private) — rosemontrvpark.com dead,
  RoverPass 404, satellite ambiguous (could be mobile homes). Confirm it's a currently-
  operating transient RV park (lean-uncertain; may be a remove if defunct/residential).
- **167 · FL · Tiger Bay State Forest** (29.2075,-81.1776, state) — FDACS page says
  "semi-primitive campgrounds" + a Tram Road equestrian camp; no per-site ReserveAmerica
  listing found confirming drive-in RV-capable sites; satellite = flatwoods, no visible
  loop. Confirm whether any drive-in RV site exists (ReserveAmerica FL state forests) —
  else remove (tent/primitive or equestrian).
- **368 · FL · Fresh Gardens** (25.4747,-80.5068, hipcamp) — Hipcamp SPA won't render;
  satellite is a drivable Homestead ag parcel (sibling "Gate to the Keys" IS RV-confirmed).
  Load the Hipcamp listing (search) to confirm RVs are permitted.
- **4757 · FL · The Captain's Hideaway** (29.9015,-83.6294, private) — Facebook-only page;
  satellite shows a rural-residential subdivision, can't isolate the 4-site RV area.
  Confirm it operates as a bookable transient RV site (tiny — may be a remove).
- **3801 · MI · Langford Lake Campground** (46.27282,-89.49243, federal/Ottawa NF) —
  **likely a REMOVE**: current Ottawa NF camping list omits it, rec.gov shows only
  "Langford Lake Boat Launch" (no campground), note flags a 2019 closure. Verify it was
  decommissioned to a boat launch → remove if so.
- **3834 · MI · Highway to Haven Family Campground** (43.04540,-86.21300, private) —
  **likely a REMOVE or mis-pin**: h2hcamp.com dead (no DNS), satellite at the pin is
  urban/commercial dev with no campground, only a thin Facebook page. Confirm closed/
  redeveloped (remove) or find the correct location.
- **3967 · MI · Isabella County Fairgrounds Campground** (43.64473,-84.76459, local) —
  fairgrounds site DNS-unreachable; county Parks&Rec lists only its 3 other parks;
  satellite shows grass camping lanes. Confirm whether it offers general public camping
  outside fair week (keep) vs event-only (remove).

Process refs: [[reference_inclusion_audit]], sequential agents
[[feedback_sequential_sweep_agents]]. Related state handoffs:
[[project_al_sweep_handoff]], [[project_fl_sweep_handoff]],
[[project_mi_local_stage_handoff]].
