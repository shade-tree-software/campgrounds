---
name: feedback-mandatory-fees-count
description: Mandatory per-person entry/day/grounds fees count toward a private campground's base nightly rate for the $50 price gate
metadata:
  type: feedback
---

A fee every guest must pay to be on the property (resort day fee, grounds fee, per-person admission) is part of the nightly price for the private price gate, not an excludable "fee" like a reservation charge. Avalon Resort (Paw Paw WV, clothing-optional): RV site $30 + mandatory day fee $50/couple = ~$80 -> skipped (AWH 2026-09-30: "The Avalon entry fee is a deal-breaker").

**Why:** the gate asks what two adults actually pay to stay a night; a cheap site behind a mandatory admission charge is not a cheap night.

**How to apply:** base rate = cheapest hookup site at 2 adults + any mandatory per-person/per-day charge for 2 adults. Still excluded: reservation/booking fees, tax, optional extras, charges for people beyond base occupancy. Also: Avalon was added as 14262 then removed - when the removed entry was the highest id, run the next append_state.py with --min-id above it so the retired id is never reissued (next free: 14263). Related: [[project_private_gap]].
