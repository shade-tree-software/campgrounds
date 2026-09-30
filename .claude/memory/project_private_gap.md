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

**MI first pass DONE 2026-09-30: +29 (ids 14201-14229)**, 24 skips, 43 holds; record `audit/mi_private/`. Unrated RV Life remainder (~25) still open. Lessons:
- **Holds dominate (43 vs 29 adds), and most are "rate unreadable"**, not "no": ResNexus (Incapsula), Open Campground (reCAPTCHA), CampLife, JS-only sites, call-for-rates. A person with a browser or phone clears these fast - batch them for AWH rather than grinding.
- **Campspot is the best price source**: `campspot.com/park/<slug>?checkin=YYYY-MM-DD&checkout=...&guests=2,0,0` in headless Chromium (Playwright, `ignoreHTTPSErrors`, retry the proxy's ERR_TOO_MANY_RETRIES) lists every site type with "Starting at $X" - the price FOLLOWS its site description in the page text. Slugs: the park sitemap (`campspot.com/about/documents/park-sitemap.xml`, fetch with a browser); NOT every slug ends in `-<st>` (beaver-trail-campground) and some match other states (lucky-lake-208 is Idaho). Campspot's "N verified reviews" rating is a usable quality signal for unrated parks.
- **RV Life park pages embed `cg_url`** (operator site) - `audit/private_gap_enrich.py` pulls it + a live probe for every candidate in ~40 s.
- **The price gate removed ~1/3 of screen-passers** even at <= $50 published: RV Life's avg_rate lags, so a $43-48 RV Life park often publishes $53-65 (Lakeshore, TeePee, Pine Ridge, Waterways, Alice Springs, Hungry Horse, Goff Lake).
- **Christian camps that rent their campground to the public nightly are keeps** (Covenant Hills, Winding Creek) - "church-retreat only" is the exclusion, not church-run.
- **No trip_data/family.json in a cloud checkout** -> `append_state.py` now refuses without `--min-id`; MI used 14201 (14175-14200 skipped on purpose).
- Good Sam's directory has no operator URLs for most private parks; its triple rating (all >= 7.0, my threshold, unconfirmed by AWH) served as the quality signal for Oak Knoll.
- Deploy to PA needs the laptop's SSH keys - not available in the cloud session; pushed to master only.
