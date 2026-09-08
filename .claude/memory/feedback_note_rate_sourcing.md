---
name: feedback_note_rate_sourcing
description: Nightly-rate figures in a campground note must name their source and date; unclaimed aggregator rate tables go stale and falsely corroborate each other
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45b0468a-4e5a-44b8-8a3e-d4e7d1bd4542
  modified: 2026-09-08T13:40:09.426Z
---

A `$NN/night` figure in a `note` needs the same sourcing discipline as every other claim: it must come from the operator's own rate page or booking channel, and if it can't, the note must say what the source was and when it was current. AWH caught Gooney Creek Campground (VA, id 13085, 2026-09-08) listing "Rates around $20 basic / $25 W+E / $28 full hookup" against a HipCamp listing whose real prices were $38.50 tent / $48.50 E+W / $53.50 creek-side E+W / $63.50 full hookup — roughly 40% of actual, and unattributed.

**Why:** rates are the claim a reader acts on when choosing between parks, and a stale one is worse than none. The private stage of a sweep quotes rates constantly, so the failure mode is systematic rather than one-off — a re-scan of the same sweep found three more entries (13096/13097/13115) whose rates rested on directories alone.

**How to apply:**
- **The booking channel is the authority.** A HipCamp `land` page's SSR HTML carries the operator's exact per-site-type inventory — fetch it with `urllib` (send a browser UA + `Accept-Encoding: gzip`) and regex out `"campgroundName"` paired with `pricePerNight` (base) and `totalPricePerNight` (with HipCamp's ~18% service fee), plus `campsitesCount` / `rvMaxLength` / `accommodationType`. Same trick fills in the site mix exactly. This also works as *waterfront and inclusion* evidence — it's the same payload those fields already cite.
- **Beware false corroboration.** Two directories agreeing does not make two sources. Montrose's "$28-34" appeared on both RoverPass and The Dyrt because both render the same unclaimed listing, last updated 11/2024. Check RoverPass for "Claim my Campground" (= unclaimed) and its "Last Updated" date before trusting a rate table.
- **Auto-generated filler is the tell.** Lee Hi's RoverPass listing named Colonial Williamsburg and Busch Gardens — ~3 hrs from Lexington — as nearby attractions. A listing that invents geography is not a booking channel; don't let one sit in `website` presented as one.
- **Dated firsthand reports are an acceptable fallback** when no operator page exists (many phone-only parks with dead domains). Campendium is the best source for these: its listing header carries "Last Nightly Rate $NN Reported MM/DD/YY" and each review carries its own nightly rate + date. Quote the figure **with its date**, and don't average across years — Lee Hi's "$35-43" range was silently mixing 2019 reports with 2026 ones.
- When even that is missing, say so ("no operator rate page exists... confirm by phone") and give the RV Life directory average as an explicitly-labelled estimate rather than a bare number.

See also [[feedback_campground_vetting_discipline]], [[feedback_urls_in_website_not_notes]], [[feedback_attribute_note_edits]], [[project_pre_playbook_private_gap]].
