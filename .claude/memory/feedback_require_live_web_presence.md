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

**Scope (AWH 2026-09-08):** applies to `private` entries. Public land is exempt — "it's common for those to have minimal online presence, especially if FCFS." A *free, no-fee FCFS* private dry camp (Chiriaco Summit CA) sits in the same logic: there is nothing to book and no rate to publish, so the rule's premise doesn't hold. Flag those rather than auto-removing.

**Why (AWH's words):** "Campgrounds that have no active website and no active hipcamp are a hassle I don't need. A HipCamp listing or a simple website with photos, current prices, and an active phone number are not difficult to maintain if you are running a serious business." The entry exists to be *planned around*; if you can't see prices or reach anyone, it fails at that regardless of how nice the place is.

**How to apply — judge the presence LIVE, not merely existing:**
- Fetch the domain. A 404, or a 301 to an unrelated business, is dead (leehi.com → 404; montrosecampground.net → etceteradecor.com).
- A Hipcamp listing at `status: "ASLEEP"` / `isBookable: false` is dormant, not a channel — check the page HTML for both fields, don't assume a listing URL means bookable.
- An **unclaimed** aggregator listing is a directory record a third party wrote, not the operator's presence. Tells: a "Claim my Campground" button, a stale "Last Updated", and auto-generated filler (Lee Hi's RoverPass page named Colonial Williamsburg and Busch Gardens, ~3 hrs from Lexington, as nearby attractions).
- A Facebook page alone is weak — accept it only if it is actually current and carries prices/contact.
- This bites hardest in the **private** stage of a sweep, where phone-only mom-and-pop parks with expired domains are common. Apply it at add time so the entry never lands.

**How to audit a whole state/ownership slice for this (method proven on 178 private entries, 2026-09-08 — 119 removed, 20 rescued):** four independent signals, cheap and deterministic, no per-entry research until the end.
1. **RV Life park pages carry the operator URL** in embedded JSON as `cg_url` (the Algolia `park` index does NOT expose it — fetch the park page). Values are JSON-escaped: unescape `\/` → `/` before probing, or every request dies as "no host given".
2. **Probe every URL** (ours + RV Life's), follow redirects, then **retry failures with browser headers** — a first-pass 403 or TLS timeout is usually blocking, not death. Facebook returns HTTP 400 to any non-browser client; never read that as a dead page.
3. **Hipcamp's sitemap is the bookability oracle**: `robots.txt` → `sitemaps/v2/main.xml.gz` → per-state `us-lands-XX.xml.gz` / `ca-lands-XX.xml.gz`. It lists only live/bookable lands, so a listing that is `status: ASLEEP` / `isBookable: false` is *correctly* absent — the sitemap's own criterion matches this rule exactly. **Campspot has the equivalent** at `campspot.com/about/documents/park-sitemap.xml` (~3,100 parks); checking Hipcamp alone misses parks that book through Campspot.
4. **Good Sam's Algolia record carries `campground.urls.campground`** — an independent second source for an operator site (see [[reference_good_sam_ratings]] for the key). Query per candidate with a `campground.address.stateCode` filter; a state-wide pull silently truncates at Algolia's 1,000-result cap.

**Always verify a name match by coordinate (<8 km).** Campground names repeat relentlessly and fuzzy matching is worthless without it: "Pioneer RV Park" matched a park 600 km away, "Junction RV Park" one 120 km away, and 8 of 11 Hipcamp name-matches and 14 of 15 Campspot ones were different properties. Also guard the empty-string case — a normalizer that strips generic words turns "A & A Park" into `""`, which then substring-matches everything.

**Four probe traps that produce FALSE deaths — every one of these bit on a real entry:**
- **A host-changing redirect is ambiguous.** It can be a *domain migration* (Old Shipyard Beach → oldshipyardcampground.com; 829 RV Park → its operator's SteadyStays page — both live businesses) or a *resale* (Pioneer RV Park Guthrie → a Montreal sauce company). Open it and read the page; never auto-classify.
- **www vs apex differ.** Try both hosts and both schemes before calling a domain dead.
- **A 403 or TLS timeout is usually blocking, not death** — retry with full browser headers. (Persistent ones are still real: Young's RV Park never completes a handshake.)
- **An empty `<title>` is not junk.** Judge by body content — riversideacres.com really is an ad shell, but the title told you nothing.
Two dead-by-construction classes worth knowing: **Google `business.site`** domains were shut down in 2024 and all 404 (Cat Creek CO), and a **parent/chain operator page counts as the operator's presence** (Pine Cliff Resort hosts Valley Breeze KY and Rest Rite WV; SteadyStays and rjourney run several parks each).

**A live URL is not enough — classify what it IS.** Sort into operator/parent site, booking platform, third-party directory, and junk. Tourism directories (travelok, go-utah, bonjourquebec, state tourism sites), a Camping World *dealer* page, an expired domain reselling as a video site, and a NameBright parking page all return HTTP 200.

**Two gotchas when writing results back to `campgrounds.json`:** apply website backfills **additively** (an entry may already hold several newline-separated URLs — replacing the value drops them), and never build the replacement with `re.sub`'s template, which interprets the `\n` inside a JSON string as a real newline and corrupts the file. Use a lambda replacement. Strip `utm_*` params off URLs that came from a directory.

See also [[feedback_note_rate_sourcing]], [[feedback_campground_vetting_discipline]], [[feedback_urls_in_website_not_notes]], [[reference_good_sam_ratings]], [[reference_rvlife_price]].
