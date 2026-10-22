# Phase-7 leads: agent instructions

Phase-7 verifiers sometimes find a real campground with no entry (a neighbour on the same booking
facility, a park an entry had been mixed up with). AWH: vet new leads myself and add them under the
curation doc ([[feedback_vet_new_leads_myself]]). Your job is to vet ONE lead as a normal new add,
applying every gate, and write one result file.

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
- **Price (private parks only):** read the current rate from the operator's own site or its booking
  engine, dated 2024 or later: the cheapest site a 23-ft motorhome fits, base rate before tax, weeknight
  in season, plus any mandatory per-night resort or grounds fee ([[feedback_mandatory_fees_count]]).
  Return it as `fees`. Over US$50 is a skip ("price") UNLESS `python3 audit/price_research/gateways.py
  lat,lng` finds a gateway within 40 km - then add, and say which gateway in inclusion_evidence. A
  private park needs a price indicator (posted rate, booking engine or RV Life $/$$) and a presence
  indicator (working website with a phone, or Google Maps open with 25+ reviews and a phone).
  Public (local/state/federal) campgrounds have no price gate and no presence rule; still record the
  agency's fee.
- **Long-stay tests 2-5** (curation doc) apply in full:
  - Nights must really be for sale, with no application, lease or waitlist.
  - Skip a park with a standing minimum over 2 nights outside holiday weekends.
  - At least 1 site in 10 must be sold by the night where a count exists.
  - Skip a park that sells homes or lots, or whose homes outnumber its RV sites. A 55+ community that
    advertises "units for sale" with a resident application is a skip ([[feedback-exclude-seasonal-residential]]).
  - **The peak-season exception (AWH 2026-10-21):** a long-stay rule (e.g. monthly-only Dec-Mar) is OK
    only if it applies to peak season alone, lasts no more than 3 months, and the note says so. Longer
    than 3 months fails test 3.
  - A standing 2-night minimum is fine. Return it in `booking.min_stay`, in the doc §4.1 shape
    (`applies` is only `always` | `weekend` | `holiday` | `summer`), with anything that vocabulary
    can't hold (dates, a phone waiver) in `booking.note`.
  - A long minimum that applies only part of the year, or that can be avoided by calling ahead or
    walking up, is not a drop (AWH 2026-10-19). Record it and flag it.
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
- **Browser:** the helpers need `PYTHONPATH=~/.cache/ekko-pw` (Playwright lives there). One headless browser at a time. Run every browser command under
  `flock /tmp/ekko-headless-browser.lock <cmd>`, and start `drv_server.py` in the background with
  `flock -o`. Never probe its socket with a bare connect. Quit the driver when done.
- Edit no repo file except your own result file. Run Python with `-I` on anything downloaded.
  Put scratch files in the scratch dir named in your prompt.

## Result file
Write `audit/verify/leads/results/<slug>.json`: ONE JSON object.
```
{"decision": "add" | "skip", "kind_of_no": "<short, if skip>", "why": "<one line with source + date, if skip>",
 "name": "<published name>", "state": "XX", "location": "lat,lng", "elevation_meters": <num>,
 "ownership": "private|local|state|federal", "website": "<operator page>\n<booking deep link>", "phone": "xxx-xxx-xxxx",
 "note": "...", "inclusion_evidence": "<one line: source + what it showed + the price-gate outcome for a private park>",
 "waterfront": "<value>", "waterfront_evidence": "<the audit proof, dated>",
 "fees": {"nightly_low": <num>, "nightly_high": <num or omit>, "currency": "USD", "checked": "2026"},
 "fees_source": "<url + what was quoted (dates, rig) + read date>",
 "booking": {"min_stay": [...]} (only if a standing rule exists), "booking_source": "<url, if booking given>",
 "rvlife": "<stars>*/<$ signs>", "flags": ["<anything AWH should see>"]}
```
For a skip, only decision, kind_of_no, why, name and state are required. Reply with one line:
the decision and the reason.
