---
name: feedback-minimum-stay
description: "A standing (every-stay, not weekend-only) minimum of 2+ nights disqualifies a campground; weekend/holiday minimums are fine (AWH 2026-10-01, tightened from 4 nights)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 96da6df7-9a3e-4409-adaa-c37da68ef643
  modified: 2026-10-01T13:18:33.878Z
---

A campground whose minimum stay applies to EVERY stay is not a nightly campground and is skipped. **AWH 2026-10-01: a standing 2-night minimum disqualifies** ("a campground does not qualify if it has a standing 2-night minimum. Weekend is ok."). This tightened the 2026-09-30 rule, which drew the line at 4 nights (American Way RV Park, Mineral Wells WV: "$50 daily, 4 day minimum").

**Why:** EKKO trips move most days; a park that won't sell one night is a weekly/monthly park wearing a daily rate.

**How to apply:**
- Skip with kind_of_no "not nightly (N-night minimum)" when the minimum applies to all stays (Sparkman Lake OH, "two night minimum at all times", skipped 2026-10-01 though it passed at $40).
- Weekend 2-night and holiday 3-4-night minimums are normal and do NOT disqualify (River Ridge).
- A "2-night minimum except events" is a standing minimum, so it now FAILS (Groves, 14240, was passed under the old rule).
- A booking engine often shows the minimum when the operator's page doesn't; ask AWH about any hold settled from a ResNexus read.
- **Applies retroactively to ALL existing entries** (AWH 2026-10-01).
- **A minimum that can be got around for one night is NOT standing**: a late-booking waiver (OH/IN/VT "within N days"), a phone single night, walk-up/FCFS sites. SC state parks publish a year-round 2-night minimum, but AWH has booked single nights "multiple times at SC by calling the campground within a week of arrival" (trips 24/56/88), so all SC state parks stay; MA likewise (trip 16 booked two single nights at Harold Parker despite DCR's "2-day minimum"). The written agency policy is not the test; whether a single night is actually sold is. AWH confirmed 2026-10-01: "a minimum that applies online but can be waived by phone is fine" (Van Hook AR, Bay Ridge MI kept).

- **Canada no_rate follow-up examples (2026-10-08):** same-day single-night products are waivers, not standing minimums - Camping Union's "Nuitée Express" (bought after 16:00, out by 09:00), Lac-aux-Sables "one night accepted same day only", Camping du Parc "one night by phone 48 h ahead". Standing minimums found only by working the engine: Wigwam (every site on a July 2027 Tuesday said "minimum de 2 nuitées" on its reservationcamping.ca site page), Péninsule (engine nights list generated from 2), Coolbreeze ("2 nuits minimum en tout temps" on its rate page). Check per site/type, not the form's first select ([[reference-hidden-rates-playbook]]).

Related: [[feedback_exclude_seasonal_residential]].
