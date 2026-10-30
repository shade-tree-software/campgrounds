# Florida Keys price re-screen (AWH 2026-10-30): agent instructions

AWH 2026-10-30: "Campgrounds on the keys that pass all other criteria can be kept even if the price is too
high." The whole island chain, Key Largo to Key West, is now a price-gate zone in
`audit/price_research/gateways.py` (reported as "Florida Keys (zone, 0 km)"). Almost no Keys park was ever
researched: the Florida private sweep screened only RV Life `$`/`$$` parks, and nearly every Keys park is
`$$$`+. None of the candidates here is in the database. Your job is to vet ONE candidate as a normal new add,
applying every gate except price, and write one result file.

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
- **Privacy:** never write a family name, an address or a distance to a family home anywhere. Never put any
  personal identifier in a User-Agent or any request (use "Mozilla/5.0").
- **Browser:** the helpers need `PYTHONPATH=~/.cache/ekko-pw` (Playwright lives there). One headless browser at a time. Run every browser command under
  `flock /tmp/ekko-headless-browser.lock <cmd>`, and start `drv_server.py` in the background with
  `flock -o`. Never probe its socket with a bare connect. Quit the driver when done.
- Edit no repo file except your own result file. Run Python with `-I` on anything downloaded.
  Put scratch files in the scratch dir named in your prompt.

## Keys-specific rules
- **Google reviews (AWH 2026-10-30):** give the park's Google Maps rating and review count in `google`
  ("4.6/812"). A markedly poor rating (AWH dropped a park for "very poor Google reviews") is a flag with
  what the reviews complain of; say what you would decide.
- **Owner-lot (condo) RV resorts (AWH 2026-10-30):** "Florida Keys owner lot resorts that rent spots by the
  night are ok if they have a normal booking site which works like a regular nightly campground and they
  meet all other criteria (except price)." Good Sam types Key Largo Kampground, Calusa, Venture Out and
  Bluewater Key as `CONDO_PARK`; others may be the same. For one of these, test 5's "sells lots" does not
  fail it. It is an add when the resort (or its association / rental manager) sells nights on a normal
  booking site that works like a regular nightly campground: pick dates, pick a site, pay, with no
  application, owner approval or lease. Every other rule still applies, including 1 site in 10 sold
  nightly and the minimum-stay rules. Nights sold only by individual owners (VRBO/Airbnb/by contacting the
  owner), or only by phone/email inquiry, or no rental program at all, is a skip. Put in the note what it
  mostly is (e.g. "Owner-lot condo resort: about 38 of its 171 lots are rented by the night."), and in
  `flags` the rental-program lot count and who runs the booking site.
- **Seasonal minimums are common in the Keys** (for example 3+ nights from Christmas to Easter, or a
  monthly-only winter). Apply the minimum and peak-season rules above exactly, give the dates, and flag it.
- **Hurricane damage:** Irma (2017) and Ian (2022) closed many Keys parks for years. If a park looks closed,
  check whether it is closed for good, rebuilding (give the reopening date if one is published), or has
  reopened. A real campground that is temporarily closed is an add with the caveat dated in the note
  ([[feedback_add_with_caveat_not_withhold]]), not a skip. RV Life's `closed` flag is a lead, not proof.
- **Brand and membership skips still apply:** Sun Outdoors / Sun RV Resorts (including a park Sun bought
  under its old name), Thousand Trails / Encore / Bluegreen / Coast to Coast, lodges, and military-only
  parks are skips. A marina's transient boat slips are not RV sites: count only drive-in RV sites.
- **Long Key State Park** is state-owned (no price gate at all). Its campground closed after Irma; find
  whether it has reopened to RVs. If it is open or reopening, return it as an add with `ownership: "state"`
  and the Florida State Parks booking link; leave `rvlife`/`google` as for any entry.
- **Canals and marina channels are not the bay.** Keys parks are laced with dredged canals and boat
  basins. A site on a canal, boat basin or marina channel is not `bayfront`/`oceanfront` just because the
  channel reaches open water; say plainly in the evidence whether the sites face open bay/ocean or a
  canal/channel, and judge a canal as the narrow water it is under the curation doc's gate (default down):
  by the size rule a canal of roughly 30 m+ open water at the sites is `riverfront` (Lakeport 14424), a
  narrower one `creekside`. A marina basin that opens onto the bay within a few tens of metres, with the bay
  in view, is bay water (`bayfront`).
- Add `"google": "<rating>/<count>"` to the result record below.

## Result file
Write `audit/keys_rescreen_2026-10-30/results/<slug>.json`: ONE JSON object.
```
{"decision": "add" | "skip", "kind_of_no": "<short, if skip>", "why": "<one line with source + date, if skip>",
 "name": "<published name>", "state": "XX", "location": "lat,lng", "elevation_meters": <num>,
 "ownership": "private", "website": "<operator page>\n<booking deep link>", "phone": "xxx-xxx-xxxx",
 "note": "...", "inclusion_evidence": "<one line: source + what it showed + 'price gate lifted: Florida Keys zone (AWH 2026-10-30, gateways.py)'>",
 "waterfront": "<value>", "waterfront_evidence": "<the audit proof, dated>",
 "fees": {"nightly_low": <num>, "nightly_high": <num or omit>, "currency": "USD", "checked": "2026"},
 "fees_source": "<url + what was quoted (dates, rig) + read date>",
 "booking": {"min_stay": [...]} (only if a standing rule exists), "booking_source": "<url, if booking given>",
 "rvlife": "<stars>*/<$ signs>", "google": "<rating>/<count>", "flags": ["<anything AWH should see>"]}
```
For a skip, only decision, kind_of_no, why, name and state are required. Reply with one line:
the decision and the reason.
