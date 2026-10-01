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
- Good Sam's directory has no operator URLs for most private parks. **Good Sam quality bar = overall (`general`) >= 8.5** (AWH 2026-09-30; calibrated: median GS 8.2 at RV Life 3*, 8.7 at 4*). Oak Knoll (7.7) was added then moved back to a hold; id 14216 is retired. MI net +28.
- Deploy to PA needs the laptop's SSH keys - not available in the cloud session; pushed to master only.

**Desktop session 2026-09-30 (later): MD +2 (14230-14231), DE 0, MI holds re-read +5 (14232-14236).** Records in audit/{md,de,mi}_private/verdicts.jsonl + private_gap_decisions.json. Next (AWH 2026-09-30, moving to a non-cloud machine): FIRST settle the remaining MI holds with the headless browser (verdicts.jsonl, latest row per name wins), THEN WV - candidates listed in audit/wv_private/candidates.json (38 screen / 20 unrated / 3 GS-only; the 2026-09-15 re-sweep skips are in its results_batch*.json), then PA/VA/OH/NY/NC/NJ. The Good Sam cache (trip_data/goodsam_parks.json) is gitignored: run `goodsam_discounts.py --fetch` (~5 min) on the new machine before private_gap_list.py.
- **On the desktop, headless Chrome reads what the cloud could not**: ResNexus, Open Campground (no reCAPTCHA), Campspot availability, Newbook, Wix/script sites. Setup: `pip install --target ~/.cache/ekko-pw playwright`, launch with `executable_path='/usr/bin/google-chrome'`, `wait_until='domcontentloaded'` (Wix never fires load). Helpers are committed in audit/private_gap_browser/ (README has setup; txt.py page->text, cs.py Campspot quote, newbook.py, sat.py Esri crop, geo.py Census geocode, v.py append verdict). CampLife still 403s. So the MI "rate unreadable" holds were mostly a cloud artifact - re-read holds on the desktop before asking AWH.
- Campspot park sitemap is now `campspot.com/c/sitemap/park/sitemap.xml` (old path redirects); fetch it with the browser.
- Hipcamp listings render in the browser after ~20 s (active listing = live presence; a real 60-site campground booked only via Hipcamp is still `private`, not `hipcamp`).
- RV Life pins can be on the wrong parcel entirely (Northern Bear Paw 500 m off, on farmland) - a Nominatim search of the street address found the OSM caravan_site node.

**Desktop session 2 (2026-09-30 evening): MI holds second pass +10 (14237-14246), 18 skips, 7 held** (commit 4cc5470). Lessons:
- **Google Maps is the working quality source** for parks RV Life doesn't rate or rates on 1-4 reviews: `audit/private_gap_browser/gm.py` reads rating + review count, coords, phone AND the park's current website from the place panel. It also cured most "no live web presence" holds - Google knew the new domain (wonderwoodsmichigan.com, campnorthernsites.com, ivansmichigan.com, greenvalleycampgrounds.com). Run it before calling a park dead. A lodging-style panel hides the count (Val-Du). Review text is not readable logged-out.
- The Good Sam fetch cache (`goodsam_parks.json`) carries NO ratings - `gsr.py ST "name"` queries Algolia for them; check the returned name, the top hit is often a different park.
- Call-for-rates parks were settled by the documented fallback (avg_rate <= $40), not left held.
- "I am human" interstitials (Rivers Bend, lakegeorgecamp.wordpress.com) are not to be bypassed - hold for AWH.
- Still held for AWH: Sutter's and Green Valley (pass price+quality, but off-season imagery full of trailers reads mostly seasonal), Val-Du, Lake George, Rivers Bend, Manistee (CampLife), Best Bear. WV DONE same evening: +9 (14248-14256), 37 skips, 3 held (Revelle's Staylist, American Way 4-night min, Yokum's Lower pin). AWH hand-read Lake George ($50, added 14247) and Sutter's (220 sites, ~20 transient -> skipped as mostly seasonal). **Next: PA**, then VA/OH/NY/NC/NJ. Method that worked for WV: gm.py over the whole candidate list first (background), rates.py crawl of operator sites in parallel, then triage; Overpass times out often - pin from satellite instead.


**2026-09-30 side work, both AWH-directed:**
- **Temporary closures are structured now**: `status: {operating: "temporarily_closed", reopens, note}` (schema doc §4.5). Map draws them grey with a dark rim, "Show temporarily closed" filter on by default. 97 backfilled by `audit/closure_backfill.py`; its RECHECK list (21 past-dated closures) still needs a person. When a sweep adds a closed campground, put `status` in the results row (append_state.py copies it).
- Ministry-run campgrounds open to the public nightly are keeps (curation doc).

**PA first pass DONE 2026-09-30 (desktop): +19 (ids 14263-14281), 78 skips, 21 holds** - records in audit/pa_private/ (verdicts.jsonl, results_private_gap.json) + private_gap_decisions.json states.PA. Lessons:
- PA family campgrounds publish $55-70: 40 of the screen-passers failed on price even though every one had RV Life avg_rate <= $50. Expect the same in OH/NY/NJ.
- Electric-only sites count as the cheapest hookup site; a "primitive w/ electric" tent site does not.
- **ResNexus starts serving a human check after a few dozen park visits from one IP** - treat its parks as holds, don't retry hard. Holds are listed in decisions.json for AWH (rate engines, two "I am human" sites, Highland/Bodnarosa pins; truck-stop hookups (Love's) are NOT campgrounds (AWH)).
- Dedupe by NAME as well as by distance: Potter County Family (13104) looked new because the Good Sam pin was 6 km off; Montrose was deliberately removed 2026-09-08.
- **Next: VA**, then OH/NY/NC/NJ (memory list), plus PA holds when AWH has a few minutes.
