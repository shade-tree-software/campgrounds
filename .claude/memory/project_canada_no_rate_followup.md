---
name: project-canada-no-rate-followup
description: PLANNED (not started) 2026-10-08 - recover the 157 Canada private-gap parks skipped as no_rate by quoting them through their own booking pages; pilot QC first
metadata:
  type: project
---

**Status: planned 2026-10-08, AWH approved the plan, to be run in a later session. Nothing done yet.**

The Canada private gap ([[project-private-gap]]) skipped 157 well-rated private parks as `kind_of_no: "no_rate"`: QC 72, ON 50, BC 36. They passed the quality screen, but no nightly rate was found while the RV Life tier was over C$55.5 or unrated. A published rate is required for those (see the gate in [[project-private-gap]]).

**Correction to the earlier explanation:** I first said their rates "sit behind booking-engine date pickers". A check of the saved crawl text (`audit/{qc,on,bc}_private/txt/<SquashedName>.txt`, sites in `sites.tsv` keyed by the squashed name) did not support that:
- 123 have no booking-engine link in the text.
- 14 have a generic `book.` subdomain, mostly QC.
- 16 have no website on file.
- 5 use Cloudbeds, Let's Camp, rvpark.com or Camping Québec.

The crawl is static text, so a booking form loaded by script is invisible to it. Some of the 123 will have online booking; others are likely "call for rates" with no online booking at all.

**Plan:**
1. **Pilot, QC first.** Take 10–15 parks. Open each in the headless browser (one browser at a time, [[feedback-limit-headless-browsers]]) and follow its Reserve/Réserver button. Quote the cheapest hookup RV site for a peak weeknight, e.g. a Tuesday in mid-July, pre-tax. Record one of: the quote plus the URL it came from, or `no online booking`.
2. **Report the pilot hit rate to AWH** before doing all 157.
3. **If it's worth it,** go one province at a time (QC, ON, BC). Each province is its own commit. Use the normal pipeline: append_state with `--min-id` from the current max+1 (15126 at planning time), then apply_waterfront_audit. Update that province's verdicts.jsonl entry and `states.XX` in `audit/private_gap_decisions.json`.

**Rules:**
- A quote counts only from the park's own site or its booking engine, never from a directory or aggregator copy ([[feedback-note-rate-sourcing]]).
- Same gate as the sweep: C$69 or less passes the US$40–50 tier, and any published rate over C$69 skips.
- No holds ([[feedback-canada-no-holds]]). A booking page that won't load is a skip, unless it's a permanent human-only captcha.
- Skip if the engine shows a 2+ night minimum on that weeknight ([[feedback-minimum-stay]]).
- Mostly-seasonal skips still apply.
- **Why:** these are the largest pool of plausible adds left in Canada.
- **How to apply:** start with the pilot, not the full list; don't re-derive the counts above.
