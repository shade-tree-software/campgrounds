---
name: feedback-minimum-stay
description: "A standing (every-stay, not weekend-only) minimum of 2+ nights disqualifies a campground; weekend/holiday minimums are fine (AWH 2026-10-01, tightened from 4 nights)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 96da6df7-9a3e-4409-adaa-c37da68ef643
  modified: 2026-10-01T13:00:59.850Z
---

A campground whose minimum stay applies to EVERY stay is not a nightly campground and is skipped. **AWH 2026-10-01: a standing 2-night minimum disqualifies** ("a campground does not qualify if it has a standing 2-night minimum. Weekend is ok."). This tightened the 2026-09-30 rule, which drew the line at 4 nights (American Way RV Park, Mineral Wells WV: "$50 daily, 4 day minimum").

**Why:** EKKO trips move most days; a park that won't sell one night is a weekly/monthly park wearing a daily rate.

**How to apply:**
- Skip with kind_of_no "not nightly (N-night minimum)" when the minimum applies to all stays (Sparkman Lake OH, "two night minimum at all times", skipped 2026-10-01 though it passed at $40).
- Weekend 2-night and holiday 3-4-night minimums are normal and do NOT disqualify (River Ridge).
- A "2-night minimum except events" is a standing minimum, so it now FAILS (Groves, 14240, was passed under the old rule).
- A booking engine often shows the minimum when the operator's page doesn't; ask AWH about any hold settled from a ResNexus read.
- **Retroactive scope is AWH's call, not settled yet** (asked 2026-10-01): ~45 existing entries carry a standing 2-3 night minimum in their notes, including every SC state park (online-reservation minimum), the Go Camp Tennessee TVA campgrounds, and several county parks. Many of those are reservation-only minimums with walk-up/phone single nights; distinguish those before removing anything.

Related: [[feedback_exclude_seasonal_residential]].
