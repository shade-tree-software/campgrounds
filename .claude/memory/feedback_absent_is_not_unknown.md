---
name: feedback-absent-is-not-unknown
description: Across this repo, a missing value must never collapse into a measured zero/false — the trap has now bitten four times in different subsystems
metadata:
  type: feedback
---

A missing value and a measured one must stay distinguishable. This has now gone wrong
**four times in four different subsystems**, which is why it is worth holding as a rule
rather than a per-case fix:

1. `process_rollups` read a day with no GPS as "0 miles" and wrote "the trip opened parked".
2. The same drafter's `trip_miles_by_day` rendered an unrecorded day as `0`, read as a pause.
3. `recgov_calendar.py` cached HTTP 429 failures as empty months and reported 19 of 30
   federal facilities as "no calendar data at all" — indistinguishable from the real thing,
   permanently.
4. The campground schema's whole design turns on it: `false` means somebody looked and
   there is none; a missing key means nobody looked.

**Why:** a default written once is indistinguishable from a verified fact, and at 12,768
entries that is unrecoverable. The failure is always silent and always looks plausible.

**How to apply:** never store a placeholder for "not determined" — omit the key. Never
cache a failed fetch as a result. In UI, a boolean needs three states, so a checkbox is
the wrong control. And in search, absent must never be grounds to EXCLUDE something —
a wrong value is visible on arrival, a silently missing row is invisible forever.
