# Short fee fix-up pass (AWH 2026-11-07)

You research a handful of campground fee records and write PROPOSALS to a JSON file. You never
edit /home/andrew/Dev/campgrounds/campgrounds.json or any repo file; the parent applies your file.

## Read first
- /home/andrew/Dev/campgrounds/campground_schema.py: the `fees` group (every key, its type and
  enum, the comments above `all_in`, `prereq_pass`, `entrance`, `extra_person`, `extra_vehicle`).
- /home/andrew/Dev/campgrounds/docs/campground-schema.md §4.2 (fees modelling: the base is 2 adults,
  1 night, the cheapest RV-usable site; permits; per-person; per-vehicle; extra_vehicle backfill rules).
- Validate every proposed fees block you write: `cd /home/andrew/Dev/campgrounds && python3 -I -c
  "import campground_schema as cs, json; cs.validate_row({'fees': json.load(open('X'))})"` or similar.

## Rules
- Use the operator / agency's OWN current page or booking channel (recreation.gov for federal).
  Aggregators, RoverPass/Campendium tables and camper reports do not count. Note the date read.
- Absent = unknown: never fill a placeholder, never guess. If you can't confirm, say so and propose nothing.
- An `entrance` is what EVERY camper pays to get in (a lone motorhome too). If the site fee already
  includes one vehicle's entry, it is NOT `entrance`; it is `extra_vehicle {included: 1, amount: <entry>}`.
  If campers are exempt from the day-use fee, propose no `entrance` and say so.
- If an entrance/pass is the ONLY charge and is per vehicle (no separate camping fee), model it
  like its siblings 9981/10119/11419: `all_in: true`, nightly = what one night costs, plus
  `prereq_pass` (required permit) or `entrance`, as the schema doc describes.
- Price gate: a PRIVATE campground whose cheapest real RV night is over US$50 / C$69 before tax:
  report it in `flag` (don't propose dropping).
- Notes name no one (no first person, no family). `fees.note` is dated prose about the fee research;
  you may propose a replacement `fees_note` (keep the facts in the old one that are still true).
- The entry `note` is deletion-only: if it repeats a fact your fields now hold, propose a cleaned
  `note` that only deletes words (joining words and, a, the, with, or, of, to, in, on, for, at, is,
  are, has, have, its, it, site, sites may be added). Keep every `--AWH` passage unless the
  fact it states is now in a field (then say so in `awh_dropped`). Omit `note` if unchanged.

## Output: a JSON array, one row per entry you looked at
{"id": 278,
 "set": {"entrance": {...}},            // fees keys to SET (whole value replaces the key)
 "remove": ["nightly_high"],            // fees keys to DELETE (optional)
 "fees_note": "...",                    // replacement fees.note (optional)
 "note": "...",                         // cleaned entry note (optional, deletion only)
 "awh_dropped": "...",                  // optional
 "sources": ["https://... (read 2026-11-07)"],
 "summary": "one line: what you found",
 "flag": "anything AWH should know (optional)"}
A row with no `set`/`remove`/`fees_note`/`note` is a "confirmed nothing to change" or "couldn't
confirm" row; still write it with a summary.

Final report: short; per id one line, plus every flag.
