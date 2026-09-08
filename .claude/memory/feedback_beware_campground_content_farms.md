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
- Entries removed under this: Rest Rite WV (1214), Valley Breeze KY (1611), Rock River WY (6567). Still open: 14 entries across OH/MO/CO/NE/IA/MN/BC/AB/WA/CA/NL whose `inclusion_evidence` cites it and which need re-vetting.

**A related, separate lesson from the same question:** a campground can have consistent firsthand reports and still lack any authoritative confirmation. Chiriaco Summit CA (12375) was a free dry camp described by Campendium/RV Life/iOverlander, but the landowner — the General Patton Memorial Museum, whose site is actively maintained — mentions no camping at all. Removed. When the obvious authority is silent about a campground on its own land, that silence is evidence.

See also [[feedback_require_live_web_presence]], [[feedback_note_rate_sourcing]], [[feedback_campground_vetting_discipline]], [[reference_inclusion_audit]].
