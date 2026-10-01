---
name: project_private_gap
description: "Private gap (queue item 3) started 2026-09-30 - measured, price gate REPLACED with the published-rate rule, work list in audit/private_gap_decisions.json"
metadata:
  node_type: memory
  type: project
  originSessionId: 09487be3-2acc-453b-83f0-9f2bf0c5b56e
  modified: 2026-10-01T16:27:09.820Z
---

Queue item 3 of [[project_remaining_work_map]], started 2026-09-30.

**GATE REVERSED AGAIN (AWH 2026-10-01), for simplicity:** RV Life `$`/`$$` passes price with NO price check; `$$$`+ is a skip unless a special exception (gateway); no tier -> avg_rate <= $40; no tier and no avg -> find a published rate <= $50. All other gates still apply. `audit/private_gap_list.py` screens on it. Retroactive handling of the 69 `$$$` private-gap adds (ids 14201-14306) and 336 legacy `$$$` private entries was put to AWH 2026-10-01 - check the answer before acting. The paragraph below is the superseded 2026-09-30 gate, kept for its measurements.

**The gate changed (AWH 2026-09-30).** RV Life's `price_level <= 2` is no longer the private price gate. The gate is now the park's OWN published base rate <= $50/night (cheapest hookup RV site, peak weeknight, 2 adults, pre-tax/fees), read during vetting and written into `inclusion_evidence` with the year. RV Life `avg_rate <= $50` (or missing) is only the detection screen. Parks with no published rate fall back to avg_rate <= $40. Unrated / not-on-RV-Life parks are eligible with a quality signal elsewhere (Good Sam rating, or Google/Campendium/Dyrt >= 4.0 over ~25+ reviews) plus the firsthand-confirmation rule. Full text: docs/campground-curation.md "Private (commercial) campgrounds".

**Why:** a 34-park check (audit/private_gap_price_check.jsonl) showed avg_rate runs below published prices (median +$8, ratio 1.32), same $ tier only 16/26, >2x wrong at 4/26 (Pittsburgh Roaring Run $11 vs $45, Black Hills Vista $106 vs $45, Smooth Rapids $110 vs $35).

**Instrument:** `python3 audit/private_gap_list.py --state XX [--all]` (RV Life cache trip_data/rvlife_XX.json; Good Sam cache from `goodsam_discounts.py --fetch`, ~5 min in the cloud). Lower-48 pool under the new rule: 3,943 screen-passing (~2,700 after dropping casino/lodge/membership/church names), 1,717 unrated, 833 Good-Sam-only. MI: 108 / 31 / 18.

**Gotchas:**
- Many screen-passers were DELIBERATE skips in the original sweeps (MI commit 2233c5c names ~28: membership chains, lodges, casino lots, seasonal, closed). Grep the state's original private-sweep commit message before re-researching; record every verdict in audit/private_gap_decisions.json so it never happens again.
- Campspot and KOA 403 scripted fetches; headless Chromium (Playwright, `ignoreHTTPSErrors` for the sandbox proxy CA) loads KOA but Campspot search results don't render. Crowd-reported rates are aggregator-grade, never the gate.
- Cloud sandbox: Overpass main servers are proxy-blocked; maps.mail.ru mirror works.
- Aggregator-as-primary-website cleanup WORKED 2026-10-01 (see below).

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
- **Temporary closures are structured now**: `status: {operating: "temporarily_closed", reopens, note}` (schema doc §4.5). Map draws them grey with a dark rim, "Show temporarily closed" filter on by default. 97 backfilled by `audit/closure_backfill.py`; its RECHECK list (21 past-dated closures) was worked 2026-09-30 (commit aab0740: 6 still closed, 15 open) - DONE. When a sweep adds a closed campground, put `status` in the results row (append_state.py copies it).
- Ministry-run campgrounds open to the public nightly are keeps (curation doc).

**PA first pass DONE 2026-09-30 (desktop): +19 (ids 14263-14281), 78 skips, 21 holds** - records in audit/pa_private/ (verdicts.jsonl, results_private_gap.json) + private_gap_decisions.json states.PA. Lessons:
- PA family campgrounds publish $55-70: 40 of the screen-passers failed on price even though every one had RV Life avg_rate <= $50. Expect the same in OH/NY/NJ.
- Electric-only sites count as the cheapest hookup site; a "primitive w/ electric" tent site does not.
- **ResNexus starts serving a human check after a few dozen park visits from one IP** - treat its parks as holds, don't retry hard. Holds are listed in decisions.json for AWH (rate engines, two "I am human" sites, Highland/Bodnarosa pins; truck-stop hookups (Love's) are NOT campgrounds (AWH)).
- Dedupe by NAME as well as by distance: Potter County Family (13104) looked new because the Good Sam pin was 6 km off; Montrose was deliberately removed 2026-09-08.
- **Next: VA**, then OH/NY/NC/NJ (memory list), plus PA holds when AWH has a few minutes.

**VA first pass DONE 2026-09-30: +10 (ids 14282-14291), 51 skips, 3 holds** (Rockahock, Small Country, Smith Mountain - engines unreadable). About 25 of the 64 candidates were already settled by the 2026-09-07 re-sweep (commit 0f4436c: Elks, Thousand Trails, timeshare/co-op/deeded parks) - read the state's earlier sweep commit FIRST, it saves half the work. Campspot `/book/<slug>/search/<in>/<out>/guests2,0,0/list` reads parks missing from the sitemap. **Next: OH**, then NY/NC/NJ.

**OH first pass DONE 2026-10-01: +15 (ids 14292-14306), 104 skips, 27 holds** (decisions.json states.OH lists them). Ohio Turnpike service plazas are skipped under the truck-stop rule. A Campspot July-weeknight quote overrules a lower "from" price on the operator's page (Wolfie's). This machine has no /usr/bin/google-chrome now - the helpers fall back to Playwright's bundled Chromium; scratch crawler rates2.py (follows rate/booking links, prints the booking ENGINE) was the productive tool. **Next: NY**, then NC/NJ.

**Holds CLEARED 2026-10-01**: AWH hand-read the last 10 (adds Big Bear Lake 14318, Ohio Christian University RV Park 14319 - its loop is on the N edge of campus, both pins were wrong; 8 skips: members-only x2, cabins-only, rental campers only, 47 seasonal vs 2 transient, $60, no presence x2).

**Aggregator-URL cleanup (2026-10-01, audit/aggregator_url/)**: 244 entries had an aggregator as first website. 38 now lead with an operator/town/Campspot page (2 renamed: The Barn RV Park 5275, Trailside RV & Bicycle Park 9847); kept as-is: 9 --AWH dispersed sites, ~30 town parks, ~83 bookable RoverPass listings. Of 86 removal candidates: AWH amended the live-presence rule (a Google listing at the pin, open, with phone and 25+ reviews counts) -> 48 kept, 1 got a site (Linton Campground 5945), 8 closed REMOVED (3883 5300 6992 7881 8071 8130 8723 8781); **29 still pending AWH OK to delete** (decisions.jsonl action=remove_candidate: 28 fail the rule, 11582 is now a long-term adult park). Rules settled: docs/campground-curation.md live-presence bullets. Pettibone Lake (3973) flagged: no longer on Newaygo County's parks list.

**NY first pass DONE 2026-10-01: +18 (ids 14320-14337), 38 skips, 9 holds** (decisions.json states.NY). NY was pre-playbook (49 private before). Lesson: under the 2026-10-01 gate a $/$$ (or unrated $-tier) RV Life row passes price with NO rate check - don't apply the $50 published test to tiered rows (I did, and reversed 4). Off-season imagery packed with trailers + no website = hold as 'reads mostly seasonal'. Top-A-Rise was already id 1476 (Good Sam pin 10 km off - name-dedupe!). **Next: NC**, then NJ.

**Holds checklist: `audit/private_gap_holds.md`** (9 open, all NY, 2026-10-01) - AWH works these by hand on the other machine. Regenerate with `python3 audit/private_gap_holds.py` after settling any (append a verdict row with private_gap_browser/v.py; latest row per name wins). OH/VA Google lookups are saved as audit/<st>_private/google.json.
