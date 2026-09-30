---
name: project_private_gap
description: Private gap (queue item 3) started 2026-09-30 - measured, price gate REPLACED with the published-rate rule, work list in audit/private_gap_decisions.json
metadata:
  type: project
---

Queue item 3 of [[project_remaining_work_map]], started 2026-09-30.

**The gate changed (AWH 2026-09-30).** RV Life's `price_level <= 2` is no longer the private price gate. The gate is now the park's OWN published base rate <= $50/night (cheapest hookup RV site, peak weeknight, 2 adults, pre-tax/fees), read during vetting and written into `inclusion_evidence` with the year. RV Life `avg_rate <= $50` (or missing) is only the detection screen. Parks with no published rate fall back to avg_rate <= $40. Unrated / not-on-RV-Life parks are eligible with a quality signal elsewhere (Good Sam rating, or Google/Campendium/Dyrt >= 4.0 over ~25+ reviews) plus the firsthand-confirmation rule. Full text: docs/campground-curation.md "Private (commercial) campgrounds".

**Why:** a 34-park check (audit/private_gap_price_check.jsonl) showed avg_rate runs below published prices (median +$8, ratio 1.32), same $ tier only 16/26, >2x wrong at 4/26 (Pittsburgh Roaring Run $11 vs $45, Black Hills Vista $106 vs $45, Smooth Rapids $110 vs $35).

**Instrument:** `python3 audit/private_gap_list.py --state XX [--all]` (RV Life cache trip_data/rvlife_XX.json; Good Sam cache from `goodsam_discounts.py --fetch`, ~5 min in the cloud). Lower-48 pool under the new rule: 3,943 screen-passing (~2,700 after dropping casino/lodge/membership/church names), 1,717 unrated, 833 Good-Sam-only. MI: 108 / 31 / 18.

**Gotchas:**
- Many screen-passers were DELIBERATE skips in the original sweeps (MI commit 2233c5c names ~28: membership chains, lodges, casino lots, seasonal, closed). Grep the state's original private-sweep commit message before re-researching; record every verdict in audit/private_gap_decisions.json so it never happens again.
- Campspot and KOA 403 scripted fetches; headless Chromium (Playwright, `ignoreHTTPSErrors` for the sandbox proxy CA) loads KOA but Campspot search results don't render. Crowd-reported rates are aggregator-grade, never the gate.
- Cloud sandbox: Overpass main servers are proxy-blocked; maps.mail.ru mirror works.
- 78 entries use an aggregator (rvlife/dyrt/goodsam/campendium/allstays) as primary `website` - separate cleanup, not done.
