# Campground Schema (structured fields, provenance, and the policy registry)

Split out of CLAUDE.md alongside `docs/campground-curation.md`. That file governs **what
earns an entry** and how `waterfront` is proven. This one governs **what an entry holds**:
the structured amenity/booking/fee/season fields, where each fact's authority comes from,
and how the web UI may edit them without silently destroying what a script wrote.

**Read this before adding a field, writing an extraction pass, or touching the manage
page's PUT path.** As in the curation doc, most rules here correct a specific mistake —
several of them mistakes this repo has already made in other subsystems and would
otherwise make again here at 12,768× the scale.

---

## 1. Format: JSON stays, and the diff is the reason

Measured on the live file before this schema was designed:

| | |
|---|---|
| file | 13.6 MB, 190,014 lines, 12,768 entries (~15 lines each) |
| a one-entry edit from the manage UI | `+21 / -18` lines |
| a 5-entry audit correction | `+5 / -5` lines |
| `json.load` | 48 ms |
| full-scan filter (state + ownership) | 1.0 ms |
| `json.dumps` (whole file) | 102 ms |

The three things a database would buy are **not needed, already solved, or actively
harmful here**:

- **Query speed** — a full scan over the whole database is 1 ms. An index solves nothing.
  Even at 10× the entries this is not the bottleneck.
- **Safe concurrent writes** — already solved. `_save_json` writes a temp file in the same
  directory and renames over the target, so a reader sees the old file or the new one and
  never half of each, with a lock serializing writers inside a worker. That fix has its own
  war story in its docstring; don't re-solve it with a storage engine.
- **Reviewable diffs** — this is the one JSON wins outright, and it is load-bearing.
  The entire curation discipline is *audit by commit review*: a sweep appends entries, an
  audit changes `waterfront` plus its evidence, and a human reads that diff. Pretty-printed
  JSON with stable key order makes a single-field correction show up as a single changed
  line. **SQLite would put a binary blob in git and end that**, and it would complicate the
  offline USB build for no gain.

**JSONL (one entry per line) is worse, not better, and the reason is non-obvious.** It
makes a one-entry edit a `+1 / -1` diff, which sounds ideal until you try to review it: the
changed line is ~1 KB of JSON and the reviewer cannot see *which field moved*. Today's
`+21 / -18` is more lines and far more information. For a human-audited dataset,
pretty-printed JSON is the optimum, not a legacy compromise.

**The one real pressure point is write amplification**, and it is not a format problem:
every UI save re-dumps all 13.2 MB (~102 ms). Adding structured fields grows that. The
release valve when it hurts is the **evidence sidecar** — `waterfront_evidence` and
`inclusion_evidence` are 4.1 MB, 30% of the file, and no client ever reads them — not a
new storage format.

**Revisit this decision if**: entries pass ~50k, or the app ever needs genuinely concurrent
multi-user writes. Neither is on the horizon.

Unchanged rules from CLAUDE.md that this schema inherits: write with `ensure_ascii=False`
(or every em-dash in every note re-escapes and churns the whole diff), append rather than
re-dump when adding entries, and ids come from `max(id) + 1` across **both** location files.

---

## 2. The two rules everything else hangs on

### 2.1 Absent means unknown. Never store a placeholder.

`"showers": false` is a claim that somebody looked and there are none.
A **missing key** means nobody looked. These must never collapse into each other.

This exact trap has bitten this repo twice in `process_rollups.py` — a day with no GPS had
no `miles` key and the model read the silence as a measured zero, writing "the trip opened
parked" for a day that drove from home. At 12,768 entries the same mistake is far more
expensive, because a default written once is indistinguishable from twelve thousand
verified facts.

Consequences, all mandatory:

- **An extraction pass writes nothing for what it could not determine.** It does not write
  `false`, `0`, `null`, or `""` to mean "not found."
- **The manage form uses tri-state selects, never checkboxes.** A checkbox cannot express
  unknown. Ship one and the first unrelated save writes `false` across every amenity on
  that entry, permanently, and nothing will ever flag it.
- **Search treats absent as "cannot rule out," never as "no."** See §2.2.

### 2.2 Eligibility defaults UP. (This inverts the waterfront rule — deliberately.)

`waterfront` defaults **down**: "couldn't confirm" resolves to `not waterfront`, because an
unearned on-water claim sends the family to a campground that isn't on the water.

Structured search fields default the **other way**: a campground whose `hookups` are
unknown must **never be filtered out** of a search for electric. It is shown, flagged
unverified, and ranked below confirmed matches.

The asymmetry is not inconsistency — in both cases the rule protects against the failure
the reader cannot detect. A wrong `waterfront` is visible on arrival. A campground silently
**missing** from a result list is invisible forever, and the searcher concludes it does not
exist. **Never let an unknown value exclude an entry.**

The worked proof is Indiana (§5.1): a naive `min_stay: 2` filter removes all 41 Indiana
state parks from a one-night search, when in fact every one of them qualifies.

---

## 3. Provenance: an entry stores only what is true *of that entry*

Policy is mostly set by an agency, not a campground — Indiana's 41 state parks share one
rule. But **the agency rule is a prior, not a truth**: Hither Hills charges double the
nightly rate for non-residents where most NY state parks charge a nominal fee, and Indian
Island (Suffolk County) requires a pricey county season pass.

If an inherited value renders identically to a verified one, the registry **manufactures
confident falsehoods at scale** — 102 NY entries all displaying "nominal non-resident fee,"
uniform and authoritative-looking and wrong exactly at the park you'd want. That is worse
than blank, and it is the same failure shape as §2.1: a default read as a measurement.

### The resolution rule

**An entry stores only facts verified for that entry. Everything else resolves from the
policy registry at read time.** Nothing is copied into the entry.

```
effective(entry, field)  =  entry[field]              if present  → scope "entry"
                            registry[policy_ref][field] if present → scope "agency"
                            absent                                → scope unknown
```

This is the same merge shape as `_load_locations_by_id()` reading both location files: one
source of truth, merged on read. It matters because:

- A registry correction propagates to all inheritors instantly. Copies would need re-syncing
  and would silently go stale.
- The file does not grow by a booking block × 6,635 entries.
- **"Verified" becomes literally checkable**: the entry has its own key, or it does not.

### `policy_ref` and the three-level chain

An entry inherits from up to three rows, **most specific first, merged per field**:

```
1. an explicit `policy_ref`      "local:suffolk-county-ny" · "federal:usfs"
2. "{ownership}:{state}"         "state:IN" — where the state IS the agency
3. "{ownership}"                 "federal" — where it is not
```

Level 2 covers most of the database, because a state park system is both an owner and an
agency. **Level 3 exists for federal**, whose policy is set per agency and largely by
recreation.gov rather than per state — without it a single federal rule would need fifty
identical `federal:XX` rows, and the 3,738 federal entries would be unreachable in practice.
Levels compose per field, so a `federal` baseline and a `federal:usfs` override merge
instead of replacing one another.

**`policy_ref: "none"` declines all three, and exists because levels 2 and 3 are DERIVED
and therefore cannot otherwise be refused.** An entry cannot be `ownership: state` in
Georgia without inheriting `state:GA`. Jekyll Island Campground (id 590) is the case that
forced it: the island calls itself a state park and is state-owned, but it is run by its own
authority, books through Campspot rather than the state's ReserveAmerica contract, charges
its own per-day gate fee, and a Georgia ParkPass is explicitly not valid there. Inheriting
would print the state system's 13-month window, 4pm cutoff and walk-up behaviour under
*"Typical for Georgia state parks"* on the one campground each of them is wrong for — the
confident-falsehood-at-scale failure this section exists to prevent, aimed at a single
entry. The sentinel is matched case-insensitively, a row named `none` is consequently
unreachable, and the entry's own verified groups still resolve as `entry` scope. Use it only
when the entry is genuinely outside its agency's system, never to paper over a row that
merely has the wrong value — fix the row. **Both sides must agree:** `policy_refs()` in
`campground_schema.py` and `policyRefFor()` in `templates/campground_manage.html`, or the
manage form keeps offering agency hints the server no longer applies.

**But federal is also where the registry helps least, and the leverage table above
oversells it.** Federal camping policy varies by *facility*: the 6-month rolling window is
the recreation.gov standard, yet group sites often open 12 months out and some BLM/USFS
facilities use 14- or 30-day windows, and FCFS varies campground by campground. So the
`federal` row deliberately carries only what is genuinely agency-wide and **withholds `fcfs`
and `min_stay` entirely** — defaulting either would be wrong at scale and invisible in the
entries. The right instrument there is the per-facility availability walk (§7 phase 4).

### `provenance`

Records the source and date for entry-scoped verifications only, per **group** — not per
field, because that is how research actually happens (you read one agency page and fill one
block).

```jsonc
"provenance": {
  "fees":   {"source": "https://parks.ny.gov/...fees", "checked": "2026-09-14"},
  "season": {"source": "recreation.gov availability calendar", "checked": "2026-09-14",
             "method": "derived"}
}
```

`method` is optional: `derived` marks a value a machine extracted (from note prose or an
API) rather than a human confirming it. Derived outranks inherited and is outranked by a
human check.

### Display and ranking

- Inherited values **never phrase themselves as a fact about the park**. "NY state parks
  typically charge a small non-resident surcharge," not "$5 non-resident fee."
- Verified > derived > inherited in search ranking.
- An inherited value may never be the sole basis for excluding an entry (§2.2).
- Outliers are **not randomly distributed**: within a state system, fee variance tracks
  demand, so the exceptions cluster in destination parks — precisely the ones worth
  booking. The outlier rate among entries you would realistically choose is higher than the
  base rate. Verify opportunistically, driven by what searches actually surface, rather
  than uniformly.

---

## 4. Field groups

All groups are optional. Within a group, every key is optional, and **absent is unknown**
(§2.1). Groups exist rather than 20 flat fields because both the PUT whitelist and the
manage form become unmanageable otherwise.

```jsonc
"rating": {
  "source": "rvlife",            // "rvlife" | "goodsam"
  "stars": 4.5,                  // as published
  "price_tier": 2,               // 0-4, the RV Life "$" count
  "checked": "2026-06"           // YYYY-MM
},

"hookups": {
  "electric": 50,                // 0 | 20 | 30 | 50 — the HIGHEST amp available on site
  "water": true,                 // at the site, not a communal spigot
  "sewer": true,
  "dump": true                   // dump station on site; independent of "sewer"
},

"sites": {
  "count": 44,
  "max_rig_ft": 40,
  "pull_through": true
},

"facilities": {
  "showers": true,
  "flush_toilets": true,
  "vault_toilets": false,
  "potable_water": true,         // communal spigots, even with no site hookups
  "laundry": false,
  "camp_store": false,
  "wifi": false
},

"season": {
  "year_round": true
  // ── or ──
  // "opens": "04-01", "closes": "10-31",   MM-DD, no year: this recurs
  // "note": "loop B closes after Labor Day"
},

"booking": {
  "reservable": true,
  "platform": "recreation.gov",  // recreation.gov | reserveamerica | usedirect |
                                 // goingtocamp | campspot | roverpass | hipcamp |
                                 // sepaq | operator | phone | none
  "url": "https://...",          // deep link, when it differs from "website"
  "window_opens_days": 180,      // how far ahead booking opens
  "reserve_until": { ... },      // see §4.1
  "fcfs": "after_cutoff",        // "never" | "always" | "after_cutoff" | "some_sites"
  "min_stay": [ ... ],           // a LIST of rules — see §4.1
  "max_stay_nights": 14
},

"fees": {
  "nightly_low": 25,
  "nightly_high": 45,
  "currency": "USD",             // "USD" | "CAD" — see the CAD caveat in §4.3
  "reservation_fee": 8,          // per-reservation booking fee, if separate
  "nonresident": { ... },        // see §4.2
  "prereq_pass": { ... },        // see §4.2
  "entrance": { ... },           // see §4.2 — a gate fee, NOT a camping surcharge
  "checked": "2026"
},

"discounts": {
  "good_sam": true,              // accepts the Good Sam member discount
  "passport_america": false,
  "koa_value_kard": false,
  "military": true,
  "interagency_senior_access": true   // America the Beautiful Senior/Access pass
}
```

Every group also accepts a free-text `note` for whatever the vocabulary cannot
hold. Use it for the qualifier that changes the meaning — "only at a limited
number of parks", "the two official pages disagree" — never as a substitute for
a field that exists.

### 4.1 Booking rules are conditional, and a scalar loses the fact

The three real cases that drove this shape are near-opposites at the same instant, and a
flat `fcfs: true/false` cannot tell them apart — Iowa's FCFS *is what its cutoff creates*.

```jsonc
// reserve_until — when booking closes
{"relative_to": "arrival", "at": "23:00"}            // IN: until 11pm on arrival night
{"relative_to": "arrival", "offset_hours": -48}      // IA: closes 48h before arrival
{"relative_to": "arrival", "at": "14:00"}            // MD: early afternoon day-of

// min_stay — a LIST, because agencies run several rules at once
[{"nights": 2, "applies": "weekend", "waived_if": {"booking_within_days": 3}},
 {"nights": 3, "applies": "holiday"}]
```

**`min_stay` is a list because the first agency verified proved one rule is not
enough** (2026-09-14). Indiana waives its two-night weekend minimum for sites
still unrented three days out — and says in the same breath that "Required
holiday minimum stays are excluded from this relaxed rule", with holiday
weekends needing three nights. A single rule object can hold the waiver or the
holiday, not both, and **all four states verified so far carry the same
weekend + holiday pair**. An evaluator takes the strictest rule whose `applies`
matches the arrival date. An empty list clears the key rather than storing `[]`,
which would claim the agency has no minimum at all.

`applies`: `always` | `weekend` | `holiday` | `summer`.
`waived_if`: `{"booking_within_days": N}` — the only waiver shape observed so far; extend
deliberately rather than by adding a free-text escape.

**These are evaluated against the query's arrival date and booking time**, never stored as a
verdict. A rule the evaluator cannot interpret degrades to "verify" and the entry is still
shown (§2.2).

Anything the vocabulary cannot hold goes in a prose `booking.note` — and the entry's `note`
remains the source of truth for nuance (§6).

### 4.2 Fees have three distinct mechanics

Flattening these into one "surcharge" number loses the cases that matter:

| mechanic | shape | effect on one night |
|---|---|---|
| per-stay surcharge | `{"type": "surcharge", "amount": 15, "per": "stay"}` | +$15 |
| **multiplier** | `{"type": "multiplier", "factor": 2.0}` | doubles the rate |
| **prerequisite pass** | `{"name": "...", "price": 25, "valid": "season"}` | whole pass price lands on night one |

`per`: `stay` | `night`. `valid`: `season` | `year` | `day`.

**`nightly_low` / `nightly_high` are the BASE rate — what a RESIDENT pays for a plain
site with no amenities.** Every other key in `fees` modifies it. Storing the
non-resident price, or the with-hookups price, makes the field incomparable between
agencies and double-counts the moment a modifier is applied on top.

**Amenities are priced separately, and they are what a search filters on.** Both systems
verified so far charge per night for exactly the things a traveller specifies: electric is
+$7 in NY state parks and +$8 in Suffolk County, a waterfront site +$6, oceanfront +$10,
full hook-ups +$13–15. A cost estimate that quotes the base rate for a query that demanded
electric hookups understates the night the traveller actually needs, so `fees.surcharges`
carries them. Anything with no cross-agency equivalent — Suffolk's Premier/Tier I/Tier II
site classes — stays in `fees.note`.

**A park ENTRANCE fee is a fourth mechanic and must not be folded into
`nonresident`** (2026-09-14). Indiana charges every vehicle to enter — $7 with
Indiana plates, $15 without — and has no non-resident *camping* rate at all;
New York is the exact opposite, with no gate-fee split and a real $5/night
camping surcharge. Recording Indiana's $15 as a camping surcharge would
overstate a one-night stay and misattribute the charge:

```jsonc
"entrance": {"resident": 7, "nonresident": 15, "per": "vehicle_day"}
```

Both sides are stored so the differential ($8) is derivable rather than baked
in, and so a resident cost can be shown too.

The third is the one a flat model cannot express at all: a season pass amortizes fine over a
week and terribly over one night, so its cost is **a function of trip length**. Which means
the honest presentation is not a stored tier but **effective cost for this stay**, computed
at query time from `home.json` residency, the number of nights, and whether the pass is
already held.

### 4.3 Do not fold fees into `rating.price_tier`

`price_tier` is RV Life's number, computed on a raw nominal average rate. It is already
known-lossy in two ways: it is **not CAD-adjusted** (Canadian parks are over-tiered by
roughly one level; use avg_rate ≤ ~$55 CAD as the affordable gate), and it knows nothing
about non-resident surcharges.

Keep the stored tier as the imported number it is. Let the presentation layer say
*"$$ nominally, but ~$$$$ for one night as a non-resident"* — computed, labelled, and
attributable. Overwriting the tier would destroy the only thing it is good for: comparing
against other RV Life tiers.

### 4.4 `discounts`

Named booleans, same absent-is-unknown rule. `good_sam` is the one asked for; the others are
here because they answer the same question ("what does this actually cost me") and cost
nothing to carry.

Two population notes:

- **`good_sam` is derivable in bulk, not a research chore** (shipped 2026-09-20, §7 phase 5).
  Membership in the Good Sam network is queryable through the Algolia index already
  documented in the Good Sam ratings reference. **Presence in that index is NOT the flag** —
  this doc said it was, and it is not close: the index is the whole directory, 24,462 asset
  rows over 14,993 campgrounds including national forests and county parks, and only 1,896 of
  those campgrounds carry `campground.isGsPark`. That field is the designation, and it is the
  one with a promise attached — Good Sam's own directory says "Every Good Sam Park offers a
  10% discount to the more than 2-million Good Sam members," which is what makes it a
  `discounts` fact rather than a listing. Being *rated* by a Good Sam inspector (the
  three-number facility/restroom/appeal score most listed parks carry) promises nothing and
  is not read. Match by name + coordinate, and treat a non-match as **unknown**, not `false`
  (§2.1): absence from an index is not evidence of refusal. A listing that IS found and says
  `isGsPark: false` is a different thing — a measured no — but it is only worth recording
  where the question is live (see phase 5).
- **`interagency_senior_access` is strongly agency-inheritable** and materially large — the
  America the Beautiful Senior/Access pass halves camping fees at most USFS and USACE sites.
  It belongs in the registry rows for those agencies, not on 3,738 individual entries.

---

## 5. The registry

`campground_policies.json`, tracked in git, keyed by `policy_ref` (§3). Roughly 70 rows
cover 6,635 entries — state 2,197 across ~48 rows, provincial 700 across ~13, federal 3,738
across ~6-10. Median state bucket is 38 entries, so the leverage is about 50:1.

Each row carries the same group shapes as an entry, plus mandatory `source` and `checked`.

**~70 rows are re-checkable annually; 12,768 entries are not.** Fee schedules and
reservation windows change most years, so this is not only the cheaper way to build the
data — it is the only version that stays true.

### Which row to write next: `policy_priority.py`

Read-only, stdlib, no arguments needed. It joins `trip_data/trips.json` against the
location database and ranks the uncovered rows **by nights actually slept**, because
entry count is the wrong question — the database is nationwide and the trips are not, and
that join is what put PA/MD/VA ahead of MI/CA in the first pass. Run it before picking a
row; the script's docstring carries the two traps that made an earlier version of the same
join silently wrong (`is_home_stay()` needs the `place` that only `parse_trips()`
materializes, and family driveways carry no `ownership`).

**As of 2026-09-15 the nights signal is spent**, so it prints an entry ranking too. Every
uncovered row above the best remaining agency is `private:*` / `hipcamp:*` / `local:*` —
the rows named below, which are not research targets — and the agency rows left are at two
nights or fewer (`state:MA` 2, `state:GA` 1, then nothing). Pick the next ones on entry
count, or on a trip actually being planned. They are printed and marked `skip` rather than
hidden, because a row withheld is one nobody can reconsider.

**A `method: "reported"` row is a research TARGET, not a covered row** (2026-09-20). Several
early rows were filled from a single page read and stamped `reported` rather than `manual`.
`state:SD` was one, and re-doing it properly moved five things: the 90-day window is 90 days
*except Custer at a year*, `fcfs: "always"` is right statewide but four parks cannot be
reserved at all, same-day booking exists at exactly two campgrounds (so no statewide cutoff
is recorded), the $10 non-resident charge is a per-SITE booking fee rather than a rate — the
registry's first `nonresident.per: "stay"` — and the entrance licence, which camping fees
never include, was entirely absent. `policy_priority.py` counts a reported row as covered,
because it is keyed on the row existing; read the `method` before trusting a row's silence.

South Dakota also turned out to be the second agency, after Massachusetts, that publishes
**per-campground** rates and dates on its own site, so the row carries the shape and 57
entries carry their own figures. Expect that pattern rather than the Indiana one wherever a
state runs its own reservation system: the park pages are where the numbers live.

The remaining 6,133 entries (private, local, hipcamp, wma) have **no agency to inherit
from**. Do not attempt to research booking cutoffs for them: FCFS/walk-up is the norm rather
than a system, notes already mention walk-up on 2% of entries, and the correct answer at 5pm
on the road is the phone number. Carry `phone`, leave policy unknown, let the UI say
"call ahead."

### 5.1 Worked cases

These seven pin the schema. Any change to the vocabulary must still express all seven.
Four were verified against agency sources on 2026-09-14; the two NY entry-level
cases (Hither Hills, Indian Island) are still as reported and not yet checked.

**Indiana state parks** (`state:IN`, 41 entries) — *the reason rules are a list.*
Verified 2026-09-14 against `CAMPING_BUSINESS_RULES.pdf`.
```jsonc
"booking": {"reservable": true, "window_opens_days": 180, "fcfs": "always",
            "reserve_until": {"relative_to": "arrival", "at": "23:00"},
            "min_stay": [
              {"nights": 2, "applies": "weekend",
               "waived_if": {"booking_within_days": 3}},
              {"nights": 3, "applies": "holiday"}],
            "max_stay_nights": 14},
"fees": {"reservation_fee": 6,
         "entrance": {"resident": 7, "nonresident": 15, "per": "vehicle_day"}}
```
Verbatim: *"campsites can, and should be, reserved until 11pm ET on the date of arrival"*
and *"Indiana is 100% reservable until 11pm ET on the day of arrival"* — no sites are held
back, though walk-in registration is still taken on the day of arrival. A scalar
`min_stay: 2` would drop all 41 from a one-night search; the *One-Night Relaxed Rule*
(*"If a campsite is not rented within 3 days of arrival, it will be available for one-night
rental"*) is what makes every one eligible. **The second rule is the catch**: *"Required
holiday minimum stays are excluded from this relaxed rule."*

The reported "$15 out-of-state fee" turned out to be the **park entrance fee** ($7 with
Indiana plates), not a camping surcharge — see §4.2.

**Iowa state parks** (`state:IA`) — *the reason a conflict is recorded rather than resolved.*
```jsonc
"booking": {"reservable": true, "window_opens_days": 90,
            "min_stay": [{"nights": 2, "applies": "weekend",
                          "season": "May 1 - Oct 31"},
                         {"nights": 3, "applies": "holiday", "season": "..."}],
            "note": "CUTOFF UNRESOLVED - two DNR pages contradict each other..."}
```
No `reserve_until` and no `fcfs`. Two Iowa DNR pages disagree — the overnight-camping page
says *"The last day to make a camping reservation, if paying by credit/debit card, is 2 days
prior to arrival"* (matching the reported 48-hour rule), while the make-reservation page
says *"up to the day of to the arrival date if paying by credit card"*. Neither is obviously
stale. **And the FCFS half is unconfirmed by any official source**, which matters because it
is the whole reason an Iowa park would answer a late-in-the-day query. Resolve by phone
before writing either.

**Maryland state parks** (`state:MD`) — *the reason a reported policy must be checked.*
```jsonc
"booking": {"reservable": true, "window_opens_days": 365, "fcfs": "always",
            "min_stay": [{"nights": 2, "applies": "weekend",
                          "season": "Memorial Day - Labor Day"},
                         {"nights": 3, "applies": "holiday"}],
            "note": "Same-day booking closes 17:00 but only at SOME parks..."}
```
Maryland was reported as having no same-day booking after an afternoon cutoff **and no
FCFS**. The second half is wrong: *"Walk-in guests at parks and forests can request any
non-reserved sites."* The first half is real but narrower than an agency default can carry —
*"Same day reservations are allowed at a limited number of parks through the call center and
website until 5 pm"*, and Maryland does not publish which parks. So the cutoff belongs on
entries once known, not on the row; writing `17:00` here would promise same-day booking at
parks that do not offer it.

**Hither Hills** (NY state park, id 291) — *the reason inheritance is a prior, not a truth.*
Verified 2026-09-14 against the park's own fees page.
```jsonc
"fees": {"nightly_low": 33, "nightly_high": 37,
         "nonresident": {"type": "multiplier", "factor": 2.0}},
"season": {"opens": "04-10", "closes": "11-22"}
```
| | resident | non-resident |
|---|---|---|
| weekday | $33 | **$66** |
| weekend | $37 | **$74** |

Exactly double in both bands, and it **replaces** the statewide $5/night surcharge rather
than adding to it. Inheriting `state:NY` here would understate a weekend night by $32 — on
the most sought-after campground on Long Island, which is precisely where an entry is most
likely to be an exception (§3: fee variance tracks demand). The `*` beside it on the
statewide fees page is unrelated to residency: it marks a **flagship** campground, *"premier
facilities that provide premium amenities"*, +$3.00/night.

**Indian Island** (Suffolk County, NY, id 1448) — *the reason `prereq_pass` exists, and the
reason `policy_ref` does.*
```jsonc
"policy_ref": "local:suffolk-county-ny",
"fees": {"prereq_pass": {"name": "Suffolk County Non-Resident Reservation Green Key",
                         "price": 50, "valid": "year"}}
```
It is a **county** park in a state whose `state:NY` row describes state parks, so without
the explicit `policy_ref` it would fall through to entirely the wrong agency — the default
`{ownership}:{state}` key gives `local:NY`, which does not exist, but a careless row added
under that name later would be worse than nothing.

The Green Key is not a discount card, it is **an access gate**: *"The Green Key card is also
required to access the online reservation system for camping and marina reservations."* A
non-resident cannot book at all without the $50 one-year key. One night in season with
electric runs $36 base + $8 electric + $5–22 site tier + $10 reservation + $3 registration —
and then the $50 key roughly doubles the trip, while over a year of Long Island camping it
disappears. That is exactly why a prerequisite pass is priced separately from the nightly
rate and resolved against trip length (§4.2) rather than folded into a tier.

Suffolk's non-resident camping rate is **also exactly double** the resident rate ($18 → $36
in season, $9 → $18 off season), so the county row carries the same multiplier Hither Hills
does. Two independent agencies reaching for the same mechanic is the argument for keeping
`multiplier` in the vocabulary rather than treating it as a one-off.

**Massachusetts DCR** (`state:MA`, 22 entries, 2026-09-20) — *the case where the agency page
is entry-level data, and the one that added a field.*
```jsonc
// on the ENTRY, not the row — DCR's fee table names every campground:
"fees": {"nightly_low": 22, "nightly_high": 22,
         "nonresident": {"type": "surcharge", "amount": 48, "per": "night"},
         "surcharges": {"electric": 6, "water": 4}}
```
Two lessons. First, **an agency page can be entry-scope evidence**: the registry exists
because policy is usually set agency-wide, but Massachusetts publishes a per-campground rate
table and a per-campground season schedule, so the right move was to write 21 entries' own
rates and 22 entries' own dates and leave the row carrying only the shape. A row is the
cheap answer, not the goal. Second, `fees.surcharges` gained **`water`**: Salisbury and
Scusset Beach sell water at $4 and electric at $6 *on the same site*, and only
`full_hookup` existed for the pair — which would have invented a bundle DCR does not sell.

Massachusetts is also the sharpest non-resident case in the registry so far: ~3.2× the
resident rate, charged as the camping rate rather than a gate fee, so no pass avoids it
($17 → $54 inland, $22 → $70 coastal). And its published *"2-day minimum stay at most
campsites"* carries no weekend or holiday scoping, unlike every other state verified — yet
trip 16 booked two separate single weekend nights at Harold Parker in August 2023 with that
exact sentence live on mass.gov. It is stored, because it is what the agency says, and the
note carries the contradiction; §2.2 is what keeps it from ever emptying a one-night search.

**A rec.gov federal campground** — most of the block resolves from `federal:usfs` or
`federal:nps`; season and FCFS are *derived* per entry from the availability calendar (§7).
```jsonc
"policy_ref": "federal:usfs",
"season": {"opens": "05-15", "closes": "09-30"},
"provenance": {"season": {"source": "recreation.gov availability calendar",
                          "checked": "2026-09-14", "method": "derived"}}
```

---

## 6. Extraction is additive. The notes stay.

Structured fields are a **searchable index derived from** the note, not a replacement for
it. The note remains the source of truth for anything the schema cannot hold — *"longer rigs
may curb-park (32-ft limit suggested)"*, *"water off Dec-Mar"*, *"pay/permit at City Hall
(721 W. Robertson St)"*. No vocabulary holds those, and gutting the prose to populate fields
would lose them permanently.

**One exception, and only one.** The templated RV Life tail — `RV Life 4*/$$ (auto 6/2026)`
— is purely structured data stored as prose on 6,002 entries (47%), and it moves into
`rating` and comes **out** of the note. Nothing else is removed from a note by an extraction
pass.

Attribution markers (`--AWH`, `--Claude`) survive intact; keep someone else's marker and
append your own, per the curation doc.

---

## 7. Population, cheapest first

What is actually recoverable, measured across all 12,768 notes:

| field | present in notes | channel |
|---|---|---|
| RV Life rating (`4*/$$ (auto 6/2026)`) | **80.4%** (47% fully templated) | mechanical regex |
| restrooms · site count · season · reservable · FCFS | 29–37% | LLM extraction |
| showers · amp service · full hookups · no hookups | 25–28% | LLM extraction |
| dump station · nightly rate | ~20% | LLM extraction |
| max rig length | **3.6%** | research |
| min stay · booking cutoff · non-resident fee | **0.1–1.2%** | research |

The fields most wanted are the ones least present — extraction and research are separate
projects with separate costs, and an extraction pass aimed at booking rules would return
almost nothing.

| phase | work | coverage | cost |
|---|---|---|---|
| 1 | Schema, deep-merge PUT, form sections (§8) | — | ~2 days |
| 2 | RV Life tail → `rating` | 6,002 entries | hours, mechanical, reversible |
| 3 | LLM extraction pass over notes | 20–37% per field | 1 day + cheap batch |
| 4 | rec.gov calendar walk → season + FCFS | 2,389 federal | unattended, slow |
| 5 | Good Sam network match → `discounts.good_sam` | bulk | hours |
| 6 | Agency registry (~70 rows) | 6,635 as inherited | **20–25 h research** |
| 7 | Per-entry verification | use-driven | ongoing, never "done" |

**Phase 3** must be incremental the way `day_rollups` is: hash the note, re-extract only
what changed, and merge deltas into the store at write time rather than dumping a dict
loaded at startup — a batch racing a UI edit must not clobber it.

**Phase 3 shipped 2026-09-15 as `extract_fields.py`.** Targets `hookups` / `sites` /
`facilities` / `season` / `booking`; `fees` and `discounts` are excluded because the table
above measures them at 0.1-1.2% of notes, where a pass returns almost nothing and invites
the model to infer a price from adjectives. What the build settled:

- **`note_scan` is the incremental record**, a top-level scalar this module owns:
  `{sig, checked, model}`, where `sig` hashes the note the scan read. It is written **even
  when the note yielded nothing**, which is the only thing that stops the ~70% of notes
  holding no structured fact from being re-sent and re-billed on every pass. That is not the
  placeholder §2.1 forbids — a placeholder is a fabricated VALUE; this is an audit record of
  an action that really happened, the same distinction `detect_people.py` draws between a
  stored 0 and an absent key. One block per ENTRY, not per group: five group-level
  provenance blocks across 12.7k entries would add a quarter of a million lines to record
  the same fact five times. Groups that DO yield a value still get their own `provenance`
  entry with `method: derived`.
- **It is chunked and stoppable, because a pass over 12,689 notes cannot be one job.**
  Batches of 12 are each written to disk before the next starts, `--limit` caps a run, and
  SIGINT finishes the batch in flight. Progress lives in the data rather than a cursor file,
  so an interrupted run resumes by being run again and a kill costs at most one batch.
  `--report` shows what is left and costs nothing.
- **A human is never overwritten:** a group whose provenance says `manual` or `reported` is
  skipped, and the entry is still stamped so it is not re-read every run to be refused every
  run.
- **Not structured outputs.** A JSON schema worth having needs `required`, and `required` is
  the opposite of what this pass needs — the whole discipline is OMITTING what the note does
  not say. The reply is parsed tolerantly instead and every field staged through
  `apply_update`, so one hallucinated value is dropped with a warning rather than costing
  the batch. A model `null` is discarded before it reaches that call, because `apply_update`
  reads null as "clear this field" and on a human-filled entry that is a silent deletion.
- **Effort `high`, measured.** `low` is ~$4.30 per 1,000 against ~$6.90 and differed on 7 of
  24 — but four were facts it simply missed (an explicit "reserve May-Sept", a "water
  station", a "no hookups" that should set water and sewer false, a stated May-Sep season)
  against two where it was rightly cautious about an approximate rig length. Omissions are
  the expensive failure for a pass whose point is coverage; the caution was recovered in the
  prompt instead.
- **Two prompt rules that cost a round of review each.** An approximate figure is still a
  figure ("rigs to ~45 ft" -> 45) — `max_rig_ft` is dropped only when the note UNDERCUTS its
  own number ("max RV ~40 ft (tight spacing, best for smaller rigs)"), so the test is
  self-contradiction, not hedging. And `platform` needs the channel actually identified: a
  bare "reservable online" names none, and an early version answered `operator` for it,
  inventing a booking channel out of nothing.
- Yield depends on who wrote the note. AWH's own early waterfront notes ("Many sites are
  right on the lake") yield ~19%; the later Claude-written sweep notes yield ~96%. A
  low-yield stretch is the data, not a broken pass.

**Phase 4** exploits something already in the tree. `AVAIL_URL` in `ridb/fetch_facility.py`
returns per-site, per-night status for a whole month, keyless. Walk a facility across the
year and **the season appears as the closed band, and FCFS loops appear as sites that never
become reservable** — both read off the same API, no agency-site reading. Sampling four
months to find the edges is ~9.5k requests across 2,389 entries: slow against an
undocumented endpoint, but unattended and cacheable.

**Hookups from the RIDB campsite catalog (2026-09-18, `recgov_hookups.py`).** RIDB lists every
campsite of a recreation.gov facility, and each one's `CampsiteType` says ELECTRIC or
NONELECTRIC; electric sites also carry `Electricity Hookup` ("20/30/50"), `Water Hookup` and
`Sewer Hookup`. That is per-site evidence from the booking system itself, better than any note.
Same two-step shape as the calendar walk: `--fetch` fills a gitignored cache
(`trip_data/ridb_campsites.json`, written after every facility, ~2,275 facilities in ~80
minutes at a 1.5 s pace), and the derivation re-runs free from it. The rules, each pinned in
`tests/test_recgov_hookups.py`:

- Only sites an RV can book count: `STANDARD*`/`RV*` types, minus ones whose equipment list
  names no RV. Group, tent-only, walk-to and MANAGEMENT (host) sites answer a different question.
- `electric` is the highest amperage, snapped DOWN to 0/20/30/50. `0` only when EVERY RV site
  is typed NONELECTRIC; an electric site with no amperage writes nothing rather than guess one.
- `water`/`sewer`: true on any yes; false only when EVERY RV site says an explicit no. Most
  non-electric sites carry no such attribute, and a missing one is silence, not a no.
- **Only sites the PUBLIC can use count**, because a camp host's pad is real but no answer to
  "can we plug in" (AWH 2026-09-18). Three rules, each tuned on named cases (the constants'
  comments list them):
  - A site NAMED host is dropped (`(?<![a-z])host`: "Host", "1Host", "Host Site 15", never
    "Ghost"). RIDB types most host pads MANAGEMENT, but not all.
  - At a campground that takes online bookings, UNBOOKABLE sites carrying a hookup are staff
    pads unless they are ≥25% of that hookup's sites AND ≥10% of the campground — then they
    are a walk-up loop (South Rim's Loop B, 22 sites). Mott Park's and Clear Lake's three
    unbookable 50-amp pads beside 30-amp bookable loops are not.
  - Amperage is read off the bookable electric sites when they state one, so a host's 50-amp
    outlet never sets the figure. One or two electric sites count only if bookable; otherwise
    electric is unknown, never 0.
- **Water/sewer need more than two public sites saying yes.** Unlike the site TYPE, these are
  free-form attributes, and one or two stray yeses at a no-hookup campground (Emery Bay,
  Wheeler Peak, Bismarck Lake) are noise, not a hookup loop.
- **A catalog under three RV sites is a placeholder** and says nothing: Long Pool lists ONE
  site for a 38-site campground with an electric loop, which had read as "no electric".
- **RIDB's offset paging is not stable.** Reading a multi-page facility can repeat one site and
  skip another (43 of 717 did, 497 repeats), and a skipped site can turn "some electric" into a
  measured 0. `fetch_campsites` unions pages by `CampsiteID` and re-reads until it reaches
  `TOTAL_COUNT`.
- **The catalog outranks a machine-derived value; a person outranks the catalog.** AWH
  2026-09-18: "I would trust current rec.gov over older auto-generated notes with unknown
  source." The notes were written during the state sweeps from unrecorded sources, so where
  one disagrees with the booking system's own per-site record, the record wins and the change
  is listed by `--conflicts`. A `manual`/`reported` group is never touched. Entries sharing one
  facility link are skipped: some are duplicates and some are wrong links.

First run: 888 entries gained keys. Two same-day corrections followed, from AWH's host-site
point and from reading the replacements' notes: the rules above retracted 104 values (`--retract`
restores a note's value or clears the key), and a catalog under three sites stopped counting.
**Net, stable result:** `electric` 57.7% -> 63.7% of the database; 33 note-derived values
replaced by the catalog, and the 29 sweep notes whose wording contradicted the final value had
that phrase REMOVED (AWH: "just remove the faulty information... no need to add an
explanation") — pure deletions, `note_scan` re-stamped so extraction doesn't requeue them. The
one to watch is Tortilla (AZ): all 76 sites say water+sewer yes against a note that said "no
hookups". The catalog was followed there, as ruled. Re-run `--fetch --max-age-days 365` yearly.
A rule that TIGHTENS cannot undo its own earlier writes (a derive that now says nothing writes
nothing), so `--retract <git ref from before the first run>` undoes the RIDB-written values the
current rules no longer derive — restoring a note's value where one was replaced.

**Phase 5 shipped 2026-09-20 as `goodsam_discounts.py`.** Two steps like the RIDB walk:
`--fetch` caches the whole directory to the gitignored `trip_data/goodsam_parks.json`
(14,993 campgrounds, ~2 minutes) and every later run matches and derives from it for free.
What the build settled:

- **The index will not page past 1,000 records**, so a state over that is read as several
  disjoint queries split on `campground.type`, then the asset `type`, then city. TX alone is
  2,936 rows. The splitter also asks for the remainder a facet does not cover, because a
  record missing the field would otherwise be dropped silently. The run accounts for every
  row it was told to expect (24,462/24,462) and that equality is the check worth repeating.
- **Matching is name + coordinate, and the subset guard is the rule that matters.** A Good
  Sam pin is geocoded from a mailing address where this database pins the campground, so a
  real pair can sit 1.9 km apart; the accept bands trade naming variation against distance
  (3 km at 0.90 similarity but only for a WHOLE-name match, 800 m at 0.75, 250 m at 0.62).
  A subset name is what the whole-name requirement exists for: `Camp Eagle Nest` scores 1.00
  against `Eagle Nest Lake State Park` 1.7 km away, and `Rufus RV Park` against `Rufus
  Landing Recreation Area`, and `Thousand Trails Crescent Bar` against `Crescent Bar
  Recreation Area` — three private parks that wrote a discount onto three public campgrounds
  before the guard existed. A distinguishing modifier on one side only (Silver Lake **East**
  vs **West**) is a veto, and two plausible listings that DISAGREE about the flag drop the
  entry rather than guess it. Good Sam's `Parent/Child` naming (`Lake Roosevelt
  NRA/Keller Ferry Campground`) and this database's parentheticals are both expanded into
  variants, which is where a third of the public-park matches come from.
- **A negative is recorded only where the question is live** (AWH 2026-09-20). The directory
  answers for all 5,828 matched entries, but 4,166 of those are federal/state/local/
  provincial, and "no Good Sam discount" on a national forest campground is noise a reader
  has to scroll past. So `good_sam: false` is written on private and hipcamp entries only,
  while a `true` is written wherever it is found — the 22 municipal and concession-run
  network parks are exactly the surprising ones.
- **`military` came along free and is true-only.** `paymentInfo.discounts` carries
  `militarydiscnt` and no Good Sam entry at all, so the list is read as a positive claim:
  present -> true, absent -> unknown. Unlike `isGsPark` there is no directory-wide
  designation whose absence means anything.

Result: 1,784 entries written — `good_sam` true 336 / false 1,326, `military` true 757.
336 of the 1,896 network parks reached an entry; of the rest, 1,267 have no entry within
3 km at all, which is this database's coverage of RV parks (and the curation rules in
`docs/campground-curation.md` excluding membership and residential parks), not a matching
failure. `--retract` drops values this source wrote that the current rules no longer derive,
since a tightening rule cannot undo its own earlier writes.

**Phase 7 is the one that makes this tractable.** Uniform verification of 12,768 entries is
a project that never finishes. Verification driven by the queries that actually surface
entries converges on the campgrounds that matter within a season of use. Surfacing
*"inherited, never verified"* in the UI is what turns that into a prompt.

Migration: this rewrites all 12,768 entries once, against the usual append-don't-re-dump
rule. Acceptable as a **single mechanical commit with the transform script committed beside
it**, and `ensure_ascii=False` or every note's em-dashes re-escape.

---

## 8. Editing from the web interface

### 8.1 The nested PUT is a clobbering hazard one level down

Today's `PUT /api/campgrounds/<id>` merges from a flat field whitelist and shallow-assigns.
That is what keeps a UI save from destroying `waterfront_evidence`, which the client never
receives.

A nested group reintroduces the identical bug one level down: if the form sends `hookups`
containing only the four keys it knows about, it **wipes any key a later script added**.

**The merge must be deep, with a per-subkey whitelist.** A group the client omits entirely
is left untouched; a subkey the client omits within a group it *did* send is left untouched.
Only an explicit `null` clears a subkey. A subkey absent from the whitelist silently will
not save — the same trap the flat whitelist already carries, now multiplied by the number of
groups, so extend the whitelist in the same commit that adds a field.

### 8.2 Tri-state controls, never checkboxes

Every boolean renders as a three-way select — **yes / no / unknown** — defaulting to
unknown. See §2.1 for what shipping a checkbox costs.

### 8.3 Form layout

The manage form is already a wide grid and the repo's primary UI rule is that every page
must work on desktop, tablet **and** phone. Twenty more inputs in one grid fails that.

Collapsible sections — Identity · Location · Amenities · Booking & Fees · Season ·
Evidence — with Identity and Location open by default and the rest collapsed. Each
non-identity section shows a one-line summary when collapsed, and marks whether its values
are entry-verified or inherited (§3).

### 8.4 Payload placement

`_MAP_MARKER_FIELDS` ships inline for **every** entry in the campground map's HTML — already
~9 MB of HTML at ~1.9 MB gzipped. `_MAP_POPUP_FIELDS` is fetched per campground on demand.

**New groups go in the popup fetch.** Leaking them into the marker payload adds an estimated
2–3 MB to a page that is already the heaviest in the app, to render data no one is looking
at yet. The exception is any field the map's **filter** UI needs to evaluate client-side —
that must ride inline, so add it deliberately and keep it small (a boolean or a short enum,
never a group).

So far the exception is five scalars: `rating.stars` and `rating.price_tier`
(`_MAP_RATING_FIELDS`), and since 2026-09-18 the hookup flags `electric` / `water` /
`sewer` (`_MAP_HOOKUP_FIELDS`, booleans — `electric` is `amps > 0`; the amperage stays in
the popup). All are flattened onto the marker rather than nested so the client reads
`cg.stars` without a group lookup on each of 12.8k markers per filter pass. **Measure before
adding more:** the rating pair took the marker payload from 304 KB to 324 KB gzipped, ~1% of
the page, and the hookup flags added another 16.5 KB. A terse encoding (`s` = stars × 10) was tried and saved 3 KB more — not worth the
unreadable client code, because gzip already collapses 12.8k repetitions of a key name to
nearly nothing. Absent stays absent here too (§2.1): an unrated entry carries no key, which
is the distinction the whole filter turns on.

The audit-evidence strip applies unchanged: `waterfront_evidence` and `inclusion_evidence`
never reach the browser, and the whitelist is what makes that safe.

### 8.5 Search surfaces

The campground map already had the pattern to extend: a legend control with clickable
toggles and a second ownership box built from `OWNERSHIP_LABELS` with
`DEFAULT_HIDDEN_OWNERSHIPS` seeding a sessionStorage fallback. New filters (hookups, season,
FCFS, Good Sam) follow that shape.

Every such filter obeys §2.2: an unknown value is **shown and flagged**, never filtered out.
A filter that silently hides unverified entries turns a 30%-populated field into a search
that quietly returns a tenth of the database.

**Shipped 2026-09-15: the rating filter**, which is the worked example of all of the above.

- **Rating is what could be filtered on first, and coverage is the whole reason.** 76% of
  entries carry `rating.stars` and 90% `rating.price_tier`; `hookups`, `facilities` and
  `season` are at **0%** until the extraction pass (§7 phase 3) runs, and everything
  populated in `booking`/`fees` is inherited from the registry, which §3 forbids being the
  sole basis for excluding an entry. A filter for a field nothing carries is a control that
  empties the map. **Measure coverage before building the next one.**
- **One box, not three.** The rating controls went *into* the bottom-right ownership box,
  which is now headed **Filters** with an `Ownership` sub-heading. A third bottom-corner
  control costs a phone ~90 px of map even fully collapsed, and the mobile rule that lifts
  bottom controls clear of the attribution (`margin-bottom: 28px`) applies to each of them,
  so stacked boxes also open a dead gap between themselves. The legend stays separate
  because it explains the colors; these two both narrow what is drawn.
- **§2.2 is implemented as fading, plus an explicit opt-out.** An entry the active threshold
  cannot evaluate stays on the map at `fillOpacity` 0.25 instead of 0.8 — opacity because
  the fill color already carries the waterfront/climate category the legend explains, so it
  is the one channel free to mean "unverified". An **Include unrated** checkbox, on by
  default, is the only way to drop them, and the box states the count either way ("2,940
  faded dots are unrated, not excluded" / "2,940 unrated campgrounds hidden").
- **The number that justifies the code:** a naive `stars >= 4` shows 8,688 of 12,774
  campgrounds. Honouring §2.2 shows 11,694. The 3,006 difference is **24% of the database**,
  concentrated in the public land RV Life never rated — which is most of what the map is
  for.
- **"Unknown" is scoped to the thresholds actually set**, and an unknown on one field never
  launders a failure on the other. With only a price filter on, a star-less campground is
  not unrated; a `$$$$` entry with no stars under "4+ and $$ or less" is *hidden*, because
  it fails on a value somebody measured rather than on a silence.
- **Both counts are taken from the render pass**, not recomputed over `CAMPGROUNDS` —
  otherwise the note includes entries the ownership filter had already removed and
  contradicts the map it is describing.
- `tests/test_rating_filter.py` pins all of it by lifting the predicates **verbatim** out of
  the template and running them in quickjs against the real `campgrounds.json`. A Python
  reimplementation would be a paraphrase, and a paraphrase of the rule under test can agree
  with the doc while the shipped code disagrees.

**Shipped 2026-09-18: the hookups filter**, the second one, built the moment phase 3 made
it possible and on the same pattern.

- **Coverage, measured first:** `electric` is recorded on 58% of entries, `water` 67%,
  `sewer` 57%, and none of it is inherited — the registry supplies no `hookups`. Facilities
  (showers 29%, flush toilets 8%) and season (30%) were too thin to be next.
- **One select, cumulative levels:** Any / Electric / Electric + water / Full
  (elec/water/sewer). A level requires every hookup it names. "Has" means at SOME sites,
  which is all `hookups` records; the popup says how many.
- **The same two halves as ratings.** A required hookup recorded as absent (`electric: 0`,
  `water: false`) hides the entry; one nobody recorded fades it. So `electric: 0` with water
  unrecorded fails every level, while electric known and water unrecorded is merely unknown
  under Electric + water.
- **One unknown switch for every structured filter**, not one per filter. It is the same
  rule, and two switches could disagree about it. Its label and the note under it are
  worded for the filters actually set ("Include unrated" / "Include unknown hookups" /
  "Include unknown"), and unknown is scoped the same way: with only a hookup level set, an
  unrated campground is not unknown. The combined predicates are `schemaPasses` /
  `schemaUnknown` / `schemaVisible` / `schemaFaded`; a measured failure on one filter is
  never rescued by an unknown on the other.
- **The fade is large, and that is the honest answer.** Electric was known-yes on 4,388
  entries, known-no on 2,987, and unrecorded on 5,399 (42%) at ship; the RIDB pass (§7) took
  the unrecorded share to 4,591 (36%) the same day. Full hookups leaves 6,475
  unknown (51%). The unknowns are spread across every ownership class (34% of private, 41%
  federal, 44% local, 53% state), so the fade hides no pattern. A naive filter would drop
  all of them. **The lever for shrinking the fade is more data, not a different rule**:
  RIDB's per-campsite attributes could fill the federal share, and phase 5 (Good Sam) the
  private one.
- `tests/test_rating_filter.py` now lifts the whole block, from `includeUnknown` through
  `schemaFaded`, and builds its fixture through `_map_marker_rows` itself, so the tests
  see exactly what rides inline.

### 8.6 The popup draws the two halves separately

The map popup fetches the resolved groups along with the rest of its detail (§8.4) and
renders them as chip runs: the verified half in the page's own voice, the inherited half
in the manage form's muted tan, italic, under the heading *"Typical for <agency>"* and the
caveat line *"Not checked for this campground"*. The heading is bold small caps inside a tan
left rule that runs down the whole block (AWH 2026-09-18): it used to be one plain tan line in
the rows' own size and weight, which read as the first row's text rather than a title over
them. Three parts of this are load-bearing rather than decorative.

- **`resolve()` names the inherited KEYS, not just each group's scope.** A `mixed` group
  holds both kinds of value at once — Hither Hills' own doubled rate sits beside the
  statewide surcharges it never overrode — and §3's ban applies field by field, not group
  by group. The renderer subtracts `inherited` from `values` to get the verified half, so a
  key missing from that list is silently promoted to a fact about the park.
- **The agency half appears only when the server could NAME the agency.** A registry key
  (`state:IN`) cannot finish that sentence, so `_policy_label()` spells one out of the
  entry's own ownership and state ("Indiana state parks", "federal campgrounds" — never
  per-state, since level 3 exists precisely because federal policy is not), and title-cases
  the slug of an explicit `policy_ref`. An unattributed inherited value is exactly the
  confident falsehood this model exists to prevent, so **no label means no agency block**.
- **Both pages format a value through one shared module**, `static/campground-schema.js`.
  A second copy of the phrasing in the other template would drift the first time a field
  was worded on one side only, and the failure is quiet: both pages keep rendering, and
  disagree. The field metadata still comes from `to_client()`; only the phrasing lives
  there.

The popup is a summary — six chips a group in the verified half, **four in the agency
half**, then a `+N more` tail. The manage form is where every value is visible and the only
place any of them can be edited.

### 8.7 A chip is read by someone who has never seen the schema

The stored shapes are terse because storage should be; the chips were terse because they
were written next to the storage. A pass over every distinct phrasing the database can
produce (rendered through the real module against the real data, not imagined) turned up
one collision and a run of shorthand nobody outside this repo could expand. The rules that
came out of it:

- **No invented abbreviation, and no unit left to inference.** `180d ahead`, `max 14n`,
  `2n weekends` and `to 25 ft` became *books 180 days ahead*, *max stay 14 nights*,
  *min stay 2 nights on weekends* and *rigs to 25 ft*. This bites hardest in the agency
  half, which is the one telling the reader something indirect already.
- **`res` meant two things one chip apart.** A reservation fee rendered `+$5 res` while a
  non-resident surcharge rendered `non-res +$5/night`, and Virginia's row printed both. The
  reservation fee is now *+$5 booking fee*; resident/non-resident are spelled in full.
- **A negative has to be English.** `season.year_round` false is *seasonal*, never
  "no open year-round" — a label that cannot carry its own negation gets an explicit chip.
- **A stored date is not a written one.** `05-01` renders *May 1*, and a span renders as
  one chip (*open May 1 – Oct 1*); an opening date alone says *opens May 1*, because
  "open May 1" reads as if that day were the season.
- **What a fee is charged PER changes what it is.** Michigan's `$15/$40` is an annual
  vehicle pass and read as a gate fee, so `entrance.per` is now always spoken (*annual park
  pass …*, *park entry $7 resident, $15 non-resident (per vehicle/stay)*). Same reasoning
  makes a nightly rate say `/night` and `fees.currency` render `C$` rather than `$`.
- **A bound dropped is a rule overstated.** `min_stay[].season` was not rendered, so
  Maryland's and Pennsylvania's weekend minimum — Memorial Day to Labor Day, absent the
  rest of the year — read as year-round. It is spelled verbatim in parentheses now,
  however long: these strings are prose because the rules are ("July 4 when it falls
  Fri-Mon"), and paraphrasing a date range is how a bound stops being true. Five registry
  rows carry one. The `waived_if` on four others still goes unmentioned, per §4.1 — but
  note that it errs the *same* way, toward the stricter reading.
- **Fold where the reader already read it; expand where the chip only hinted.**
  `50A · water · sewer` is one chip (*full hookups (50A)*) and its opposite is *no hookups*;
  a dated season drops the redundant *seasonal*. Against that, `surcharges` rendered as the
  bare label *per-night amenity surcharges* — the existence of a cost, with no cost — and
  now expands to one chip per add-on (*electric +$7/night*), letting the six-chip cap trim
  the tail instead of the formatter.

Both surfaces change together because both call `sfChips`; the manage form's collapsed
summary is the same run cut to three.

**Surfacing the rating was a fix, not a garnish.** Phase 2 lifted `RV Life 4*/$$` out of
the note prose on 11,771 entries, and the popup renders the note — so between that pass and
this one, a published fact about four fifths of the database was visible nowhere but the
admin form. Any future extraction that empties prose into a field inherits the same
obligation: the field has to come back out somewhere a reader looks.
