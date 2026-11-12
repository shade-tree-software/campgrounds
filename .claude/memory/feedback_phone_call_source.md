---
name: feedback-phone-call-source
description: "AWH 2026-11-11 - a phone answer from the operator is a valid curation source; dialmcp place_call available, but each call waits for AWH's go-ahead"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d4b55933-c695-4ba4-bcb2-b8423ed39732
  modified: 2026-11-12T01:22:18.131Z
---

AWH 2026-11-11: "a phone answer [is] a valid source." A call to the operator's published number
counts as operator-sourced for rate, season, site length, nightly-guest policy etc. Record it as a
dated phone call (e.g. `p3-N (YYYY-MM-DD): phone call to <number>: ... --Claude`) in
`curation_note`; field values go in with that as their source.

**Why:** several MN city campgrounds (Karlstad, Sherin, Warroad, Wildcat, J.F. Jacobson Park) refuse
web fetches, so the [[project-phase7-verification]] unread sweep can't otherwise read them.

**How to apply:** calls go through the dialmcp `place_call` tool, which dials FROM AWH's own number
with an AI agent that discloses itself and the recording; US/CA only, 08:00-21:00 destination local
time. AWH said 2026-11-11 to wait until they say when to try the FIRST call (planned: Karlstad,
5649), and confirm each call with AWH before dialling. Offer AWH the listen_url.
