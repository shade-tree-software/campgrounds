---
name: project_inclusion_review_queue
description: "CLOSED 2026-07-21 — the 11 held inclusion-audit 'review' entries were all resolved: 8 keeps stamped, 3 closed campgrounds removed"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1ef9304d-92d4-4988-a48d-f91c76aef59f
  modified: 2026-07-21T20:47:02.601Z
---

**DONE — this queue is empty. No open task here.**

The 11 inclusion entries left as `review` during the MI/FL/AL backfill (held because
that session's WebSearch budget was capped) were finished on **2026-07-21** with web
search available. Commits `7de288a` (keeps) and `8ae3847` (removes).

**8 keeps** — `inclusion_evidence` stamped: 4944 Sun Runners RV Park (AL), 4950
Mulberry Creek Camp (AL), 4952 Lakeview RV Park Citronelle (AL), 4985 Rosemont RV
Park (AL), 167 Tiger Bay State Forest (FL — ReserveAmerica Bennett Field: 5 "RV or
Tent" sites, 30 ft max; deep booking link added), 368 Fresh Gardens (FL — Hipcamp
"Freshgardens Everglades (RV only)"), 3834 Highway to Haven (MI), 3967 Isabella
County Fairgrounds (MI — county page: FCFS outside fair week, so NOT event-only).

**3 removes** (owner-approved; no `trip_data` references): 4949 Chief Ladiga Trail
Campground (closed, owner health), 4757 The Captain's Hideaway (owner site: hoping
to reopen in a *new* location), 3801 Langford Lake (USFS: "Campground has been
permanently closed. The boat ramp is open").

**Two lessons worth carrying forward:**
1. A dead domain in the `website` field is not proof of closure — 3834's
   `h2hcamp.com` was dead but the campground had simply moved to
   `highwaytohavencampground.com` and is operating. Search the *name*, not just the
   stored URL.
2. 3834 was also mis-pinned ~700 m into urban Grand Haven; the real campground is
   west of US-31 off Robbins Rd (re-pinned to 43.0413,-86.2214, elev 186 m).
   A satellite look that shows no campground means check the pin before concluding
   the place is gone.

Process refs: [[reference_inclusion_audit]], [[project_al_sweep_handoff]],
[[project_fl_sweep_handoff]], [[project_mi_local_stage_handoff]].
