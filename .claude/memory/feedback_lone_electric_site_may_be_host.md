---
name: feedback-lone-electric-site-may-be-host
description: "A campground whose only electric site (or two) can't be booked may just be showing the camp host's pad — never read it as public electric"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 95575d5f-3916-412c-94a2-a511a600ed77
  modified: 2026-09-18T15:36:57.791Z
---

A campground with a single electric site may have that site reserved for the
camp host, never available to the public (AWH 2026-09-18, after the RIDB hookups
pass wrote electric for campgrounds with one electric site).

**Why:** the map's Hookups filter would then show a campground as "has electric"
when a family can never plug in there — a wrong yes is visible only on arrival.

**How to apply:** in any derivation of hookups from per-site data (RIDB, a
booking engine, a site map):
- drop sites NAMED host outright (Boise Creek's only electric site is a
  STANDARD ELECTRIC called "Host" — RIDB doesn't always type them MANAGEMENT);
- when there are only 1-2 electric sites, count them only if the public can
  book them (RIDB `CampsiteReservable: true`); otherwise electric is UNKNOWN,
  not 0 — the site exists, we just can't tell whose it is.
- the same caution applies to reading prose: "one electric site" in a note is
  not evidence of public electric.

`recgov_hookups.py` implements this (`FEW_ELECTRIC_SITES`, `HOST_NAME`).
Related: [[project-campground-schema]], [[feedback-absent-is-not-unknown]].
