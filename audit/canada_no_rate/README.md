# Canada private-gap "no_rate" follow-up

The 2026-10-07/08 Canada private gap skipped 158 well-rated private parks as
`kind_of_no: "no_rate"` (QC 72, ON 50, BC 36): they passed the quality screen but no nightly
rate was found while their RV Life tier was over C$55.5 or missing, and the Canada gate needs
a published rate of C$69 or less (US$50). This folder works through them again with a real
browser: rate pages the static crawl couldn't read, booking engines, archived rate tables and
the official Bonjour Québec listing. AWH's instruction (2026-10-08): a genuine posted rate, or
one obtained by working through the booking engine, is wanted; a park that posts no rate and
books only by phone is a skip.

## Files

- `build.py` -> `worklist.json`: the 158 rows with everything the original sweep knew (RV
  Life / Good Sam row, Google line from gm.py, site URL, the original "why"). Membership is
  decided on the ORIGINAL verdict rows only, so row numbers never shift; each row also carries
  its latest follow-up verdict (`followup`). Re-run after appending verdicts.
- `info.py ST N [N...]` - show rows by per-province index; `info.py ST todo` - the open rows.
- `adds_work.json` - one record per follow-up ADD, keyed by the work-list name: display name
  (current operator name), Google coords, phone, website lines, the rate statement, facts for
  the note, quality line, site-map URLs, the water body to check, and any pin hint or caveat.
  This is the input for the add batch (below). Not yet in campgrounds.json.
- Tools: `../private_gap_browser/` (drv_server.py / drv.py driver, scan.py, rpa.sh,
  rc1night.sh, rpro.py, rms.sh, wb.py, bqread.py, v.py) - see its README, which also holds the
  rate-finding and seasonal-share playbooks.

## Recording a verdict

    python3 audit/private_gap_browser/v.py qc_private '{"name": "<exact work-list name>", "decision": "add"|"skip",
      "kind_of_no": "...", "base_rate": 57, "currency": "CAD", "rate_source": "<URL + what it said + date>",
      "why": "no_rate follow-up: ...", "followup": "no_rate 2026-10-08"[, "add_as": "<current name>"]}'

The latest row per name wins, so a revised call is just another row (Bellerive was added,
then reversed to a price skip the same day). `followup` marks the row as this pass's.
kind_of_no values used: price, mostly seasonal, not nightly (2-night minimum),
no published rate / phone only, no readable web presence, restricted admission (men only),
no RV sites (pods only), duplicate, no clear rate / phone only, no published rate.

## Status (2026-10-08, paused by AWH)

- QC: 58 of 72 settled - 30 adds, 28 skips (`info.py QC todo` lists the 14 open: #53
  Sainte-Madeleine onward; #64 Parc de la Chaudière is a Camping Union park - same grid and
  Nuitée Express as La Demi-Lieue and du Gouffre; #63 Parc-Estrie is Parkbridge - count its
  map like Domaine des Érables).
- ON (50) and BC (36): not started. ON's original sweep pre-skipped Parkbridge resorts as a
  "seasonal chain"; Domaine des Érables (QC) showed a Parkbridge park can be ~20% traveller, so
  any Parkbridge park that is on the no_rate list should be measured, not brand-skipped.
- Nothing appended to campgrounds.json yet.

## Next: the QC add batch

For each record in `adds_work.json` (st == QC), following docs/campground-curation.md:
1. Pin `location` on the campground loops (satellite; several records carry a `pin_hint`;
   Google's pin is often the reception at the road).
2. `elevation_meters` from Open-Meteo at the pin.
3. Waterfront call from satellite + the operator map (`maps`, `water`); evidence string ends
   with the verdict; default down.
4. Note (current name, site mix incl. the seasonal share, rate statement with its source and
   year, booking channel and minimums, season; caveats such as Libby's unconfirmed weekday
   minimum or Baie du Diable's phone-only 2024 rates) + `--Claude`; RV Life tail only for
   RV-Life-rated rows; `inclusion_evidence` one line; ownership `private`.
5. Write `audit/qc_private/results_norate.json` + waterfront results, then
   `python3 append_state.py --state QC --min-id 15126 audit/qc_private/results_norate.json`
   (check the max id first) and `python3 audit/apply_waterfront_audit.py <waterfront results>`.
6. Update `audit/private_gap_decisions.json` states.QC, commit. Then ON, then BC.
