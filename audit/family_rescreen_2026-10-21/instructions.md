# Family-home price re-screen (AWH 2026-10-21): agent instructions

AWH made family homes price-gate gateways on 2026-10-21. A private park within 40 km of a family home now
skips the US$50 cap (`audit/price_research/gateways.py`). Each candidate here was skipped earlier only
on price: either an over-$50 published rate, or RV Life's `$$$`+ tier at the list stage. None is in the
database. Your job is to vet ONE candidate as a normal new add, applying every gate except price, and
write one result file.

## Read first
- `audit/add_research_instructions_pa_private.md`: inclusion criteria, ownership classes, the
  seasonal-park risk, pinning, elevation, website/phone rules and the result-record shape. Follow it,
  with the changes below.
- `docs/campground-curation.md` lines 14-54 (inclusion criteria, including the five long-stay tests in
  the "Long-stay, seasonal and residential parks" bullet) and the waterfront gate (search "waterfront"
  in lines 55-200).
- `audit/private_gap_browser/README.md`, for the helpers: `txt.py`, `gm.py`, `sat.py`/`satz.py`,
  `cs.py`/`csl.py` (Campspot), `newbook.py`, the `drv_server.py`/`drv.py` driver, and `koa.py` for a KOA.

## Changes from the PA instructions
- **Price:** there is no price gate. Still read the current rate from the operator's own site or its
  booking engine, dated 2024 or later. Use the cheapest site a 23-ft motorhome fits, as the base rate
  before tax for a weeknight in season. Add any mandatory per-night resort or grounds fee
  ([[feedback_mandatory_fees_count]]). Return it as `fees` (below). A park with no readable rate
  anywhere fails the presence rule (private parks need a price and a live presence), so skip it with
  kind_of_no "no rate".
- **Long-stay tests 2-5** (curation doc) apply in full:
  - Nights must really be for sale, with no application, lease or waitlist.
  - Skip a park with a standing minimum over 2 nights outside holiday weekends.
  - At least 1 site in 10 must be sold by the night where a count exists.
  - Skip a park that sells homes or lots, or whose homes outnumber its RV sites. A 55+ community that
    advertises "units for sale" with a resident application is a skip ([[feedback-exclude-seasonal-residential]]).
  - **The peak-season exception (AWH 2026-10-21):** a long-stay rule (e.g. monthly-only Dec-Mar) is OK
    only if it applies to peak season alone, lasts no more than 3 months, and the note says so. Longer
    than 3 months fails test 3.
  - A standing 2-night minimum is fine. Return it in `booking.min_stay`, in the doc §4.1 shape.
  - 55+ or adults-only is a note line, not a skip.
- **The 23-ft fit:** skip if the largest drive-in sites cap under ~23 ft. Skip if the park admits only
  Class A or 5th wheels, or sets a minimum rig length or age rule that a 23-ft Class C fails. A
  "RVs under 10 years old" rule is a note line.
- **The note:** never repeat what a structured field shows. That rules out price, RV Life stars/$,
  phone, website, hookups and min stay. Keep what no field can say: what the park mostly is ("Mostly
  seasonal: ..."), 55+, a peak-season long-stay rule, a dead-domain caveat, oddities. One or two
  sentences, ending ` --Claude`. Still put the RV Life star/$ figures in `rvlife` (below), not in the note.
- **Waterfront:** run the real audit; don't return a placeholder. Apply the curation doc's
  waterfront gate:
  - Default down, and earn any value.
  - The satellite look is mandatory, and it can only veto.
  - A name, marketing prose or a boat ramp is never the basis.
  - Use the open-apron and distance rules, and below-a-dam-berm is not on the lake.
  - Lake Erie and the Gulf beaches are big water. The coastal dunes/woods types apply only where the
    doc allows.
  - Check that every image Read actually rendered pixels ([[feedback_verify_image_reads]]). Never write
    satellite evidence from a read with no image.
- **Privacy:** never write a distance to a family home, a family name or an address anywhere. The only
  wording allowed is "within 40 km of a family home (gateways.py)". Never put any personal identifier
  in a User-Agent or any request.
- **Browser:** one headless browser at a time. Run every browser command under
  `flock /tmp/ekko-headless-browser.lock <cmd>`, and start `drv_server.py` in the background with
  `flock -o`. Never probe its socket with a bare connect. Quit the driver when done.
- Edit no repo file except your own result file. Run Python with `-I` on anything downloaded.
  Put scratch files in the scratch dir named in your prompt.

## Result file
Write `audit/family_rescreen_2026-10-21/results/<slug>.json`: ONE JSON object.
```
{"decision": "add" | "skip", "kind_of_no": "<short, if skip>", "why": "<one line with source + date, if skip>",
 "name": "<published name>", "state": "XX", "location": "lat,lng", "elevation_meters": <num>,
 "ownership": "private", "website": "<operator page>\n<booking deep link>", "phone": "xxx-xxx-xxxx",
 "note": "...", "inclusion_evidence": "<one line: source + what it showed + 'price gate lifted: within 40 km of a family home (gateways.py)'>",
 "waterfront": "<value>", "waterfront_evidence": "<the audit proof, dated>",
 "fees": {"nightly_low": <num>, "nightly_high": <num or omit>, "currency": "USD", "checked": "2026"},
 "fees_source": "<url + what was quoted (dates, rig) + read date>",
 "booking": {"min_stay": [...]} (only if a standing rule exists), "booking_source": "<url, if booking given>",
 "rvlife": "<stars>*/<$ signs>", "flags": ["<anything AWH should see>"]}
```
For a skip, only decision, kind_of_no, why, name and state are required. Reply with one line:
the decision and the reason.
