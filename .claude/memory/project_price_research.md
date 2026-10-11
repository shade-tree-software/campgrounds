---
name: project_price_research
description: Task #2 handoff (2026-10-10) - nightly-fee research for no-price entries; what's done, tools, open lists, next steps
metadata:
  type: project
---

AWH 2026-10-09 "Continue with #2": price every entry with no `fees` and no RV Life `price_tier`.
All writes go through `audit/price_research/apply.py FINDINGS.json [--apply]` (skips entries
that already have fees or a manual/reported fees group; provenance `{source, checked}`, no method).

**Done (all committed on claude/note-scan-gajem7, not yet merged to master as of 2026-10-10):**
- Dispersed 64/89 (dispersed_1/2.json); MI state forests 111 (registry row
  `state:michigan-state-forests`) + MI state parks 87; NY 45; WA DNR 34 (`state:washington-dnr`)
  + 4 WA parks; MT FAS 43 fee sites.
- **Forest Service pages**: `fs_fees.py --fetch/--build/--show` (cache trip_data/fs_fees.json,
  gitignored) -> 575 (fs_fees_findings.json) + 25 hand-read (fs_fees_hand.json). Parser keeps
  single/standard sites only; drops double/group/walk-in, extra-vehicle/holiday/hookup add-ons,
  pass-holder discount prices, and pre-2026 clauses when a 2026 price is given. OVERRIDE dict
  holds hand calls (Whitetail 6266 left out; Oak Flat 12216 = $20).
- **recreation.gov**: `recgov_rates.py --fetch/--build` (cache trip_data/recgov_rates.json, 2,414
  facilities) -> 2,286 entries (recgov_findings.json). Current seasons, STANDARD/RV types; per-site
  "u52-00p0..." override keys used only when no plain key; drops glamping/triple/long-term and
  prices > 2x median. ScanPay names ARE real nightly rates (don't filter them).
- Booking fixes 2026-10-10: 29 free FS dispersed sites got own booking reservable:false/fcfs always
  (were inheriting federal "recreation.gov 180 days"). 22 PA state FOREST motorized sites + 7 MD state
  forest entries got `policy_ref: "none"` + own booking (registry merges per field, so a forest row
  can't clear the state-park `min_stay`; "none" is the only clean opt-out). PA: reservable 330 days
  to noon of arrival, 7-night max. MD Potomac-Garrett (41-44) + Green Ridge (129): FCFS self-register
  $10. Savage River Big Run (89) / St. John's Rock (64): reservation only.

**Remaining**: ~1,607 entries with neither fees nor price_tier (counting may differ from the
earlier 1,476/1,553). Biggest buckets: QC private 81, WI state 71 (PARKED - GoingToCamp hides prices
until a site is picked), IA local 63, TX private 56, AL private 54, WI local 45, CO federal 41,
BC/ON private 40 each, NY local 38, CA local 38, AL local 37, KY state 31, MT state 31 (license-only
FAS, see mt_fas_license_only.txt), WA state 30.
**2026-10-10: KY DONE** — 31 entries (29 state parks + Horse Park + Nolin) from per-site RA prices (`kentuckystateparks.reserveamerica.com/campsiteDetails.do?...&arvdate=M/D/YYYY&lengthOfStay=1` shows 'Price Breakdown: Camping Fees (1 night)'; no date = no price; scraper recipe in ky_state_parks.json sources). Same trick should work on every classic RA host (MD, MA, TX, UT, MT, OK, NY...). **The 'WA state 30' bucket was a miscount**: all 30 are DNR camps already inheriting $0 + Discover Pass from `state:washington-dnr` — count remaining with registry inheritance resolved, not raw `fees`.
**2026-10-10 (later): state stragglers +43** — AL 20 (reserve.alapark.com Calendar View, `al_state_parks_scrape.py`; same vendor runs reserve.tnstateparks.com via `--host`), TN 3, WY Glendo 4 (2026 statewide schedule), OK/UT/FL/NH/CT/VT/MD 10 via **`ra_site_prices.py`** (classic RA per-site 'Camping Fees (1 night)' by plain urllib; price shows even on booked nights; RA rate tables EXCLUDE hookup attribute fees - Beavers Bend table $18 vs real $40-48), NV 2, ND 1. **True remaining count = 1,227 → 1,187** (registry inheritance resolved via `cs.resolve(r, campground_policies.json)`). **WRONG, corrected 2026-10-10:** CO federal / WI state do NOT inherit a rate - they inherit a fees group holding only a note/surcharge. Left unpriced on purpose: AL Fort Toulouse/Bladon Springs/Little River SF (undated aggregator figures only), KS 5 (ksoutdoors fee pages block every fetch path; fees change 2026-11-01), MO Long Branch (closed 2026, rate PDF link dead), TN state parks closed for renovation (Pickwick Main is closed per its banner but has NO `status` flag - tell AWH). Not yet tried: NJ Stokes Shotwell, ID Challis Hot Springs, ND Hahn's Bay, MS John W. Starr, KY local 19, the /explore/ new-RA locals (NY 1438, MA 13355, NY 13359).
**2026-10-10 (3rd pass): platform buckets +110 → 1,077 left.** Campspot 25 (`campspot_prices.py`: drives one browser, reads the availability JSON the park page fetches - curl/page-context fetch are refused), mycountyparks 27 (`mycountyparks_fees.py`, plain urllib digest of facility 'Fees' text, read by hand), Hipcamp 35 (`hipcamp_prices.py`, __NEXT_DATA__ land.sites.edges: host pricePerNight + ~18% service fee noted), Natrona WY 9, NWFWMD FL 8 ($0, 'Use of District lands is free of charge'), Suffolk NY 6 (Mar-2026 PDF schedule). Closed flags added: Pickwick Main 13725, Kettletown 13975. **Flagged for AWH, not acted on:** Hipcamp 7 Lovers Lane (no RV site) REMOVED per AWH 2026-10-10; 671 Grouseland (2-night min on every site) KEPT as an AWH exception, min_stay + fees $66.50 recorded; 4859 Clay County FG (ASLEEP Hipcamp, but local with phone + county site) KEPT per AWH; 368/774 (ASLEEP) and 767/770 (listing gone) REMOVED 2026-10-10 per AWH rule: a private campground needs a working booking site showing prices, or operator-published rates + a booking phone - none had any other channel (Campertunity's scraped price for 368 doesn't count); Tosanak 13500 RV sites 2-night minimum - KEPT as AWH exception with note. Hillside RV 14677 priced $32 from AWH's own Campspot checkout (manual). Clay County FG 4859: Hipcamp link dropped, booking platform=phone. Skipped: MWCD 5 (only a 2024 brochure), PG&E 12 (no published fees), Summers County WV WMAs (AWH handling WV WMAs), Idaho getoutside.idaho.gov (captcha), NJ dep.nj.gov (bot wall), McGowen 3116 / Deep Lakes 13505.
**Next planned**: CO/FS stragglers (55 unparsed FS
blocks -> ~30 are pass-only sites: Adventure Pass / Tonto / 3-day pass = an entrance-type fee, not
nightly; 8 Sawtooth NRA pages only link a fees page; 23 FS pages 404), then local/private one by one.
**Open singles**: NY Copake Falls, Hamlin Beach, Poke-O-Moonshine; MI Ely Lake; Lake Buffalo WV 121;
Cedarville SF MD 830 (booking unverified); WV WMAs (AWH handling).

**2026-10-10 AWH checks:** Stokes 1818/1819 priced ($20 res / +$5 non-res; AWH read $25 at NJ Outdoors) and min_stay 2 always recorded - a standing minimum, KEPT as an AWH exception. Deep Lakes 13505 $40 (AWH). REMOVED per AWH: McGowen 3116, Fort Toulouse 4928, Bladon Springs 4861, Little River SF 4873 (no rates, no working booking site). Kansas 5: HOLD per AWH, revisit after 2026-11-01. Challis 13966 $31-47 (AWH). MWCD/PG&E: URLs given to AWH for reading.

**MWCD done 2026-10-10:** AWH saved each lake's reserve.mwcd.org calendar (Jul 2027) to ~/Downloads; parsed with the site-row data-* attrs (usetype/electric/water/sewer/maxrv + per-date price). 7 priced (1238, 1228, 13345, 13347, 1240, 13346, 13344). Leesville North Fork 13349 $44-48 from the operator's rate list (AWH saved page). South Fork 13348 (FCFS, MWCD, call Atwood 330-343-6780) left unpriced per AWH 2026-10-10 - do not chase.

**PG&E done 2026-10-10:** all 21 PG&E entries priced from recreation.pge.com site cards (POST the search form; 'Use Fee' is the STAY total, halve a 2-night search). Recipe in audit/price_research/pge/README.md. Reservations need 2+ nights (FAQ) but every PG&E campground has FCFS sites; min_stay 2 recorded on the 14 with reservable sites (fcfs some_sites, note says one-night FCFS stays are possible, kept per AWH); the 7 all-FCFS ones (Fuller Grove, Hawkins, Navy, Oak Flat, Pogie, Ruling, Sunset) set reservable false, fcfs always, no min_stay.

**2026-10-10 (4th pass): site_digest.py sweep, 1,046 -> 652 left.**
- `audit/price_research/site_digest.py --state XX --ownership local OUT` (or `--ids`) fetches each unpriced entry's website plus up to 3 rate/fee subpages (PDFs via pdftotext) and prints the lines carrying money figures.
- It is read by hand; findings go to `*_local.json` / `us_private_N.json` and are applied with `apply.py`.
- Done: all US local buckets (~190 priced) and all 341 US private (~210 priced).
- Rules used:
  - Only the operator's own page or its booking channel counts (Campspot/RoverPass/Firefly page of that park).
  - A dated firsthand Campendium figure is acceptable only when there's no operator page.
  - Good Sam / The Dyrt "from $N" is never used.
  - Mandatory per-person passes go in `fees.entrance` (Veyo).
- What's left: entries whose sites post no figure or need JavaScript, Canada private (209, digest running), MT state 31 (license-only FAS).
- Flags for AWH are in the session summary (standing minimums, closures, KOA, no-website privates).

**5th pass (residue, 2026-10-10):** 507 -> 379 unpriced. Rendered every remaining operator site once in one headless browser (scratchpad bq.py run over all 407; a hung site stalled it 30 min - watch for stalls) + WebSearch for official pages of no-website entries + live Campspot quotes; 126 priced (audit/price_research/residue_1..4.json). Dead ends: Firefly (date picker won't take scripted dates), reserve.tnstateparks.com (403 to headless; no official TN rate sheet - 9 TN state campgrounds stay unpriced), Lehi city site (403), mostateparks fee page. Left: MT FAS (license only), KS fishing lakes (hold), WV WMAs (AWH), no-website/Facebook-only, and sites that post no rate.

**COUNTING BUG found 2026-10-10 (after the residue pass):** every count above (1,187 / 1,077 / 652 / 379) and `site_digest.py`'s target list treated `cs.resolve(...).get('fees')` as 'priced', but 309 entries inherit an agency fees group with NO nightly_low/high (note, surcharge, entrance or reservation fee only). Count 'priced' as nightly_low or nightly_high present (own or inherited). True no-rate total 2026-10-10 = **685** = 376 with no fees group (the worked residue) + 309 hidden: WI state 71, CO federal 41 (FCFS rec.gov listings - rec.gov camps API 404s and RIDB FacilityUseFeeDescription is blank for them, so the FS recarea page is the source), VA DWR WMAs 23 (no nightly fee by rule, $10 authorization + $4/person/day permit - $0-or-absent is AWH's call), IL state 23, SC state 22, CO state 17, NC state 15, WV federal 14, AR federal 9, MI federal 8, PA state 7, WV state 7 (Inntopia), ~40 scattered.

**6th pass, 2026-10-10/11: 685 -> 405** (count = no nightly rate own/inherited and no RV Life tier; `audit/price_research/unpriced.py`). VA WMAs $26 (AWH: two people, one night, all-in). Colorado 56 (FS/BLM/NPS pages; forest **sitemaps** `fs.usda.gov/rNN/<forest>/sitemap.xml` give the slugs old links lost; CPW park fee tables + per-site rates on cpwshop `r/campsiteDetails.page?parkID=&siteID=` show '$X/Per Night'). Federal 39 more (BLM/NPS/USACE pages via the browser, rec.gov rate tables; rec.gov `api/search` carries `price_range`). **Wisconsin 70 via GoingToCamp: `gtc_prices.py` - POST /api/resource/feeDetails?resourceId=&startDate= (body []) returns a site's nightly fee; one call per feeScheduleId** (works on any GoingToCamp host, e.g. Thunder Bay; --currency CAD). SC state parks 15 via al_state_parks_scrape.py --host reserve.southcarolinaparks.com (same vendor as AL/TN). Registry: state:NC now carries the statewide $30-45 table (27 entries inherit); state:CO entrance is split by residency. IL 22 from the 2027 IDNR schedule ($11 non-electric / $28 electric) + each park's site classes; NE from the statewide 2025 grid ($10-35; PDF fetched through the browser in chunks); NY via ra_site_prices (now reads 'Use Fees (1 night)'). ResNexus = human captcha + anti-scraping terms: do not automate. Open questions for AWH (MT FAS licence-only, CO SWAs, FLREA dispersed $0, likely drops, 112 note-only prices): `audit/price_research/open_questions_2026-10-11.md`. Pushed and deployed at 58b5517 (2026-10-11).

**AWH decisions applied 2026-10-11: 405 -> 266.** CO SWAs 2268/14478 = $40 (2 people x 2 one-day SWA passes x $10: a one-day pass is valid only on its date; everyone 16+; annual fishing/small-game/big-game/turkey licence holders exempt; annual pass $43.87), as entry fees with `policy_ref: none` because state:CO is the PARK system (vehicle pass, cpwshop) - `co_swa.json`. GW/Monongahela dispersed 13 = free, method manual (FLREA 16 USC 6802(d)(1)(E)) - `gw_mon_dispersed.json`. 16 "probably drop" entries removed - `dropped_2026-10-11.jsonl`. **Note-only prices accepted** (108 of 110; 1459 gives only a surcharge, 14683 only a weekly rate) - `note_prices.json`, provenance method `derived`, source `our note[ (entry added DATE)]: '<quote>'; recheck <website urls>`. To re-check later: `unpriced.py --from-note` lists them with the page, `site_digest.py --ids` re-reads, `apply.py --replace-derived` lands a confirmed figure over a derived one (never over manual/reported). 16 of the 108 have no operator page (tourism/aggregator listing or nothing), so a re-check there starts by finding the operator. Donation-only -> 0/0 per the free-fees rule (13572); 13395's $22 is the non-resident rate. Don't date notes with `git blame`: later bulk passes (RV Life lift, field scans) touched most note lines; the commit that ADDED the entry is the usable date. Still open: MT FAS 31 (no answer yet).
