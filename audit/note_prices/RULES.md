# Note-price cleanup: rules for the read-through (AWH 2026-11-07)

AWH: "remove the extra person charge info from the note wherever this has been recorded in the new
field ... remove the base price if it has been recorded in the price field. This includes --AWH notes
too." The structured `fees` group is the record and the popup shows it as chips; a note that repeats
it goes stale (Low Water Bridge 12: an --AWH "$50/night" beside the 2026 rate page's $35-60).

Each input item gives the entry's `note` and the `fees` it RESOLVES to (its own values plus any
agency registry row): `nightly_low`, `nightly_high`, `currency`, `extra_person`, and the fee source
and date, so you can tell which is newer.

## Remove
1. **The nightly site rate, in any form**, whenever `nightly_low` or `nightly_high` is present:
   "$20/night", "$35-45 a night plus tax", "C$55-65", "from $35 (2026)", "$20 single/$40 double",
   rates by site type ("$35 non-electric, $45 electric", "Electric +$10", "full hookups $5 more"),
   weekday/weekend/holiday/seasonal versions of the nightly rate, resident/non-resident nightly
   rates, "fees vary by site", an aggregator's average nightly rate ("RV Life (C$45 avg)", "Campendium
   ~$30"), and the words "free" / "no fee" / "no charge" about camping when `nightly_low` is 0.
   **Remove it even when the note's figure differs from the field** - the field is the record and
   the note's figure is the stale one.
2. **The extra-person charge**, whenever `extra_person` is present: "additional adult +$12",
   "$5 per extra person", and the occupancy the rate covers that goes with it ("2 adults",
   "for up to 4 people", "rates cover 2 adults and 2 children").

## Keep (do not touch)
- A **CAMPER-REPORTED RATE** sentence (AWH asked that a camper-reported rate stay in the note,
  labelled, with its month): leave it whole.
- Prices no field holds: weekly / monthly / seasonal-lease rates, cabin / yurt / lodge / tent-only
  rates, entrance, day-use, parking, permit and pass fees (incl. the Virginia DWR camping
  authorization + access-permit explanation), dump, shower, boat-launch, pet and deposit charges,
  reservation fees, discounts.
- A sentence explaining why a park stays despite its price (gateway, family, Good Sam): keep the
  reason; it may lose only the figure.
- A non-price fact inside a price sentence (a rig length that fits, a site count, a season): keep
  it, rebuilt from the sentence's own words (e.g. "Sites under 20 ft base rate, +$6 for longer (23 ft
  fine)" -> "Longer sites (23 ft fine).").
- Which sites or which season a rate applies to, when the fields can't say it: "Loop 4 primitive is
  free FCFS in the off-season" stays whole (the field holds one range, not the season split).
- Everything that is not a price: FCFS wording, hookups, site counts, setting, rules, caveats, dates.
  Do not fix anything else, do not reword, do not tidy other facts.
- **Exception - the note is newer:** if the note's price is clearly dated LATER than the fee
  source/checked date (e.g. note "2027 rates $48", fee source read 2025), leave the note unchanged
  and output a `flag` saying so.

## How to edit
- **Deletion only.** Cut the price words and repair the grammar at the cut using punctuation and,
  at most, joining words (and, a, the, with, or, of, to, in, on, for, at, its, is, are, has, also,
  site/sites). Never add any other word; the landing check refuses an edit that does. Capitalise the
  first word of a sentence if a cut leaves it lowercase.
- Keep `--AWH` and `--Claude` markers and the two-space gap between sentences. Do not add a
  signature. If a signed segment is left with nothing but its marker, drop the marker too, and for
  an `--AWH` one record it in `awh_dropped` ([{"old": "<AWH's removed text>", "why": "fees.nightly_low ..."}]).
  If nothing remains of the whole note, output `"note": ""`.
- Unsure whether something is the nightly rate? Leave it and add a `flag`.

## Output
A JSON list in the output file named in your task, holding ONLY entries you changed or flagged:
`{"id": N, "note": "<the whole cleaned note>", "awh_dropped": [...], "flag": "..."}`
(`awh_dropped` / `flag` only when needed; a flagged-but-unchanged entry omits `note`).
Then run `python3 -I audit/note_prices/check.py <output file>` and fix every line it reports.
