---
name: reference_campspot_api
description: How to price a Campspot park - its private JSON API through the one driver browser (header x-client-type CONSUMER; CloudFront blocks ~590 calls in 6.5 min, so pace 3 s), the reader/builder pair from the 421 pass, what a quote means, and the traps (closed dates still quote, never compose a slug)
metadata:
  type: reference
---

Campspot prices come from Campspot's own private JSON API, called from a campspot.com page open in the one driver browser (`audit/private_gap_browser/drv_server.py`; `drv.py quit` when done). A plain curl/urllib of campspot.com answers 403, and every API call needs the header `x-client-type: CONSUMER` ("Unknown request." without it). The endpoints, the guests string (every category in the park's order, plus a pets slot) and the pacing are at the top of `audit/private_gap_browser/campspot_api.py`. The builder's method (what is stored, how fees are fitted, closed dates) is the docstring of `audit/price_research/campspot_tier_build.py`. Built for the 421 tier-only entries of 2026-10-13 ([[project_price_research]]).

- **Pace:** CloudFront answered "403 Request blocked" after ~590 calls in ~6½ minutes. One call per 3 s (`CS_PAUSE`). The reader stops at the first block without writing that park, so re-running the same command resumes. Never run two readers ([[feedback-limit-headless-browsers]]).
- **Slugs:** `/park/<marketplace slug>` and `/book/<engine slug>` both resolve through `parks/slug/<slug>`. A dead slug errors GATOR-3. Copy a slug from the website field, the operator's own Book link or the evidence. Never build one from the name: a guessed `/park/` slug got into a report once.
- **What a quote means:** the list average is the site charge + the park's own fees + Campspot's 3% booking fee (minimum $3), before tax.
  - Store the site charge after any automatic discount, plus any fee the park charges every night.
  - A flat per-stay park fee goes in `fees.reservation_fee`. A percentage, or a fee only some types carry, goes in the note.
  - Campspot's own fee is the platform's: never stored, only mentioned in the note.
  - A 2-night quote (`campspot_api.py --add WHY ID:TYPE:DATE:2`) tells a per-stay fee from a per-night one.
- **Closed dates still quote a price**, not always the season's. The builder sets them aside when another date is open (RESORT_CLOSED_RULE on every RV type). If every date read is closed, the closed-date quote is used, the note says so, and it is re-checked in spring: Fergus 6117, Bear Lake 12639, Serpent River 12698, Karner Blue 14224.
- **Closures are inclusive:** the season opens on a closure's end + 1 day and closes on the next closure's start − 1 day. A listing is dead if its closure calendar ended years ago (Winding Creek 14229: 2024) or no type lists a site. Price it from the operator's page, or hold it.
- **"No campsites available" on every type, with no closure** (Duke Creek in January) is not a price. Builder OVERRIDE keys, per park:
  - `skip_dates` + `dates_text`: drop those dates and say why;
  - `skip`: a type to leave out;
  - `fee_text` / `fee_model`: a fee the fit can't settle;
  - `mins_text`: the minimum-stay sentence.
- **Minimums:** when every Tuesday asks for 2+ nights, run `audit/private_gap_browser/campspot_dates.py` on more dates. It separates a standing minimum (`booking.min_stay`, written by hand, [[feedback-minimum-stay]]) from a run of event dates. Summer sold only in Saturday-to-Saturday weeks (Sandbanks 12695) is a 7-night minimum.
- **Operator page vs Campspot:** when they differ, the range spans both and the note quotes each.
- **Waterfront:** a Campspot type tagged "Waterfront Site", or named lakefront or waterfront, at a campground audited not waterfront is a lead for a re-audit, not a waterfront call. The 2026-10-13 re-audit of 9 such leads changed 5 and kept 4: `campspot_map.py` draws the per-site map, and each type's photos (`images.slideshowImages` in the availability JSON) show the ground the satellite may predate. The name alone decided nothing (Spirit Springs' "WATERFRONT" sites sit across a road behind a tree belt).
- **Per batch:** the outputs are committed in `audit/price_research/campspot_tier/`; `report_items_2026-10-13.md` there holds what each batch raised. Steps, in order:
  1. reader;
  2. builder `--ids` (+ `--fields`);
  3. hand findings for the parks Campspot can't price;
  4. extra field sets;
  5. notes ([[feedback-clean-up-notes]]);
  6. `merge_notes.py`;
  7. `audit/note_scan/clean_notes.py`;
  8. `assemble.py`;
  9. `apply.py`;
  10. note scan ([[reference_session_note_scan]]);
  11. a by-id diff of campgrounds.json (only the batch's ids may change);
  12. tests;
  13. commit.
- **QC:** before landing anything, check that every quoted string appears in a saved page. The helpers were session scratch: a whitespace- and case-normalized search over the saved `.txt` pages is all they did.
