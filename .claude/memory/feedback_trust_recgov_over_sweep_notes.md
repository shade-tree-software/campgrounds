---
name: feedback-trust-recgov-over-sweep-notes
description: "Current recreation.gov/RIDB data outranks the auto-generated sweep notes when they disagree — AWH hasn't visited those campgrounds and can't adjudicate"
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

`recgov_hookups.py` implements this for hookups. Related:
[[project-campground-schema]], [[feedback-lone-electric-site-may-be-host]].
