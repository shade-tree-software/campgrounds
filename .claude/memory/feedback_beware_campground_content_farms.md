---
name: feedback_beware_campground_content_farms
description: Sites like pinecliffresort.net impersonate a parent operator with real-looking per-campground pages; never accept one as an operator source or a website
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45b0468a-4e5a-44b8-8a3e-d4e7d1bd4542
  modified: 2026-09-08T15:12:36.522Z
---

**`pinecliffresort.net` is a scraped SEO content farm, not a campground operator** — confirmed 2026-09-08 after AWH asked how we knew a kept entry was legit. It presents as "Pine Cliff Resort — Campgrounds & RV Parks", and each page carries a plausible campground name, a real street address and descriptive prose, so it reads exactly like a small chain's site for one of its parks. The tell is its own index: 16 paginated pages covering BWCA canoe campsites in Minnesota, Coal Banks Landing in Montana, Wyoming forest campgrounds and a free California dry camp — no real operator holds that portfolio.

**Why it matters:** it had contaminated the database from earlier state sweeps — 11 entries carried it in `website` and 15 cited it in `inclusion_evidence`, several as "Operator page". A validity proof resting on it is worthless, so those entries were effectively un-audited. It also fooled *this* session's web-presence audit into keeping three entries (Rest Rite WV, Valley Breeze KY, Rock River WY) whose only "live operator site" was one of its pages, and into backfilling it as a website.

**How to apply:**
- **Verify the operator, not just the page.** Before accepting any unfamiliar domain as an operator or parent business, open its index / "our parks" page and check the portfolio is geographically coherent. A "resort" with pages in six states that never repeat a region is a farm.
- **A per-campground page with a correct address proves nothing** — farms scrape accurate data. Plausibility is what they sell.
- **Real parent operators do exist and DO count** (rjourney, SteadyStays, a motel or museum with an RV park attached). The difference is a coherent, self-consistent portfolio and a business that transacts.
- **Never let an unfamiliar domain supply `inclusion_evidence`.** Authoritative means the agency/operator page or the reservation system — see [[reference_inclusion_audit]] and [[feedback_campground_vetting_discipline]].
- Entries removed under this: Rest Rite WV (1214), Valley Breeze KY (1611), Rock River WY (6567).

**Cleanup is COMPLETE (2026-09-08).** All 18 contaminated entries were re-vetted; no trace of the domain remains in `campgrounds.json`. 8 were re-evidenced from real sources (Camp Rio NM is the only one with a live bookable channel; the rest from provincial/state tourism, municipal pages, an operator site found by search, or the operator's own dormant Hipcamp listing). The remaining 9 went through a full `audit/inclusion_audit_instructions.md` pass: **4 kept** (3242 IA Hidden River on its own operator domain, found only by search; 4613 GA Hippie Hollow on a Harvest Hosts operator listing; 2629 CO and 8624 BC on dated 2026 firsthand stay reports, with the evidence string saying so) and **5 removed** — 1985 MO (operator's own post: "Must Stay at Least 1 Month"), 5531 MN (closed: parked domain + RV Life closed=1 + no review since 2024), and 1280 OH / 2057 MO / 9110 AB as unconfirmable. Database ends fully audited: inclusion 12768/12768, waterfront 12768/12768.

**Audit-agent results need verifying, not accepting.** The subagent returned `keep` for two of these on evidence that did not hold: for 9110 it cited rates at a URL that 404s (the real page carries no rates or site inventory at all), and for 1280 it leaned on an RV Life record plus allstays plus satellite — pure aggregator evidence, which those very instructions bar as a sole basis. Both were downgraded to `review` before applying. Spot-check every cited URL and ask whether the named source actually contains the claim.

**A full-database sweep for sibling farms found none.** Method worth reusing: extract every domain from `website`, keep those on 2+ entries whose name sounds like a single property (resort/campground/rvpark/lake/creek…), exclude known platforms and agencies, and eyeball the survivors. All legitimate multi-entry domains were real operators or agencies (Alabama State Parks, NL provincial parks, Grand River Conservation Authority, TVA Bear Creek Lakes, Merced ID's Lake McClure, Xanterra Yellowstone, Park With Us booking software, Sunrise Resorts). The same sweep caught two unrelated defects: a name collision putting a Byram-MS park's website on a Heber-Springs-AR entry, and `campingprepper.com` (a blog listicle whose domain no longer resolves) sitting in four entries' `website`.

**A related, separate lesson from the same question:** a campground can have consistent firsthand reports and still lack any authoritative confirmation. Chiriaco Summit CA (12375) was a free dry camp described by Campendium/RV Life/iOverlander, but the landowner — the General Patton Memorial Museum, whose site is actively maintained — mentions no camping at all. Removed. When the obvious authority is silent about a campground on its own land, that silence is evidence.

See also [[feedback_require_live_web_presence]], [[feedback_note_rate_sourcing]], [[feedback_campground_vetting_discipline]], [[reference_inclusion_audit]].
