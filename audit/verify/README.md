# Schema phase 7: verifying a campground against its own pages

Read `docs/campground-schema.md` §2-§4 first (absent means unknown, provenance, the field
groups). This file is the procedure for checking ONE entry and writing the result.

**Order of work** comes from `queue.py` (AWH 2026-10-20): campgrounds stayed at, then ones anyone
in the family opened on the map, then every other campground, state by state in order of how
much the family camps there.

**The loop:** `queue.py --batch NAME --limit N` writes `batches/NAME.json` (one dossier per
entry). A verifier works through it and writes one `results/<id>.json` per entry **as soon
as that entry is done**, so stopping costs at most the entry in flight. `apply.py` validates
the results and writes them to campgrounds.json (dry run unless `--apply`); commit after each
batch.

**Parallel verifiers, one browser** (AWH 2026-10-20: 4-6 verifiers at once, still one
headless browser at a time). Plain HTTP (curl, WebFetch, the rec.gov API) needs no
coordination. Anything that starts a headless browser (the `audit/private_gap_browser/`
driver, gm.py, rates.py, koa.py) must run under the shared lock, so verifiers queue for it
instead of each launching Chrome:

    flock /tmp/ekko-headless-browser.lock <command>

Keep the locked command short (one page or one batched call) so the others are not starved.

**Privacy:** never put AWH's email address or any personal identifier in a User-Agent or any
request to an outside service (one verifier did, to Nominatim); use a plain browser UA.

**Scratch files:** verifiers share one scratchpad, so keep yours in a subfolder named for
your batch (`<scratchpad>/<batch>/`); another verifier overwrote a shared `tools/rg.py`.

## What to check, per entry

The dossier holds `entry` (the stored record), `resolved` (each group's effective values,
its `scope` and which keys are `inherited` from the agency row) and `policy_refs`.

1. **Find the campground's own pages.** The operator's or agency's page for THIS campground
   and its booking page. Federal rec.gov campgrounds: `https://www.recreation.gov/api/camps/campgrounds/<id>`
   (description, notices, rules) and `/rates`; the per-site catalog is cached in
   `trip_data/ridb_campsites.json`. Never confirm from an aggregator (Campendium, The Dyrt,
   campsitephotos, RoverPass tables): those are `reported` at best and only when the
   operator has no page of its own. Beware content farms (see the curation doc).
2. **Check each group the page speaks to:**
   - `fees`: the BASE rate (resident, plain site a 23-ft rig fits, one night, before tax),
     `nightly_high`, currency, reservation fee, non-resident and amenity surcharges. A rate
     needs a date: 2024 or later from the operator.
     The base is never a tent-only or primitive site a 23-ft motorhome may not fit (Jekyll
     Island's $36 primitive sites vs its $51 RV base).
   - `booking`: reservable, platform, url, fcfs, window, min stay, max stay.
   - `season`: opens/closes or year_round. **Only a statement about the CAMPGROUND counts**,
     never park hours or "the park is open year-round".
   - `hookups` (highest amp at a site, snapped down to 15/20/30/50; water/sewer AT the site),
     `sites` (count, max_rig_ft, pull_through), `facilities`.
   - `status`: a temporary closure (with `reopens` as published). When two official pages
     give different reopening dates, record both in `reopens` and `note` rather than
     picking one (Rocky Gap: DNR says 2028, ReserveAmerica 2029).
   - **recreation.gov rule fields and rate tables** (lessons from the pilot): a rate
     season's date range is NOT a campground season (seasons come from a statement, or from
     `recgov_calendar.py`); a minimum rec.gov marks `soft` IS a rule (AWH 2026-10-21: at
     Seven Points the soft weekend minimum is enforced but was relaxed for a same-day Saturday
     booking): record it in `min_stay` and say in `booking.note` that it may be relaxed for a
     same-day booking (a soft value of 0 or 1 is no rule at all); and a catalog length that is
     plainly a typo (140 ft) is left out of `max_rig_ft`, not believed.
   - `booking.platform`: a state's own branded booking site (Reserve Florida, ReserveVAParks)
     keeps the label its agency row uses (`operator` or `usedirect`); don't relabel one as
     the other, it is the same site either way.
   - `discounts`: only what the page states.
3. **Write only what a page says.** Never fill a field with a guess, a typical value or a
   placeholder. A page that says nothing about a field leaves it alone.
4. **Inherited values** (`resolved[g].inherited`): if the campground's page states the same
   value, write it into the entry (it is now verified for this campground). If the page
   states something different, write the campground's value (it overrides the agency row).
   If the page is silent, leave it inherited: do not copy the agency's value in.
5. **Existing entry values** with provenance `method: derived` (read from note prose or an
   API by a machine): the page wins; write its value, or `null` to clear a derived value the
   page contradicts and does not replace. A value whose provenance is `manual` or
   `reported`, or any `--AWH` note text, is NOT overwritten: put the disagreement in `flags`.
6. **Criteria problems are flags, never edits.** If the pages show the campground is closed
   for good, tent/cabin/group-only, hike-in, fits nothing 23 ft long (a trailer limit counts
   for a motorhome too; 22 ft is fine, AWH 2026-10-20), over the US$50 / C$69 base-rate gate
   with no gateway, behind a login to see rates, or otherwise fails
   `docs/campground-curation.md`, say so in `flags` with the evidence. A human decides.
7. **The note — clean it on every entry (AWH 2026-10-21).** Whenever your result changes
   anything, propose a cleaned note in `note` if the current one carries text that is
   (a) **redundant** — it only restates a structured value the entry will carry after your
   result (booking/FCFS, fees/prices, season, hookups, site counts/lengths, facilities,
   discounts, an "RV Life N*/$ ..." or other rating line already in `rating`), or
   (b) **incorrect** against the pages you read. This applies to `--AWH` text too: AWH said
   AWH's comments, pricing and ratings included, are to be trimmed when redundant or wrong.
   List every dropped `--AWH` run in `awh_superseded` (`[{"old": ..., "source": ...}]`), where
   `source` is the page quote that contradicts it, or `redundant: <group.field>`; apply.py
   refuses a rewrite that drops --AWH text without it. Keep what no field can say (where the
   good sites are, setting, caveats with their dates, AWH's firsthand impressions that are
   still true) in the author's words with their marker; sign your own text once, `--Claude`.
   Never ADD facts a field holds to a note. Omit `note` when nothing needs to change.
   Silence or an aggregator never makes text "incorrect"; conflicting official pages don't either.

## Result file: `results/<id>.json`

```json
{
  "id": 620,
  "checked": "2026-10-20",
  "sources": ["https://www.pa.gov/.../shawnee-state-park/stay", "https://pennsylvaniastateparks.reserveamerica.com/..."],
  "groups": {
    "booking": {"values": {"reservable": true, "platform": "reserveamerica", "fcfs": "always"},
                "source": "https://...", "method": "manual"},
    "hookups": {"values": {"electric": 50}, "source": "https://...", "method": "manual"}
  },
  "note": "optional: the whole corrected note",
  "summary": "one line: what was confirmed, what changed, what the pages did not say",
  "flags": ["optional: criteria problems or conflicts with manual/AWH values, with evidence"]
}
```

`groups.<g>.values` uses the schema's own field names; a `null` clears that key. `method`
is `manual` for the operator's or agency's own page, `reported` for anything secondary (and
the `source` must say what it was). A result with no `groups` is still written: it records
that the pages were read and said nothing new, which takes the entry off the queue.
