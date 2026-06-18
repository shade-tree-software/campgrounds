---
name: feedback_urls_in_website_not_notes
description: "Campground website/reservation URLs go in the website field, not in note prose"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f0f241c6-6ec0-4e4c-a2e2-5487197fe8e7
---

Keep website URLs out of campground `note` text — the reservation/official site belongs in the `website` field (newline-separated if several, deduped by domain). Write "Reservable online" instead of "Reservable via recreation.gov".

**Why:** the user wants the website field to be the single home for URLs; notes carrying reservation links is clutter and duplication (most already had the portal in `website`).

**How to apply:**
- Positive "Reserve/Reservable/Booked via <portal>" → reword to "...online" and ensure the URL is in `website` (recreation.gov, camp.in.gov, reserveamerica, state/agency portals, the campground's own domain).
- Keep as prose (do NOT move): negative reservation facts ("FCFS -- not on recreation.gov", "book via Campspot, not recreation.gov") and a dead/suspect official domain noted as a caveat.
- Source citations (a blog/listicle/video the pick came from, e.g. campingprepper.com, a youtube link) are attributions, not the campground's site -- don't put them in `website`; de-URL to a bare name if practical.
- Avoid global whitespace munging when editing notes -- the DB uses a two-space house style between sentences; only touch the URL phrasing.

See also [[feedback_attribute_note_edits]], [[feedback_campground_vetting_discipline]].
