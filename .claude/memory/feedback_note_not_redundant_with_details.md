---
name: feedback_note_not_redundant_with_details
description: AWH 2026-10-21 - a campground note shouldn't repeat what the structured details (booking/fees/season/hookups/rating chips) already show; I may trim notes to remove it
metadata:
  type: feedback
---

AWH 2026-10-21: "When updating campground information, there is no need to put information in the
note if it is reported in the campground details ... You may edit notes as necessary to remove
redundant information." Example: Hone Quarry (484) had "FCFS only - pay on-site, not bookable in
advance" and "RV Life 4*/$ (auto 6/2026)" in the note while the popup already showed "not
reservable · FCFS" and the rating chip; the note was cut to AWH's own line.

**Why:** the popup draws the structured fields (docs/campground-schema.md) as rows right under the
note, so a note restating them is the same fact twice.

**How to apply:** when I or a verifier touch an entry, drop note text that only restates a
structured value the entry carries (booking/FCFS, fees, season, hookups, site counts/lengths,
discounts, RV Life rating lines). Keep what the details can't say (where the good sites are, the
caveats, why). --AWH text stays verbatim ([[feedback_clean_up_notes]]) unless AWH says otherwise.
Phase 7 verifiers get it via audit/verify/README.md step 7 ([[project_phase7_verification]]).
752 notes still carry an "RV Life N*/$" line duplicating the rating chip - a bulk trim was offered,
not done.
