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

## Status (2026-10-08)

- QC: DONE. 72 of 72 settled: 39 adds appended as ids 15126-15164, 33 skips.
- ON: 49 of 50 settled: 7 adds appended as ids 15165-15171 (Lakefield Campground is a
  Township of Selwyn park - added as `local`), 42 skips. Open: #12 Paradise Valley (Killam
  Leisure Living; its sites answer HTTP 429 - back off and retry; a third-party listing says
  69 overnight sites of ~350 and Killam's Family Paradise sold overnight hydro/water at C$69 in
  RMS but was ~5% traveller). Build file: `build_on_results.py`, calls `on_wf_calls.jsonl`.
- BC (36): not started. Next append `--min-id 15172` (check the max id first).
- Engines met in ON: CampLife (`../private_gap_browser/camplife.py`), Campspot
  (`campspot.py`, or the /book/<slug>/search/<in>/<out>/guests0,2,0/list view for parks not on
  the marketplace), RMS (Killam parks: `rms.sh <hash-id>` works with the hash in the link),
  PitchCamp (click the calendar), Let's Camp, ResNexus, Cloudbeds, Checkfront.

## The add batch (how QC's was built - copy it per province)

1. For each record in `adds_work.json`: fetch `satz.py LAT LNG 17` at the Google pin (or the
   record's `pin_hint`), find the loops, and pin them with
   `../private_gap_browser/satpx.py LAT LNG Z X Y` (pixel in that frame -> lat,lng; the
   crosshair is not at the frame centre). Zoom to 18 on the water edge and read the operator's
   per-site map before the waterfront call; evidence string ends with the verdict, default down.
   Calls go one per line into `qc_wf_calls.jsonl` (`key` = work-list name, `pin`, `waterfront`,
   `wf`), then elevations from Open-Meteo in one batched call (a shoreline pin can read 0 m on
   a sea cell - take the nearest land cell).
2. `build_qc_results.py` holds the hand-written note and inclusion line per add and writes
   `audit/qc_private/results_norate.json`; it drops Bonjour Québec URLs from `website`.
3. `python3 append_state.py --state QC --min-id <next> audit/qc_private/results_norate.json`,
   then `python3 audit/canada_no_rate/build_qc_results.py --wf` (maps the new ids) and
   `python3 audit/apply_waterfront_audit.py audit/qc_private/waterfront_norate_results.json`.
4. Update `audit/private_gap_decisions.json` states.<ST> (`no_rate_followup`), the memory
   files, and commit.

Waterfront judgment used in QC (not AWH-confirmed): judge the sites a traveller can book
(a seasonal-only shore row doesn't make the park lakefront); a lane, swimming beach or
car-free road between pads and water = view; canopy hiding a stream -> the per-site plan
decides; a continuous riparian treeline = not waterfront.
