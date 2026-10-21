---
name: feedback_price_gate_proximity_exceptions
description: AWH keeps some over-$50 / skip-brand campgrounds because of where they are (near family, near NYC); don't remove them on price or brand
metadata:
  type: feedback
---

**STANDING RULE, AWH 2026-10-19: "From now on you may drop any campground that is over the price limit unless it has a specific exception (which includes gateway campgrounds)."** I may drop on my own and just report which ones. Specific exceptions = the named ones below + gateways.py + Good Sam rate test; the gate is still private-only (local/government has no limit — Earl Warren Showgrounds 11749 stays). This supersedes "leave the existing ones for now" for any entry I touch; a sweep of the older over-limit entries is permitted but offer it before running. SWEEP DONE 2026-10-19 (audit/price_research/overgate_2026-10-19/: screen.py, kept_on_review.json, apply.py): 311 over-gate private -> 104 exempt (57 gateway, 26 Good Sam, 14 named, 7 family stayed), 9 kept on reading (tax-included figures, posted GS/cash/2-person rates, Periwinkle 556 = 9 km from Fort Myers family), 198 dropped (193 after the --AWH restores). **An --AWH note is a specific exception (AWH 2026-10-19):** AWH added those parks firsthand knowing the price, so never drop one on the gate; the sweep first dropped 5 (River's Edge VA 13, Fourth Moon 746, Trout Camp 750, Pragma Farms 755, Seven Islands 759) and they were restored. Final: 193 dropped. Lessons: stored nightly_low is sometimes TAX-INCLUDED (Aintree, Pine Cone, Drifters) - compare before tax; a near-family entry is an exception. First drops: Cal-Nev-Ari 11277, Peace Garden 5928 (admission counted), Whitesands 8335 (per-person rate x2), log audit/price_research/dropped_2026-10-19.jsonl.

**Good Sam discount counts (AWH 2026-10-14):** AWH is a Good Sam member, so at a Good Sam Park (discounts.good_sam true) test the park's posted Good Sam rate, else rate less 10%, against the gate. fees keeps the undiscounted rate. Restored 2227, 4943, 7385, 7860 on it.

Some campgrounds stay in the DB despite failing the $50 price gate or the KOA/Sun brand skip, because their location is unusually useful:

- 14882 Fort Myers / Pine Island KOA Holiday (FL, $104.50+) - near one of the family homes (AWH 2026-10-10).
- The Fort Myers relaxed-price mini-sweep (2026-10-05, ids 14868-14877 + holds 14880/14881) is the same family-proximity exception; AWH 2026-10-10 confirmed Bonita Lake 14875, Imperial Bonita Estates 14876, Sanctuary 14877 stay.
- 14435 Twin Palms Resort (FL, Lakeport; RV sites exactly $50) kept (AWH 2026-10-10) - $50 is at the gate, not over.
- 3363 Liberty Harbor RV Park (NJ, $170/$189 holiday) - "unusual proximity to New York City" (AWH 2026-10-10).

**Why:** the gate screens ordinary options; a rare location (family visits, a city with almost no RV camping) outweighs price.

**How to apply:** record the real price, but don't flag these for removal again. When a new over-gate entry is near family or a major city with few alternatives, ask rather than drop. Related: [[feedback_skip_sun_koa_brands]], [[feedback_mandatory_fees_count]].

**Scope of the gate (AWH 2026-10-10, confirmed):** the $50 price gate applies to PRIVATE campgrounds only. Government campgrounds (county/city/water district/fairgrounds/state/federal) have no price limit - don't flag them as over-gate (Santee Lakes $62-111 and Bay RV Stay $85-125 are fine).

**General rule since AWH 2026-10-14 (#4 and the over-limit list): "drop if over price limit unless very close to major gateway points (major cities, major tourist attractions, National Parks, etc.)".** The test is `audit/price_research/gateways.py`: within 40 km of the downtown of a 1M+ metro, a US or Canadian national park entrance or main visitor center, or a listed major attraction. The limit is the base rate before tax: US$50, C$69 (C$55 in one report was an error). Dropped on it 2026-10-14: Cedars 8295, Bare Oaks 12636, Country Gardens 12648, Fisherman's Cove 12655, Riviera 1990, The Outpost 1496, Nevada Treasure 11305, Rolle's Lynda Vista 14851, Millwood 14655, Harmony Ridge 1823 (768c56d); Camp Central North 4798 ($65) and Happy Camp 7547 ($60-70) (5479fc1); 16 more in the RoverPass operator pass (37768ea). Kept: Rockwell 14708 ($65, 11 km from downtown Oklahoma City). Worcester MA (metro under 1M) came off the metro list. The named exceptions above still stand. AWH 2026-10-14 on the 73 older over-limit private entries: "leave the existing ones for now" - don't drop them unless AWH reopens it that the 10-01 "Not retroactive" rule keeps (the Fort Myers exceptions and the #2 long-stay parks are not counted).

**Periwinkle Park 556 (Sanibel, $65-70, also sells lots/residences) KEPT by AWH 2026-10-21 for its proximity to a family home.** This is the same family-home exception as the Fort Myers / Pine Island KOA. It covers both the price gate and the long-stay "sells lots" test. Don't re-flag it.

**Family homes are gateways (AWH 2026-10-21):** "Add family homes to the list of areas that cause campground price caps to be lifted." `gateways.py` now reads every kind "family" entry from the gitignored trip_data/family.json at import and uses the same 40 km straight-line radius. It reports only "family home", because these labels get copied into tracked evidence. With no family.json (a fresh clone) there are no family points, so run price-gate work where that file exists.
- **Retro check, same day:** of the 548 price- and verify-dropped ids, only 4 fall within 40 km of a family home with no other gateway: Orange Grove 14868, Gulf Waters 14871, Sanctuary 14877 and Swan Lake 14880. All four were dropped for non-price reasons, so nothing came back.
- **Not yet re-screened:** private-gap and KOA candidates that were never added because of price.
