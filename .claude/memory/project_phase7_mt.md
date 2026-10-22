---
name: project-phase7-mt
description: Phase 7 MONTANA run in a cloud session (2026-10-22), parallel to the main phase-7 session; batches mt-N on branch claude/youthful-ramanujan-3k9rmh
metadata:
  type: project
---

AWH 2026-10-22: a second (cloud) session works phase 7 on MONTANA only, beside the main session
([[project-phase7-verification]]), to spend expiring credits. Batches are named `mt-N` (never
p3-N) and come from `queue.py --state MT`. One verifier at a time in this session.

**Conflict rules:** MT notes in waterfront_leads.md / criteria_followups.md go in a
"## Montana (mt-N batches)" section near the TOP (the main session appends at the end), so
merges don't collide. removals.json will conflict on merge: keep both sides.

**Cloud-checkout gaps:** trip_data/trips.json is an empty placeholder (gitignored, family data
not here), but AWH 2026-10-22: "We have never stayed anywhere in Montana", so standing-rule drops
(presence, 4WD/motorhome-not-recommended, price gate with no gateway) go straight into
criteria_drops.py (MT block at the TOP of DROPS) and are reported. No RIDB key: helper catx.py reads rec.gov's
public search API for the per-site catalog. No PA deploy from here.

**Progress:** mt-1..mt-4 applied (mt-5 running). Dropped so far: 6166 B&L (presence), 6227 Grizzly (motorhomes not recommended), 6155 Riverside (no posted RV rate), 6168 Sand Springs (dead site). bw.py here must point at /opt/pw-browsers/chromium-1194 (pip playwright wants a newer build); USACE nws.usace.army.mil pages 403 from the cloud.
