# Extra-vehicle pass (AWH 2026-11-07)

AWH asked for a per-vehicle fee field; it is `fees.extra_vehicle` (schema: `campground_schema.py`,
the comment above it; doc: `docs/campground-schema.md`, the paragraph starting "**Vehicles past the
ones the site fee covers**"). This pass reads each entry's `note` and `fees_note`, fills
`extra_vehicle` where they state it, and deletes the copy of that fact from the `note`.

## The field

`{"included": INT, "amount": NUM, "per": "night"|"stay", "max_vehicles": INT}`, every key optional.
Absent means unknown: set only what the text states. Never guess `included`.

| Text says | Write |
|---|---|
| "One vehicle included; $8 per extra vehicle per night" | `{"included": 1, "amount": 8, "per": "night"}` |
| "extra vehicle $5" (no unit) | `{"amount": 5}` |
| "$5/day per additional vehicle" | `{"amount": 5, "per": "night"}` (a day charge on a camping stay = per night) |
| "$10 per extra vehicle per stay" | `{"amount": 10, "per": "stay"}` |
| "Up to 8 people and 2 vehicles" | `{"max_vehicles": 2}` (the people cap is not this field; leave it) |
| "2 vehicles per site, extra $7" | `{"included": 2, "amount": 7}` only if the text says the 2 are covered by the fee; otherwise `{"max_vehicles": 2, "amount": 7}` is wrong too (a cap and an extra charge contradict): flag it |
| "extra vehicle free" / "second vehicle no charge" | `{"amount": 0}` (+ `included` if stated) |
| The SITE fee itself is per vehicle: "$8 per vehicle per night" as the camping fee, "$15 per vehicle" | `{"included": 1, "amount": <that per-vehicle figure>, "per": "night"}`: a lone motorhome pays the base, a second vehicle pays it again. If the figure is a range, use the low end. |
| "towed vehicles free" / "RV plus tow car" | `{"included": 2}` only if it clearly says the rate covers the RV and one more vehicle; else skip |

NOT this field, never write it for these:
- park entrance / day-use / vehicle permit / parking pass charged per vehicle (state park entry
  "$5 per vehicle", Kansas "vehicle permit $7 a day", "Park entrance fee is separate: $35 per
  vehicle"). That is `entrance` (already structured, or flag it if `fees` lacks it).
- boat trailers, extra tents, pets, horses.
- a vehicle LENGTH limit.
- a group site's vehicle rules.
- anything for cabins, tent-only sites or day use.

If `fees.inherited_from_agency` already covers the matter, or the text is the agency's statewide
schedule, do not write an entry-level value: flag it ("agency-wide: <agency>") so the registry row
gets it once.

When the note and `fees_note` disagree, `fees_note` wins (it is the dated fee research); flag it.
A dated fee (`fees_note` "Read 2026-..") outranks an undated note figure.

## The note edit

Once the field holds the fact, delete the extra-vehicle / vehicles-per-site wording from `note`
(not from `fees_note`, which you never edit). Deletion only, same as the note-price cleanup
(`audit/note_prices/RULES.md` "How to edit"): the new note may add no word the old one lacked
except joining words (and, a, the, with, or, of, to, in, on, for, at, is, are, has, have, its, it,
site, sites). No bare fragments; keep any other fact that sat in the same sentence; keep `--AWH`
text unless the fact it states is now in the field (then list it in `awh_dropped`). If the note
says nothing about vehicles (the fact was only in `fees_note`), omit `note` from the row.

## Output row

```json
{"id": 2332, "extra_vehicle": {"included": 1, "amount": 8, "per": "night"},
 "evidence": "One vehicle included; $8 per extra vehicle per night.", "from": "fees_note",
 "note": "<cleaned note, only if you changed it>", "awh_dropped": "<only if>", "flag": "<only if>"}
```

`evidence` is an exact substring of `note` or `fees_note` (whichever `from` names) that states the
value. A row may be a flag only (no `extra_vehicle`). List only entries you write or flag.
