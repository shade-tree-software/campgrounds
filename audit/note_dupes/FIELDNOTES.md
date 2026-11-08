# Note read-through, round 2: a note that repeats a group's own note (AWH 2026-11-08)

AWH: Pohick Bay "is an example of a campground for which the note contains way too much
information that is duplicated in the fields" — its note spelled out the minimum stays by
site type that `booking.note` already holds in full. The map popup now draws the
`season`, `booking`, `fees` and `sites` notes under their rows (the last three folded to
one line, a tap opens them), so a note sentence one of them already says is a second copy
that goes stale on its own.

**Read `RULES.md` in this folder first: every rule there still applies** (deletion only,
attribution markers, --AWH handling, bookkeeping to `curation`, readability, the calls
settled in chunks 001-014). This file adds one thing.

## Input
As in RULES.md, plus `field_notes`: each popup-drawn group's own note, by row label
(`"Booking": "..."`, `"Fees": "..."`, `"Sites": "..."`, `"Season": "..."`). A fact a
`field_notes` text states is SHOWN, exactly as a `shown` chip is.

## Cut from the note (no curation)
Wording that states only what a `field_notes` text (or a `shown` chip) already states, **at
least as specifically**: minimum stays, stay limits, fee tables and surcharges, site counts
and types, pad lengths, booking channels and phone lines for booking, gate hours, season
dates and which loops stay open.
- **Same fact only.** The note must lose nothing a camper would miss. "Sites 5, 6, 8 and
  12 are waterfront" stays beside a fee note that prices "the lakeside sites 5, 6, 8 and
  12": the fee note says what they cost, not that they are on the water. A note sentence
  with a detail the field note lacks stays whole, or loses only the part fully covered.
- **The field note must be at least as current.** If the note's version is dated later
  than the field note's, or the two disagree, cut nothing and add an `ask`: "note
  contradicts <Group> note: <a few words>".
- Description, setting, water, scenery, road access, what a loop is like, a dated closure
  or outage, a camper report: never a repeat of a booking/fee/site/season fact. Keep it.
- `field_notes` is reference only. Never edit it, never copy words from it.

## Output
`fn_out/NNN.json`, rows as in RULES.md (`id`, `was`, `note`, optional `curation`,
`awh_dropped`, `ask`), only for items you change or ask about. An ask-only row keeps
`note` equal to `was`.

## Settled in chunk 001
- **A caveat that qualifies a sentence left in the note stays**, even when a field note
  repeats it: "DWR bars camping within 300 ft of a lake" stays beside "parking areas,
  including one on the lake", which would otherwise read as a lakeside camp spot (236).
- "Recommended by Grok ..." --AWH openers go to `curation` (AWH answered for 15/17); other
  recommendation/sourcing lines in --AWH text are still an `ask`.
- A "CAMPER-REPORTED RATE: ..." sentence is a fee fact like any other: cut it when the Fees
  note gives the same report (same amount, month and source) at least as fully (chunks 003-005
  did; 006 kept them, which is also safe).
