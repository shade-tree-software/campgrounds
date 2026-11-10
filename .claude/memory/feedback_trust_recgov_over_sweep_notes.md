---
name: feedback-trust-recgov-over-sweep-notes
description: "Current recreation.gov/RIDB outranks sweep notes AND the home agency's own web page (FS/NPS/BLM) when they disagree (AWH 2026-11-08); within rec.gov the live selling calendar beats its notice text"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 95575d5f-3916-412c-94a2-a511a600ed77
  modified: 2026-09-18T19:50:48.909Z
---

When recreation.gov (RIDB catalog, availability calendar) disagrees with a
campground note, **trust current rec.gov** (AWH 2026-09-18: "I would trust current
rec.gov over older auto-generated notes with unknown source").

**Why:** nearly all notes were auto-generated during the state sweeps from
unrecorded sources, so a disagreement with the booking system's own per-site
record has no good explanation on the note's side. AWH has never been to most of
these campgrounds and cannot adjudicate a conflicts list — don't hand him one.

**How to apply:**
- Machine-derived values (`provenance.method: derived`, e.g. `source: note prose`)
  are replaceable by the catalog; record the change and list it, don't queue it
  for his review.
- A value a PERSON checked (`manual` / `reported`) still outranks the catalog.
- Notes signed `--AWH` are his own first-hand words, not sweep output — that is
  the exception worth flagging rather than overriding silently.
- The note prose itself stays unedited (schema doc §6) unless he asks.

**Extended 2026-11-08 (AWH):** rec.gov also outranks the campground's HOME AGENCY page
(Forest Service, NPS, BLM, USACE) when they conflict: "they are the ones who are actively
selling sites and are therefore more likely to be up to date than an infrequently-maintained
forest service or national park web page."
- Within rec.gov, what it actually SELLS (the live availability calendar) beats its own
  notice/rules text: Water Canyon 8037's calendar sells Mar 15-Nov 30 though a notice says
  first-come Oct-Mar; Little Coon Creek 5210 sells April nights though its rules say "Not
  Reservable".
- Not a conflict: `season` (open) vs the calendar span (reservations). An agency season
  WIDER than the calendar is the first-come shoulder, not a disagreement (season pass rule).

`recgov_hookups.py` implements this for hookups. Related:
[[project-campground-schema]], [[feedback-lone-electric-site-may-be-host]].

**Exception, AWH 2026-11-10 (Watercress 1916):** "rec.gov might not maintain accurate listings about campgrounds that are FCFS only. In that case, default to trusting the forest service page." So rec.gov outranks the agency page only where rec.gov actually sells the sites.
