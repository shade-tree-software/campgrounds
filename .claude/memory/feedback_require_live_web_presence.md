---
name: feedback_require_live_web_presence
description: A campground with no live website AND no active bookable platform listing is excluded outright — not merely suspect
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45b0468a-4e5a-44b8-8a3e-d4e7d1bd4542
  modified: 2026-09-08T13:50:57.319Z
---

AWH 2026-09-08: a campground must have at least one **live** web presence — a working official site with photos, current prices and a phone number, OR an active bookable platform listing (Hipcamp `isBookable`, recreation.gov / ReserveAmerica / US-eDirect, Campspot, a *claimed* RoverPass listing). One with neither is excluded, even when reviews prove it is operating and well-liked. This hardened the old "dead website is a strike" guidance into a disqualifier. Removed on the spot: Lee Hi Travel Plaza (VA, was id 13096), Interstate Campground (VA, was 13097), Montrose Campground (PA, was 13115).

**Why (AWH's words):** "Campgrounds that have no active website and no active hipcamp are a hassle I don't need. A HipCamp listing or a simple website with photos, current prices, and an active phone number are not difficult to maintain if you are running a serious business." The entry exists to be *planned around*; if you can't see prices or reach anyone, it fails at that regardless of how nice the place is.

**How to apply — judge the presence LIVE, not merely existing:**
- Fetch the domain. A 404, or a 301 to an unrelated business, is dead (leehi.com → 404; montrosecampground.net → etceteradecor.com).
- A Hipcamp listing at `status: "ASLEEP"` / `isBookable: false` is dormant, not a channel — check the page HTML for both fields, don't assume a listing URL means bookable.
- An **unclaimed** aggregator listing is a directory record a third party wrote, not the operator's presence. Tells: a "Claim my Campground" button, a stale "Last Updated", and auto-generated filler (Lee Hi's RoverPass page named Colonial Williamsburg and Busch Gardens, ~3 hrs from Lexington, as nearby attractions).
- A Facebook page alone is weak — accept it only if it is actually current and carries prices/contact.
- This bites hardest in the **private** stage of a sweep, where phone-only mom-and-pop parks with expired domains are common. Apply it at add time so the entry never lands.

See also [[feedback_note_rate_sourcing]], [[feedback_campground_vetting_discipline]], [[feedback_urls_in_website_not_notes]].
