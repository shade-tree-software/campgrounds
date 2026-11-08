# Note read-through: drop what the fields show, move bookkeeping out (AWH 2026-11-07)

AWH: notes that "say something that should be conveyed in the fields" are unnecessary —
"RV Life listed but unrated $ (auto 6/2026). --Claude  FCFS, no advance online booking.
--Claude" (Little Fort), "First-come, first-served (no reservations)." (Laurel Fork),
"RV Life 4.5*, $$$$." (a KOA). And "Corrected 2026-10-01 against the operator page
(staff-collection and year-round claims removed); the $40 dump fee is sourced to a Google
review and the owner's reply, found by AWH. --Claude" is true but "not information that
users need to know. It is more for our own bookkeeping" — it belongs in a hidden field.

The exact template shapes were already cut by script (rvlife.py, fcfs.py). What is left
needs reading.

## Input
Each item: `id`, `name`, `note`, and `shown` — the chips the map popup ALREADY draws for
this entry from its own fields, grouped by row label (e.g. `"Booking": ["not reservable",
"FCFS"]`, `"Rating": ["4.5★", "$$"]`, `"Hookups": ["none"]`). `shown` is the only
reference for what is "conveyed in the fields". If a fact is not in `shown`, it is not
shown, whatever the note says.

## Output
Write a JSON array to the output path you are given: one row per item you CHANGE (leave
unchanged items out):
`{"id": N, "was": <the input note, exactly>, "note": <cleaned note>, "curation": <text moved
out, optional>, "awh_dropped": true (only if an --AWH segment is emptied), "ask": <optional
question for AWH>}`.

Every edit is **deletion only**. The cleaned note may not contain any word the old note
lacked (beyond joining words like and/the/with/of, and capitalising a letter), and
`curation` may contain only words that left the note. A tool refuses anything else. You
may cut a clause, a sentence, a parenthetical, or a few words inside a sentence, and fix
the punctuation and capital letter around the cut so it still reads as English.

## Remove from the note (no curation)
1. **Wording that says only what a `shown` chip says.**
   - Booking: "first-come, first-served", "FCFS", "no reservations", "not reservable",
     "walk-up only" when `shown.Booking` has "FCFS" / "not reservable". Keep what else the
     sentence says: "FCFS; pay at the honor box" → "Pay at the honor box."; "FCFS only, a
     few RV sites" → "Only a few RV sites." (if that reads; otherwise keep the words that
     carry the other fact). "Reservable online" does NOT go — the popup shows no chip for
     reservable.
   - Rating: an RV Life star rating / $ tier the `Rating` chips already show ("RV Life 4*/$$",
     "RV Life unrated $" when Rating has "$" and no ★). Keep RV Life remarks that are about
     something else ("RV Life tags it county but it is city-owned" is bookkeeping, see
     below; "listed on RV Life/Campendium" stays).
   - Any other fact a chip states exactly: max stay ("14-day limit" beside "max stay 14
     nights"), hookups ("no hookups" beside Hookups "none"), a season ("open May-Oct" beside
     "open May 1 – Oct 31" ONLY if the chip is at least as specific), a rate or fee shown in
     Fees. **Same fact only**: "92 sites have E/W hookups" stays even if Hookups shows
     "water" (the count is not shown); "sites to 30 ft" stays unless Sites shows that length.
2. **An "(auto M/YYYY)" stamp** left over anywhere.

## Move to `curation` (cut from the note, copied VERBATIM, word for word)
Statements about the RECORD rather than the campground — who checked what, when, against
which source, what was corrected or removed, why an entry was kept:
- correction / audit histories: "Corrected 2026-10-01 against the operator page (... removed)",
  "Waterfront-audited 2026-06-18: lakefront confirmed via ...", "Rechecked 2026-10-01: ...",
  "Pin moved onto the camping loops.", "PIN APPROXIMATE (RV Life geo) - verify."
- sourcing and attribution of the record: "found by AWH", "per AWH", "kept as an exception
  ... per AWH", "the $40 dump fee is sourced to a Google review and the owner's reply",
  "Phone not verified - omitted.", "RV Life tags it county but it is city-owned.",
  "Satellite cloud-covered at pin.", "Priced above the sweep's usual private gate.",
  "General campground (offers a horse loop)." (an inclusion justification).
- Keep the attribution marker (`--Claude`) on the moved text in `curation` when the moved text
  was a whole marked segment.

**Keep in the note** facts a camper uses, even when they carry a date or a source: a
closure, outage or repair ("bathrooms out of order (city page, read 2026-11-05)"), a rate's
date, a camper report, a road warning. When unsure whether something is bookkeeping, keep it.

## Attribution markers
`--AWH` / `--Claude` mark the end of the segment their author wrote. Never move a marker
off its own text. If your cuts empty a segment, drop its marker too; if that marker is
`--AWH`, set `awh_dropped: true`. The note must not end in a bare ";".

## --AWH text
AWH's own words: cut chip duplicates in them as above (that rule includes --AWH text), but
**do not move AWH's own text to curation** — if an --AWH segment reads like bookkeeping
("Recommended by Grok ..."), leave it and add an `ask` saying what you would move.

## Do not
Reword, summarise, correct, reorder, merge or tidy anything else; fix typos; touch facts that
are not in `shown`; add anything. Do not edit any file but your output file.

## Calls settled in chunks 001-014
- **To curation:** "kept as an exception ... per AWH", "Kept as a nightly stop ... (AWH date)", "Kept because trip N stayed here", "AWH <date> (driven past)", "Added by cross-referencing ...", "rest on directory listings (checked ...)", "RV Life mis-tags it ...", "RV Life N★/$$, N reviews; confirmed operating", "RV Life N stars (few reviews)", "RV Life rating not recorded", "Currently operating per ...", "PIN APPROXIMATE ... verify", "FLAGGED:", "Aggregator claims ... official wins", "a real campground, not event-only / not equestrian-only / general campground", "Under $50/night" (the sweep's price gate), audit stamps, and a named private person (a manager or host by name).
- **Cut:** an RV Life sentence whose stars/$ the Rating chips show, together with its "N/10" score and review count; a minimum-stay segment the Booking chip states at least as specifically; amenities inside a list (showers, dump station, flush/vault toilets, laundry, WiFi, potable water) when a Facilities chip shows the same item; an older --Claude "FCFS" when `shown.Booking` says "no walk-up sites" (a later, dated finding).
- **Passed closures:** a --Claude closure/construction caveat whose dates have fully passed AND that a later "Rechecked" line says is over: move both to curation as one verbatim piece ending in a single --Claude. Without such a recheck, keep it.
- **Seasons:** where the note's season disagrees with the Season chip, keep the note's. Keep holiday-anchored seasons ("Memorial Day-Labor Day").
- **Leave alone:** "(waterfront none)"-style tags (a script handles them); another name the campground goes by elsewhere ("RV Life lists it as ..."), since campers search by it.
- **Ask, don't cut:**
  - An RV Life star figure with no ★ chip in `shown.Rating`: leave it untouched and ask "stars missing from rating".
  - A note saying reservable/bookable when `shown.Booking` says "not reservable": cut neither, and ask "booking chip contradicts note".
- **Readability:** after a cut, what is left still reads as English. No dangling "+", "but" or "--", no sentence starting mid-word, and no one-word leftover sentence like "Back-ins.". If the leftover says almost nothing, keep the original words that carry it. When cutting the head of a sentence ("Max RV ~25 ft with several sites fitting ..."), keep the head if what is left would start with a participle or otherwise not be a full sentence.
