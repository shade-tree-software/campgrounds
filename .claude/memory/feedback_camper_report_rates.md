---
name: feedback-camper-report-rates
description: "AWH 2026-10-11: a camper's dated report (2024 or later) may price an entry only when the operator has no web page at all, and the note must say so with a CAMPER-REPORTED RATE line; not for 'call for rates' pages"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 697b5c76-5652-4131-bd7c-1761a58eb19c
  modified: 2026-10-11T22:06:57.247Z
---

**Rule (AWH 2026-10-11):** "You can use a camper's dated report (2024 or later) to price an entry when the operator has no web page at all, but be sure to indicate it in the note."

**Why:** the operator is the authority on its own rate ([[feedback_note_rate_sourcing]]). A camper's report is the fallback only when there is nothing official to read. I had asked whether to extend it to operator pages that say "call for rates". AWH answered by restating the no-web-page limit, so a page that exists but posts no rate does NOT open the camper route.

**How to apply:**
- Only use a review that carries a date (a Campendium or RV Life stay or review date, or a dated Dyrt review), and only 2024 or later. Undated "$X / night" badges never count, nor do directory "from" prices.
- "No web page at all" means no page from the operator about the campground. A tourism or directory listing (Explore Georgia, VisitNebraska, CamplinQ, RoverPass) is not the operator's page. A Facebook-only park was treated as having no web page (Kinser 13390, Kona Beach 14945).
- Append a dated line to the note: `CAMPER-REPORTED RATE: $X a night in <Month YYYY> (<site> review); the park has no web page (YYYY-MM-DD). --Claude`. Then re-stamp note_scan with `extract_fields.py --apply-file` and empty proposals.
- The fees note and the `provenance.fees.source` name the review and its date as well.
- A price resting on an older report (Wessington Springs 13553, June 2023) was turned back into a note-derived price instead of being kept as sourced.

Related: [[project_price_research]], [[feedback-missing-rate-is-unresearched]].
