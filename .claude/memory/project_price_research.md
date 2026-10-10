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
**Next planned**: CO/FS stragglers (55 unparsed FS
blocks -> ~30 are pass-only sites: Adventure Pass / Tonto / 3-day pass = an entrance-type fee, not
nightly; 8 Sawtooth NRA pages only link a fees page; 23 FS pages 404), then local/private one by one.
**Open singles**: NY Copake Falls, Hamlin Beach, Poke-O-Moonshine; MI Ely Lake; Lake Buffalo WV 121;
Cedarville SF MD 830 (booking unverified); WV WMAs (AWH handling).
