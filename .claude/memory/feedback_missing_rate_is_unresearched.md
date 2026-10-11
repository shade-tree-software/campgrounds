---
name: feedback-missing-rate-is-unresearched
description: A rate-less entry usually means the sweep never dug for the rate, not that none is published - follow the booking engine before recording "no rate posted" or bringing a drop to AWH
metadata:
  type: feedback
---

AWH 2026-10-11: "many of the campgrounds in our database that had no rates were in that state because the original sweep that added the campground wasn't very thorough about trying to look for rates. When we've looked deeper, especially examining booking sites, we've found the rates that were probably there all along."

The data agrees. In price research #2 (2026-10-09..11), about 2,600 entries with no RV Life tier got a nightly rate:
- 1,359 from the operator's or agency's own pages;
- 764 straight off a booking engine;
- 302 free sites read as $0 from the note;
- 106 from our own sweep note;
- 65 from pages AWH read.

The residue held the same lesson. The 126 public entries filed as "operator pages read, no rate posted, only a phone call will price them" had been read for `$` lines only. One static fetch found a booking-engine link on 24 of the 108 with a website, and 27 more had refused the earlier non-browser fetch. Leads: `audit/price_research/public_engine_leads_2026-10-11.json`.

**Why:** the sweeps read the operator page for a rate and moved on. Booking engines show prices only after a date (sometimes a rig size) is picked, so a `$`-line read, static or rendered, never sees them. "No rate found" recorded the depth of the look, not a fact about the campground.

**How to apply:**
- Treat a missing rate as unresearched. Before writing "no rate posted", filing an entry as phone-call-only, or bringing a rate-less entry to AWH as a drop, open every Reserve/Book link on the operator page and quote a date in the engine. `scan.py` lists the engine hosts; recipes are in `audit/private_gap_browser/README.md` ([[reference-hidden-rates-playbook]]).
- A non-browser fetch that failed has not looked at the page: retry it in the one browser.
- Captcha engines (ResNexus, Firefly, Itinio) are still never automated: ask AWH to save the page.
- At add time, take the rate from the booking channel and record it then.

Related: [[project_price_research]], [[feedback_require_live_web_presence]], [[feedback_note_rate_sourcing]].
