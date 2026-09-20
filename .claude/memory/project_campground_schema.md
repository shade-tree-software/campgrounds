---
name: project-campground-schema
description: Structured campground fields (amenities/booking/fees/season) + agency policy registry — phases 1/2/3/4/5 + popup surfacing + map rating/hookups filters ALL DONE; phase 5 (Good Sam discounts) shipped 2026-09-20; what's left is phase 6 (registry rows) and phase 7 (use-driven verification)
metadata: 
  node_type: memory
  type: project
  originSessionId: a9cf38ab-6047-479a-a981-ab7343bcae7a
  modified: 2026-09-20T00:00:00.000Z
---

Structured-field project on `campgrounds.json`, started and largely built 2026-09-14.
Rules live in **`docs/campground-schema.md`** (read it first); this is only the status
and the things that are not written down there.

**Done:** schema vocabulary + deep-merge PUT + policy registry (`campground_schema.py`,
`campground_policies.json`); manage-form UI with tri-state selects; RV Life rating lifted
out of note prose into `rating` on 11,771 entries (`extract_rating.py`); rec.gov season
derivation (`recgov_calendar.py`); 27 registry rows covering 5,704 entries (44.7%) and 57.2%
of nights actually slept (`state:WV` added 2026-09-15).

**Map popup surfacing DONE 2026-09-14** (commit `95879c2`): verified and inherited chip
runs, the agency half attributed ("Typical for Indiana state parks") and withheld when
`_policy_label()` cannot name the agency; `resolve()` gained a per-group `inherited` key
list because group-level scope cannot split a `mixed` group; formatters shared with the
manage form in `static/campground-schema.js`. **The motivation is worth carrying forward:
phase 2 had emptied the RV Life rating out of note prose on 11,771 entries and the popup
renders the NOTE, so the pass made a published fact invisible.** Any extraction that moves
prose into a field owes the same debt — see doc §8.6.

**Map RATING FILTER DONE 2026-09-15** (commit `b52cd19`, doc §8.5 rewritten to describe it):
minimum stars + maximum `$` tier in the bottom-right box, now headed **Filters** with an
Ownership sub-heading. **Coverage is what picked the field, and measuring it first is the
transferable part** — `rating.stars`/`price_tier` sit on 76%/90% of entries while
`hookups`/`facilities`/`season` are at **0%** and every populated `booking`/`fees` value is
inherited from the registry (§3 forbids that being the sole reason to exclude). A filter on
a field nothing carries is a control that empties the map, so **measure coverage before
building the next one.** §2.2 is implemented as FADING (`fillOpacity` 0.25 — opacity is the
only free channel, the fill colour belongs to the legend) plus an "Include unrated" checkbox
on by default; the number that justifies it is that a naive `stars >= 4` shows 8,688 of
12,774 where the rule shows 11,694, so 3,006 (24%, mostly the public land RV Life never
rated) would have vanished silently. One box, not three: a third bottom-corner control costs
a phone ~90px even collapsed and the mobile `margin-bottom: 28px` rule applies to each, so
stacked boxes also open a dead gap. Payload measured before adding (§8.4): +20 KB gzipped,
~1%; a terse `s`/`p` encoding saved 3 KB more and wasn't worth unreadable client code.

**PHASE 3 SHIPPED 2026-09-15 as `extract_fields.py`** (doc §7 has the full write-up).
Reads `hookups`/`sites`/`facilities`/`season`/`booking` out of note prose via `claude-opus-5`;
the note itself is never edited. Things worth carrying forward that the doc does not stress:

- **The chunking design is the reusable part**, and AWH asked for it explicitly: "no huge
  unstoppable tasks that lose all their data if the session limit hits. Small chunks,
  sequentially, stoppable, easy to commit work." Batches of 12, N in flight, written in
  WAVES (one writer, so no lock), `--limit` per run, SIGINT finishes the wave. Progress
  lives in the DATA (`note_scan` = hash of the note that was read) rather than a cursor
  file, so resuming is just running it again. Exercised for real: a mid-run Ctrl-C finished
  its wave, wrote 144 entries and exited with a full summary. Use this shape for any future
  bulk pass over the library.
- **`note_scan` is written even when the note yields nothing.** That is the whole of the
  incrementality — without it the ~70% of notes with no structured fact are re-billed every
  pass. Same distinction as `detect_people.py`'s recorded 0. See [[feedback-absent-is-not-unknown]].
- **Effort was measured, not assumed** — `low` looked obviously right for "read a fact off a
  sentence" and was wrong: it MISSED four explicit facts out of 24 to save ~$2.60/1,000.
  Same for workers (1→53/min, 4→82, 16→338, no 429s).
- **Two prompt rules each cost a review round:** an approximate figure is still a figure
  ("rigs to ~45 ft" → 45) and `max_rig_ft` is dropped only when the note UNDERCUTS its own
  number; and a bare "reservable online" names no platform (an early version answered
  `operator`, inventing a channel).
- **Verify a sample against the notes by hand before a bulk run.** That is what caught the
  `operator` bug and confirmed every stored `false` traced to an explicit negative in the
  prose ("restrooms (no showers)", "no potable water", "no hookups").

**PHASE 3 IS COMPLETE — all 12,689 notes scanned, 0 left** (finished with
commit `7982373`, 2026-09-18). Final coverage: hookups 80.2%, sites 78.3%,
facilities 63.2%, season 30.5%, booking 80.3%. `python3 -m unittest
tests.test_extract_fields` green (30 tests) at the finish line.

**How the last stretch went, for anyone auditing the tail:** every US state
finished (including three small pockets — PA/Pennsylvania, VA/Virginia,
WV/West Virginia, MD/Maryland — that had NOT been part of the original
50-state sweep and were mistaken mid-session for typos/mistags before being
confirmed real and swept in), then every Canadian province/territory with
entries in the corpus: QC (`b9e9647`), ON (`ab0f4a1`), BC/AB/SK/MB
(`7c13487`/`c77030f`), NB (`7fd9441`), NS+PE (`2d49c4c`), NL (`c9535ef`),
and a final 41-entry mixed batch (`7982373`) that closed out the last of NL
plus VA/PA/WV/MD stragglers. **No further `--dump`/`--apply-file` work is
needed for phase 3.** If `--report` ever shows entries again, it means new
campground entries were added to `campgrounds.json` after this pass (a new
sweep, an edit) — treat that as a fresh, much smaller incremental pass using
the exact same loop and judgment calls documented in this file, not as
unfinished phase-3 work.

**Next phase-3-adjacent work (not started):** re-measure `--report` coverage
periodically as new entries get added, and revisit **phase 5** (Good Sam
bulk match) and **phase 6** (more policy-registry rows) per the "Not done"
paragraph below — those were always separate from the note-extraction pass
and remain open.

**Judgment calls settled on the Ontario private-RV-park run (notes
12634-12653), a private/commercial-heavy tail with a recurring "mostly
seasonal but keeps a transient section" pattern:**
- **When a note gives ONE hookup spec that explicitly covers the WHOLE site
  count ("245 sites, all with electric/water/sewer"), use the whole count**
  — even when the note also breaks that same total down by booking category
  (full-season vs. overnight), because the hookup fact and the site count
  both describe the same physical inventory (Petersburg 12648, Killaloe
  12650, Vermilion Bay's Crystal Lake 12651).
- **When a note gives DIFFERENT hookup specs for different named subsets
  (a leased "full-season" block vs. a separate "overnight/traveler"
  section with its own stated hookup type), use ONLY the subset's own count**
  paired with ITS hookup facts — using the grand total would attach the
  transient section's water/electric/sewer facts to sites that were never
  described that way (Midland's Georgian Bay camp 12637: 165 seasonal sites
  left unspecified, 15 hydro/water OVERNIGHT sites described in detail →
  `count:15`, not 180; Powassan's Wasi Lake 12642: 63 full-season sites
  unspecified, 8 RV overnight sites explicitly "no sewer at the overnight
  sites" → `count:8, sewer:false`, not 72).
- **"No sewer at the overnight sites" / "no sewer hookups at the sites —
  there's an on-site dump station" is an explicit negative, not an omission**
  — `sewer:false` (not omitted), `dump:true` when a dump station is named
  separately (KOA Cardinal 12646, same pattern).
- **A named booking SOFTWARE platform not in the enum** (CampLife, ResNexus,
  Good Sam Booking, a KOA/franchise's own booking system) is `platform:
  "operator"` only when it's the SOLE channel named; when the note pairs it
  with "or by phone" (two channels, no clear primary), the standing
  two-channel-omit-platform rule wins even though one of the two is a real
  enum value like `roverpass` (North Bay's Lavase River park 12653: "book
  online through RoverPass or by phone" → platform omitted, not roverpass).
- **The bare "phone/email" exception is narrow — it requires BOTH named
  together with no third channel**, not phone alone or email alone. "Reserve
  by phone" alone → `platform: "phone"`. "Reservations by email preferred"
  alone (no phone mentioned) → platform omitted, doesn't invoke the
  phone/email exception (Vermilion Bay's Crystal Lake 12651).
- **"Reserve by phone/email; no online booking engine"** (stated as the pair,
  no third channel) → `platform: "phone"`, confirmed twice this run
  (Killaloe 12650's sibling notes, Bushwell Bay 12643).
- **"Short-term/nightly camping offered year-round" inside a note that also
  describes a seasonal LEASE program running a shorter window** still earns
  `year_round: true` — the seasonal program's dates describe the lease
  product, not whether the campground itself operates that time of year
  (White Lake resort 12638).

**A second, larger Ontario private-park run (notes 12654-12713) sharpened
the subset-vs-whole-total call from the bullet above — it is genuinely a
judgment call each time, not a fixed rule:**
- **When a hookup breakdown's own subset numbers SUM to (or land very close
  to) the site count actually being used, that confirms the breakdown covers
  the WHOLE inventory being described** — e.g. "192 sites with 30-amp hydro/
  water/sewer and 31 with hydro and water" against a stated "223 sites
  total" (192+31=223 exactly) means the union applies campground-wide, not
  just to a named subsection. Do this arithmetic check before deciding
  whether to use the grand total or carve out a subset.
- **Water/sewer facts sold as an ADD-ON SERVICE rather than a per-site
  connection are NOT a hookup** — "mobile water fill and pump-out sold
  separately rather than site sewer" (12693) or "weekly septic pump-out"
  bundled with power+water (12682) both read as `water:false/sewer:false`
  with `dump:true` (a delivered/collected service), not as a water or sewer
  hookup — the schema's water/sewer fields mean a fixed connection AT the
  site, and a note that explicitly contrasts "at the site" vs "sold
  separately" is doing the work of telling you which one it is.
- **"Sites are assigned on arrival rather than pre-booked" (an all-transient
  park that explicitly does NOT take advance reservations) is `reservable:
  false, fcfs: "always"`**, even though the rest of the note reads exactly
  like every other bookable private park (nightly rate card, full hookups,
  pool) — the operator's own stated booking mechanism overrides the
  default assumption that a private RV park is reservable.
- **"Book by phone/e-transfer" is NOT the phone/email exception** — e-transfer
  is a payment method, not a second communication channel, so this reads as
  a single named channel (`platform: "phone"`), same outcome as the
  exception but for a different reason: read what the second word actually
  names before applying the phone/email shortcut.
- **A named booking-software brand appearing ALONE (no "or by phone")** is a
  clean single channel → `platform: "operator"` (Staylist, ResNexus,
  PitchCamp, KOA's own system, a park's own CampLife listing with no phone
  alternative given) — only demote to "omit platform" when a second channel
  is explicitly offered alongside it.

**BC/AB/SK/MB/NB private-park runs (notes 12714-12894, ~180 entries) were
the same private-RV-park genre as Ontario and confirmed every rule above
holds nationwide with no new exceptions** — same union-across-subsets logic,
same subset-vs-whole-count judgment call, same phone/email narrowness, same
platform-omission-on-two-channels rule. Two additions specific to this run:
- **"Rented as available" / "sites assigned... contact ahead" language for
  an otherwise ordinary private park is NOT automatically FCFS** — only the
  Ontario-style explicit "sites are assigned on arrival rather than
  pre-booked" (a stated absence of advance reservations) earns
  `fcfs: "always"`; "long-stay focus but nightly sites rented as available"
  (Osoyoos Lake resort) still reads `reservable: true` with no fcfs, because
  it describes availability, not booking mechanism.
- **A note with NO reservation language at all — full hookup facts, pool,
  laundry, but nothing about booking — genuinely omits `booking` entirely**,
  rather than inferring `reservable: true` from "this is a private RV
  park" — happened several times this run (12763, 12767, 12790, 12822,
  12880) and is the correct conservative read: private parks that don't
  take advance reservations exist (walk-up FCFS lots), so silence isn't
  evidence either way.
- **"May long weekend" (Victoria Day, a floating Canadian holiday) is NOT a
  day-level date** — omit `opens` rather than guess a specific day, even
  though "Thanksgiving weekend" (mid-October) and named months are common
  in this corpus; only encode a date when the note gives an actual
  day-of-month or an unambiguous "mid-May" style approximation already used
  elsewhere in this project's convention.

**Judgment calls settled on the first Quebec/SEPAQ batch (notes 12474-12533),
where the note style and vocabulary differ from every US batch so far:**
- **Quebec's "N-service" (service/services) tiering has NO fixed universal
  meaning — each note (or family of notes about the same park) must be read
  for its OWN definition, never assumed from a prior park.** Confirmed
  readings seen: "two-service (water+electricity)" appears constantly across
  SEPAQ parks (Presqu'Îles, Frontenac, Gaspésie, Mont-Mégantic, Lac-Saint-Jean,
  Aiguebelle) → `water:true`, electric omitted unless an amp is stated,
  `sewer:false`. "Three-service (full hookup)" appears at several parks
  (Rimouski, Port-Daniel, Ville-de-Québec private park, L'Islet, Île-Melville)
  → `water:true, sewer:true` via the standing union-across-subsets rule. But
  **Lac-Walker's own note explicitly redefines "full 2-service" as
  water+SEWER** (no electric) for that one specific remote reserve — the
  explicit in-note definition always overrides the corpus-wide default.
  When a note gives NO explicit definition, only extend the water+electric
  default when the SAME named park/sector is defined elsewhere in the batch
  (e.g. Frontenac's Saint-Daniel sector, defined once at 12499, reused for
  12501 with no restated parenthetical).
- **A composite entry describing SEVERAL differently-serviced campgrounds/
  sectors under one record (a whole park's frontcountry system, e.g.
  Presqu'Îles' five named campgrounds, or Le Bic's four) gets NO single
  hookup/count value** — extracting one number would misrepresent whichever
  sector wasn't the one meant. Record only facts true of the WHOLE entry
  (a dump station present somewhere, `reservable:true`) and leave hookups/
  sites empty rather than picking one sector's numbers to stand for all.
- **"Unserviced" / "sans service" / "no-service" / "sur l'emplacement" is the
  French-corpus equivalent of the US "no hookups" trigger phrase** — same
  triple `electric:0, water:false, sewer:false` when it's stated as the WHOLE
  record's condition, same omission when it's just one grade among several
  offered at the site (semi-serviced/serviced/unserviced together, no single
  answer for "this entry").
- **Ready-to-camp units (yurts, oTENTiks, Huttopia tents, prospector tents,
  Cool Box micro-cabins, rental chalets) are excluded from `sites.count` the
  same way US walk-in/tent-only sites are** — they're not RV/trailer-capable
  and several notes say so explicitly ("not counted").
- **A pad dimension given as `L x W m` (metric WxL pair, e.g. "12.5 x 10 m")
  is excluded from `max_rig_ft` exactly like the US-corpus pad-dimension
  rule** — but a single-figure metric length WITH a feet conversion already
  supplied in the note ("up to 8 m / 25 ft") is used directly as the feet
  value already given, no conversion arithmetic needed on my part.
- **"Rigs over N ft allowed" (SEPAQ Ashuapmushuan's phrasing) is a floor
  statement like the US "30 ft-plus" cases, not a cap** — omit `max_rig_ft`
  rather than reading N as the maximum.
- **A named third-party regional booking site not in the platform enum**
  (`campin.ca`, a Quebec-wide municipal-campground booking portal) is
  `platform: "operator"`, same treatment as a concessionaire's own site —
  it's a single named channel, just not one of the big enum platforms.
  Reservable via **Parks Canada** (federal, not SEPAQ) still gets NO platform,
  matching the established Parks-Canada precedent from the Alberta run.
- **A remote reserve managed by a named Indigenous corporation/nation for the
  province** (Corporation Nibiischii for Réserve faunique des
  Lacs-Albanel-Mistassini-et-Waconichi) books through that corporation, not a
  SEPAQ portal — `platform: "operator"`, ownership stays whatever the land
  registry says (these are provincial wildlife reserves, not tribal land, so
  don't reclassify ownership on this basis alone).

**A rule this same file stated wrong got applied and then fixed (commit `c0856bc`, ids
10540/10548)** — see the CORRECTED bullet just below. The wrong version wasn't caught by
`audit_extracted_fields.py` (a guessed-but-plausible platform isn't a shape the auditor
flags); it was caught by re-reading the whole file, not just the most recent paragraph,
before the next batch. Do that each time.

**Recurring judgment calls settled during the WA run, worth reusing:**
- **A named hookup SUBSET implies the unnamed utility is absent.** "partial-hookup
  (water/electric)" or "utility (elec/water)" → `water: true`, `sewer: false` (electric
  amp omitted unless a number is given) — the type name IS the inventory, so what it
  doesn't list isn't there. Reserve `sewer: true` for "full hookup" / an explicit sewer
  mention. This reading was applied consistently across ~40 entries; revisit if a
  counterexample turns up (a "partial-hookup" site that turns out to have sewer too).
- **"Non-hookup" / "no-hookup" sites are a fourth trigger phrase** alongside "no hookups"/
  "primitive"/"non-electric" in the doc's list — treated as equivalent (electric 0, water
  false, sewer false).
- **"Pit toilets" and a bare "toilet"/"restroom" (type unnamed) map differently**: pit
  toilet → `vault_toilets: true` (same fixture, different name); a bare "toilet"/
  "restroom" with no type word → omit per the doc's existing flush-vs-vault rule.
- **CORRECTED (was wrong in this file, see below):** two reservation channels named in one
  note (e.g. "by phone or via RoverPass/Hipcamp") do NOT get the third-party platform —
  this bullet used to say pick it over `phone`, which contradicts the SK/MB/ID-era rule
  below ("two channels, no clear primary → omit platform entirely") and caused two real
  extraction errors (ids 10540, 10548; fixed in commit `c0856bc`). The correct rule is the
  one below: omit platform when two channels are named with no clear primary, except a
  bare "phone/email" pair still resolves to `platform: "phone"`.
- **A stated total that doesn't quite match the sum of subcategories** ("40 campsites: 8
  full-hookup, 24 standard, 5 equestrian, 1 hiker/biker" summing to 38) → trust the
  directly-stated total over re-deriving it, since the note author had the real count and
  the category breakdown may have a typo or omitted category.
- **"Open year-round except an annual N-day closure"** (e.g. "except Dec 20-Jan 1") →
  still `year_round: true`, deferring to the note's own words over the literal exception;
  a temporary/one-off closure (construction, fire damage, flood) never sets `year_round`
  either way regardless of duration.

**Judgment calls settled over the Oregon USFS/BLM/OPRD run (notes 10580-10879):**
- **"Max spur X ft" is read as `max_rig_ft`** even though a spur is nominally pad length
  not rig length — this notation is USFS-specific shorthand for the site's vehicle
  capacity, used interchangeably with "max RV/vehicle length" across hundreds of these
  notes, unlike a WIDTH×LENGTH pad dimension (doc's worked example 2), which stays
  excluded.
- **A number followed by an advisory caution about that SAME number is the undercut
  pattern and still gets omitted** — "listed to 40 ft... favor shorter rigs", "posted 20-ft
  cap but... rigs over 19 ft face tight turns", "not recommended for large rigs (max spur
  40 ft)". But a number followed by a DIFFERENT, unrelated caution (rough access road,
  washboard gravel, high-clearance advised) is not an undercut and the figure stands —
  the test is whether the caution is ABOUT the stated length specifically.
- **"Rigs over N ft not recommended" / "not recommended for rigs over N ft" is itself a
  usable max_rig_ft = N** (not an undercut of some other number) when N is the only figure
  in the sentence — it's a negatively-phrased direct statement, not a hedge.
- **Oregon State Parks' "electrical" (or "electrical only") site type, unlike WA's
  "partial-hookup (water/electric)", names NO water** — `water: false, sewer: false` (not
  omitted), because OPRD's own site-type vocabulary is electrical / electric+water /
  full-hookup as three distinct tiers, and a bare "electrical" is the bottom tier.
  "Electric+water" or "electrical with water" sites → `water: true` per the existing WA
  subset rule. Don't confuse this with a vague, non-official "some sites have electrical"
  aside (no tier name) — that stays omitted, unresolved.
- **A firsthand/reviewer-reported rig length ("Campendium reports rigs to ~28 ft",
  "reviewers confirm a 30-ft trailer fits") is usable as `max_rig_ft`** when it's the ONLY
  figure given and isn't contradicted by an official number — same footing as an
  agency-stated approximate figure, per doc's "an approximate figure is still a figure."
  It stops being usable the moment an official figure conflicts with it (then it's the
  undercut/contradiction pattern above, and both get omitted).
- **"No published/posted max length" is an explicit statement, not silence** — omit
  `max_rig_ft` the same as the doc's own "RV length cap not published" worked example,
  don't treat the sentence as just absent information.

**Judgment calls settled over the Oregon county-park / private-RV-park tail (notes
10940-11121), where the note style shifts from federal-forest terse facts to county
parks-and-rec prose:**
- **A record's OWN headline label ("full-hookup RV park", "full hookup sites") carries
  water+sewer even when a later sentence only names the amperage** ("76-80 sites (30/50-amp)"
  under a "Private full-hookup RV park" lead sentence still gets `water: true, sewer: true`)
  — the type is asserted once and the amp clause is just adding detail, not re-scoping it.
  This is different from a bare "X-amp electric" sentence with no headline hookup claim,
  which still gets no water/sewer per the existing WA subset rule.
- **A facility explicitly placed away from the site (\"potable water at nearby Anthony Lake
  CG\", \"dump 5 mi away at Tenmile County Park\", \"restroom a short walk down at the dock\")
  reads the same as the doc's \"dump station ~6 blocks away\" example — false, not omitted**,
  extended from dump stations to `potable_water` and `showers` too: the note is telling you
  where it actually is, which is not here.
- **"Open year-round except [a specific recurring closure]" still needs the note's OWN words
  to say "year-round"** — a schedule that's merely described as open Month-Month even when
  paired with "(regular season ...)" doesn't get `year_round: true` by inference; only take it
  when the note explicitly uses "year-round" (or "24/7 for public camping", equivalent
  wording), consistent with the WA-era rule already in this file.
- **Two named booking channels stayed correctly omitted throughout this tail** ("reserve by
  phone/in person", "reservable online/by phone or FCFS") — the SK/MB/ID-era rule (below)
  held for the whole run once the earlier contradiction was fixed; no further violations
  found on a spot re-check.

**Judgment calls settled over the Nevada / early-Arizona federal-land run (notes
11184-11368), which is almost entirely BLM/USFS/NPS/state-park primitive-to-moderate
campgrounds again, after the OR county-park detour:**
- **The "elsewhere" facility rule (doc precedent: a dump station described as being at
  another named place reads false) extends to `vault_toilets` too**, not just
  `potable_water`/`showers`/`dump` — "vault toilet/water ~1.25 mi at Empire Ranch HQ" got
  `vault_toilets: false, potable_water: false` for the campground itself, the same as an
  off-site dump station would.
- **A seasonal split expressed as two DATE WINDOWS that together cover (or nearly cover)
  the whole year — "Reservable Nov 1-Mar 15... FCFS Apr 1-Oct 31" — still doesn't earn
  `year_round: true`.** Only the note's own literal "year-round" (or equivalent) phrase
  does that, per the standing OR-era rule; don't derive it by adding up two windows
  yourself, even when they visibly sum to ~12 months.
- **A dual/ambiguous stay limit ("7-day/30-day limit", "14-day/28-day limit") is omitted
  from `max_stay_nights`** rather than guessing which figure is the real cap — these
  typically mean "N days per M-day period" and the note doesn't say which number the
  schema's single integer should hold.
- **BLM/NPS boilerplate variants of the undercut pattern keep showing up and the same test
  applies**: "listed max RV 22 ft but firsthand reviews confirm 24-25 ft... fitting" is the
  REVERSE undercut (official number contradicted upward) and also gets omitted — not just
  the "official number contradicted downward by a caution" version documented earlier.
  Both directions of contradiction mean the figure isn't reliable, so both get dropped.
- **A number for one named alternate location or a different loop/campground is not an
  undercut of the number in front of you** — "not recommended for large rigs (max spur
  40 ft)" IS an undercut (same figure, same site); "sites fit ~25 ft (larger rigs use
  Wahweap instead)" is NOT (different named place). Read carefully which noun the caution
  is actually about before dropping a number.

**Judgment calls settled over the Arizona run (notes 11369-11616) — mostly USFS forest
camps, then AZ county/state parks, then a long private-RV-park tail:**
- **"Rigs over N ft not recommended" and "listed max RV N ft" appear constantly as the
  SAME pattern with no caution attached** (unlike the undercut/contradiction cases) — most
  of AZ's USFS camps just state a plain `max_rig_ft` this way, often specifically because a
  switchbacked access road (Swift Trail, Catalina Hwy, Mingus Mtn) caps it well under the
  doc's 23-ft baseline (22 ft shows up dozens of times). Take these at face value; only
  drop the figure when the note itself hedges or contradicts it, not just because the
  number is small.
- **Arizona county regional parks and AZ State Parks & Trails share one hookup pattern
  worth recognizing on sight: "water and electric hookups" with NO water, sewer field
  set true** — sewer stays `false` (or omitted if truly unaddressed) unless the note
  separately says "full hookup" or names sewer/septic explicitly. This is the same
  WA-era subset rule, but it is so dominant across this agency family (Maricopa/Pima/
  Pinal County parks, nearly every AZSP&T entry) that entries naming ONLY "electric"
  (no "and water") get `water: false, sewer: false` too, not just "unaddressed" —
  several AZSP&T entries state "electric only (no water/sewer at site)" outright.
- **A stated hookup type at the PARK/AREA level ("Central Shooter's Campground ~24
  full-hookup...") that then lists per-loop or per-site-range subsets with different
  hookup levels is summed by counting the numbered subsets, same as the doc's
  unambiguous-sum rule** — but the hookup fields themselves take the UNION across
  subsets (if any subset has full hookup, `sewer: true` for the whole record), since
  the schema has no way to say "sewer present at 40% of sites."
- **Private/casino/snowbird RV parks are the cleanest note style in the whole corpus**:
  almost every one states "full hookups (NN/NN-amp, water, sewer)" plainly with no
  hedge, undercut, or ambiguity — the main judgment calls left are pad-dimension
  exclusion (own examples keep appearing: "30x60 concrete pads", "22'x120'" — the
  X-by-Y pair is excluded from `max_rig_ft` regardless of how large the numbers are)
  and the recurring two-channel-booking omission (their own site + Hipcamp/RoverPass
  together, or "online/phone" — still omit platform per the standing rule).

**More conventions settled over the Saskatchewan/Manitoba/Idaho tail of that
run, beyond what the Alberta section below already covers:**
- **Same "province-wide agency portal earns no platform" rule extends to
  SKPP/Sask Parks and Manitoba's goingtocamp**, exactly like Alberta Parks
  and Parks Canada below. `recreation.gov` and `reserveamerica` still get
  named when the note spells one out (or names "ReserveAmerica SKPP" — SKPP's
  own reservation system runs on ReserveAmerica, confirmed by sibling notes
  that spell it out in full next to others that just say "Sask Parks").
- **A note naming TWO concrete channels with no clear primary** ("online/by
  phone", "phone/email or website", "Campspot or by phone", "in person,
  phone, or online") -> `reservable: true` with platform omitted every time,
  even when one of the two is a named enum value — picking one would be a
  guess. Exception: "phone/email" alone (no third "online") still resolves to
  `platform: "phone"`, matching the pre-existing data precedent this was
  checked against.
- **"100% reservable" / "fully reservable" / "reservation only" / "no
  self-registration" / "no FCFS"** -> `fcfs: "never"`, not just `reservable:
  true` — matches the existing "reservations required" -> never convention.
- **A range for any numeric field ("12-18 sites", "25-32 ft", "50-63 sites")
  is always omitted, never split-the-difference** — consistent with the
  existing "skip ranges" rule for counts, extended here to `max_rig_ft`
  ranges too, which came up constantly in Idaho USFS notes citing
  reviewer-reported rig-length ranges.
- **A temporary outage/closure note (wildfire, hazard-tree removal, "no water
  summer 2026", repairs) is never encoded as a permanent `false`** — omit the
  affected keys rather than assert a durable fact about a fixable, dated
  condition. Came up constantly in the Idaho/Alberta forest-service entries.
- **"Book direct" == "reservable via/by the operator"** — both phrasings
  point at the campground's own booking system as opposed to a third-party
  platform, and both map to `platform: "operator"`.

**A long run of Alberta Parks provincial/PRA campgrounds (8826-9005) settled a
few more conventions, all confirmed against already-scanned precedent:**
- **"Walk-in tent sites" are excluded from `sites.count`** unless the note
  itself states a combined total (e.g. "10 sites: 7 walk-in + 3 vehicle" ->
  10; "16 unserviced ... plus 3 walk-in" with no combined figure -> 16). Same
  exclusion as group/equestrian sites. The existing corpus is actually split
  on this (checked both ways), but exclusion is the more common prior pattern
  and the more conservative reading of "total campsites."
- **A subset that stays open/FCFS through the off-season does NOT flip
  `season.year_round` to true** when it's a small minority of the campground
  (a few sites of hundreds) — matches the existing "Loop A FCFS year-round"
  precedent. It only goes to `true` when the note frames the MAJORITY as
  continuous (e.g. "47 of 61 sites powered year-round").
- **`fcfs: "some_sites"`** for an explicit "mix of reservable and FCFS"
  statement, as opposed to `after_cutoff` for a genuine within-season DATE
  switch ("reservable May-Sep, sites 186-195 add FCFS after early Sep").
- **A facility named as being at a DIFFERENT loop/location within the same
  park ("showers available at nearby Lakeview loop", "dump station in nearby
  Lac La Biche") is treated as off-site — omitted or `false`, never claimed
  for the entry being scanned** — same rule as the existing "dump station 6
  blocks away" convention, just extended to showers/potable water and to
  "nearby"/loop-level phrasing, not only literal distances.
- **"Reservable via/by the operator"** (an explicit, singular, named booking
  party — a concessionaire like West Fraser Mills, not a province-wide
  agency) -> `platform: "operator"`. But "Reservable via Alberta Parks" (the
  province-wide portal covering hundreds of parks) still gets **no platform**,
  same as the Parks Canada precedent — the agency itself isn't in the enum
  and isn't a single campground's own system.
- **A temporary 2026 outage note** ("showers/flush toilets closed for repairs,
  alt sani-dump elsewhere") was NOT encoded as a permanent `false` — omitted
  those keys rather than asserting a durable fact about a fixable outage.

**New wrinkle handled in the Parks Canada / Banff / Jasper / Kananaskis batch
(8766-8825):** several notes give `max_rig_ft` only in metres ("RVs/trailers to
10 m"). Converted to feet by arithmetic (10 m -> 33 ft) since the audit script's
own docstring already treats unit conversion as an expected source of "number
not in note" flags (same bucket as "3-week max stay" -> 21 nights). Where a
note already carried a parenthetical (e.g. "8.2m (27')") that number was used
directly rather than recomputed. Also settled: "reservable via/through Parks
Canada" -> `reservable: true` with **no** platform (Parks Canada isn't in the
platform enum and isn't a third-party channel to point at) — matches
already-scanned entries 8265/8573. A season that is reservable in the main
window and FCFS in the shoulder (or a summer/winter-loop split covering the
whole year) -> `fcfs: "after_cutoff"`, matching the existing USACE/USFS
"reservable in peak season, FCFS off-peak" convention already in the data.
The API account ran out of credit at 7,544 (AWH 2026-09-15: "we won't be getting more API
credits for the time being"), so the last 482 were done by reading the notes in-session and
feeding them back through `--apply-file`. **To resume, with or without credits:**

    ./extract_fields.py --report                        # free, what is left
    ./extract_fields.py --limit 4700 --workers 16       # with API credit
    ./extract_fields.py --dump 60                       # without: read them yourself,
    ./extract_fields.py --apply-file proposals.json     #   same validation + write path

Nothing is half-done and there is no cursor to repair — `--dump` always returns what is
still queued. Coverage at the pause: hookups 48%, booking 45%, sites 45%, facilities 35%,
season 17%. Everything is committed and deployed to PA through commit `d62464d`; the ten
hand-extracted batches after that are committed locally but **not yet pushed**.

**Quality was checked, not assumed.** `./audit_extracted_fields.py` re-reads every derived
value against its own note; it flags ~5% and the flags are overwhelmingly benign (the doc and
the script's own docstring list which). It found exactly one real error in the first 3,675
numbers — a "15-amp electric only" rounded up to the enum's 20 — now fixed, with the rule
"never round up to reach an allowed value" in the prompt. The hand pass shows the same flag
profile as the API pass, so the two are interchangeable in quality.

**One judgement call applied uniformly** and worth revisiting if it looks wrong: where a note
says "individual sites first-come, first-served; group sites reservable", the entry gets
`reservable: false` / `fcfs: always`, because an RVer looking for a site cannot reserve one.

### Resuming the hand pass on another machine (written 2026-09-15 for the next session)

Assume **no API credit**. The loop is two commands per batch, and it is stateless — just
start it:

    ./extract_fields.py --dump 60          # read the 60 notes it prints
    ./extract_fields.py --apply-file <path to your JSON>   # then: git add -u && git commit

**Read `SYSTEM` in `extract_fields.py` before the first batch and follow it literally.** It
is the same prompt the API pass used and nearly every rule in it is a mistake that was made
and caught. The ones that come up constantly:

- **Absent is unknown.** Emit a key only when the note says it. Most entries yield two or
  three keys, and `{}` is a fine answer. Never write `false` for "not mentioned".
- `electric` is one of 0/20/30/50 and **nothing else** — "electric sites" with no amperage
  OMITS the key; "50/30-amp" is 50; "50 & 60-amp" is 50 (highest ALLOWED value genuinely
  offered); "15-amp only" omits it (never round up to reach an allowed value).
- "full hookup" = water+sewer true, electric only if the amperage is stated.
- "no hookups" = electric 0, water false, sewer false. "primitive"/"non-electric" = electric 0.
- A **dump station is not a sewer hookup**, and "dump station ~6 blocks away" / "sani-dump nearby" is `dump: false` (the note says it is elsewhere). Committed data is inconsistent here (18 false vs 25 omitted as of 2026-09-16).
- `max_rig_ft`: an approximate figure is still a figure ("rigs to ~45 ft" -> 45). Omit only
  when the note UNDERCUTS its own number ("max ~40 ft, tight spacing, best for smaller rigs")
  or gives a bare range ("24-32 ft"). A pad dimension ("40x15") is not a rig limit.
- `platform` only when the channel is NAMED. A bare "reservable online" names none.
- `season.opens/closes` for day-level dates, **tilde included** (AWH 2026-09-16: "~Apr 15-Oct 15" shifts a little each year, often to a weekend, but it still says the place is shut in December). Omit alternatives ("Apr 15/May 1") and month-only; a stated season with no dates still gives `year_round: false`. Only 6 of the first 250 scanned tilde-date notes got dates under the old rule.
- **Sonnet is fit for this** (2026-09-16 blind re-run of 8585-8644: 398/427 values agreed, a similar number of clear errors on each side). Spot-check a batch against the committed data now and then.
- Counts: use a stated total or an unambiguous sum; skip ranges ("128-130", "~18-22").

**Practicalities:** batches of 60 cost roughly 20K tokens round-trip and one commit each;
write the JSON with a heredoc to a scratch file, not into the repo. Run
`./audit_extracted_fields.py` every several batches — a ~5% flag rate in the known-benign
categories is normal and healthy; a NEW category appearing is the signal to stop and look.
`python -m unittest tests.test_extract_fields` needs no API and no network.

**Not done:** Good Sam bulk match (phase 5); more registry rows (phase 6); manage-table sort
on the new fields; the NL corridor search that started the whole thread (deliberately
tabled).

**RIDB hookups pass DONE 2026-09-18** (`recgov_hookups.py`, doc §7): stable after two same-day
corrections (host/staff-pad rules, placeholder catalogs) — electric coverage 57.7% -> 63.7%.
Per AWH, rec.gov wins over sweep notes, and 29 contradicting note phrases were REMOVED (no
explanation added). Tortilla (AZ, all 76 sites water+sewer yes vs note "no hookups") is the one
catalog value worth doubting. The cache also holds Driveway Length / Entry / Max Vehicle Length
per site for a future `sites` pass (max_rig_ft, pull_through) — no refetch needed.

**`wma:VA` registry row added 2026-09-18** (28 rows now), from AWH's question about VA WMA
permits: no camping fee; DWR Access Permit $4/person/day as `fees.entrance` per person_day
(17+, exempt with a VA hunting/fishing/trapping license or boat registration); a daily permit
covers only its own date, so an overnight needs one for BOTH days (read from the wording,
DWR doesn't state it outright); the camping authorization is ONE PER PARTY of up to 6, stored
as `prereq_pass` with NO price because it goes free -> $10 on 2026-10-01 (the note gives both).
Annual permit $23 -> $28 the same day. The `prereq_pass` chip now names the pass.

**HOOKUPS FILTER SHIPPED 2026-09-18** (doc §8.5 has the design): Any / Electric /
Electric + water / Full, one shared "include unknown" switch for both filters, three
booleans inline. ~42-51% of the map fades depending on level, spread across all ownership
classes — AWH hasn't reacted to that yet; if it bothers him, the answer is MORE DATA (RIDB
per-campsite attributes for federal hookups; phase 5 Good Sam for private), never hiding
the unknowns. Facilities (showers 29%) and season (30%) were too thin to be next.

**(Superseded — kept for the reasoning) Next: more map filters, and RE-MEASURE COVERAGE FIRST.** The rating filter shipped the same
day on the argument that everything else was at 0%; phase 3 is falsifying that, so the choice
of the next filter has to be re-derived from `extract_fields.py --report` rather than from
anything written here. Doc §8.5 has the shape and §2.2 the rule that makes it non-trivial
(an unknown value is shown and flagged, never filtered out); §8.4 caps what may ride in the
inline marker payload. After that: phase 5, phase 6.

**Priority came from joining `trips.json` against `campgrounds.json` by nights slept**,
not entry count — that is what put PA/MD/VA ahead of MI/CA. Re-run that join before
picking the next rows — **`./policy_priority.py`** (committed 2026-09-15, read-only, no
args) is that join, and doc §5 names it. **Two traps it exists to hold:** `is_home_stay()`
reads `stay["place"]`, which only `parse_trips()` materializes (raw `trips.json` records
give a silent False and 23 home nights in the denominator), and family-kind entries carry
no `ownership`, so 47 driveway nights land in a bogus bucket unless excluded.

**The nights signal is now spent, as of the 2026-09-15 run.** Every row above the best
remaining agency is `private:*` / `hipcamp:*` / `local:*`, which doc §5 says to leave alone,
and the agency rows left are at 2 nights or fewer: `state:MA` (2 nights, 22 entries),
`state:GA` (1, 53), then nothing. So the next rows should be picked on **entries** or on a
trip actually being planned — `state:OR` (55), `state:GA` (53), `provincial:MB` (53),
`state:OK` (52), `provincial:SK` (52) lead that ranking; 961 entries across 34 rows remain.

**Realistic ceiling is ~52%.** `local:*` rows are mostly dead ends (`local:IA` is 245
entries across 245 different counties); Suffolk County worked only because it genuinely
is one authority.

**Watch items — schema gaps deliberately left open**, each seen once and awaiting a
second instance before extending the vocabulary: Hither Hills' one-reservation-per-
household peak-season limit; Virginia's non-resident surcharge scaling by site type
($5 standard → $8 full hookup); BC's maximum stay being per calendar year rather than
per visit.

**WV is the third row that could not state a booking window** (after IA's contradicted
cutoff and PA's absent non-resident rate), and the first with NO published rates at all —
West Virginia puts every number inside its Inntopia booking engine and nothing on the web.
The pre-online brochures still served from `wvstateparks.com` are the trap: they describe
held-back FCFS sites and a two-days-prior cutoff the current system contradicts, and a
search engine will hand you both as current.

**Unresolved:** Iowa's two official pages contradict each other on the booking cutoff,
and its post-cutoff FCFS is uncorroborated — resolve by phone. Florida's site 403s
automated fetch so its row is `method: reported`, not verified.

**Verifying map UI with no browser extension:** headless Firefox takes screenshots
(`firefox --headless --profile <scratch dir> --screenshot out.png --window-size=W,H <url>`)
— the separate profile is REQUIRED or it refuses while the user's own Firefox is running.
Log in for the shot by adding a temporary entry to `trip_data/share_tokens.json` and hitting
`/s/<token>?next=/campgrounds/map`: one GET authenticates and lands on the page, where a
password login cannot. Back up and restore both that file and `users.json`, and diff them
afterwards. A non-default control state (a filter already applied) is reachable by
temporarily editing the `STORE.get(..., default)` in the template, screenshotting, and
reverting.

**Judgment calls settled over the California county/district-park and fairgrounds run
(notes 11738-11860):**
- **California county-park and regional-park-district prose reads exactly like Arizona's:
  a named subset ("water/electric hookups", "many with water/electric hookups") implies
  `sewer: false`**, and a "full-hookup" mention (even for only a subset of sites, e.g. "18
  full-hookup, 78 non-hookup") gets the whole record `water: true, sewer: true` per the
  existing union-across-subsets rule — this pattern is now confirmed dominant across CA
  county/district parks (East Bay Regional, Santa Clara/San Mateo/Sonoma/Solano/Riverside/
  San Bernardino/Stanislaus county parks) as well as AZ.
- **County-fairgrounds RV parks often state a max-stay-then-cooldown cycle** ("28-day max
  stay then a 10-day break", "14-day max continuous stay, 28 days/year") — the FIRST
  number (the continuous-stay cap) is what goes in `max_stay_nights`; the cooldown/annual
  cap isn't a schema field and is dropped.
- **PG&E-operated recreation land (Lake Pillsbury, Butte Valley Reservoir) stays classed
  private** by the existing utility-land convention, same as OR/WA PUD parks.
- **A posted vehicle-length maximum survives even when a pad dimension is given right next
  to it** ("posted vehicle max ~22 ft (pads ~12x25 ft)") — the pad WxL pair is still
  excluded per the standing rule, but the separately-stated posted max is a normal usable
  figure, not the excluded pad number.
- **A firsthand rig-length note for a DIFFERENT subset of sites at the same campground
  doesn't undercut the stated figure for the sites actually being described** ("RVs/
  trailers to 30 ft use sites 1 and 6-10; sites 2-5 not recommended for trailers" → 30 ft
  stands; it's a which-sites-fit distinction, not a caution about the 30 ft number itself).
  Likewise "best for rigs to ~24 ft (pull-through sites 7 and 10 take larger)" keeps 24 ft
  — the exception carves OUT specific sites rather than casting doubt on the figure.
- **A single vague "hookups available" or "some sites have hookups"/"many with hookups"
  with no water/electric/sewer word at all stays fully omitted** (not even `water: true`)
  — this is stricter than the named-subset rule above, which requires at least one
  specific utility word (water, electric, sewer, or "full hookup") to trigger a value.

**Judgment calls settled over the Sierra/southern-CA USFS+NPS forest-camp run
(notes 11861-12100), the densest run of primitive vault-toilet camps in the
whole corpus:**
- **A "walk-in"/"tent-only" subset named alongside a total is subtracted from
  the total to get the RV-usable `sites.count`** ("19 sites (7 tent-only)" →
  12; "88 sites across several loops (incl 19 tent-only)" → 69) — extends the
  standing walk-in-exclusion rule to an explicit subtraction when the note
  gives both numbers, rather than just omitting a combined figure.
- **An equestrian or double/triple/quad subset named alongside a total is
  KEPT in the count** (unlike walk-in/tent-only) when the note frames it as
  part of one general campground ("19 sites (three equestrian)" → 19; "12
  sites (single/double/triple/quad)" → 12) — the distinction is whether the
  subset is still a drive-in vehicle site (equestrian, multi-unit) or not
  (walk-in, tent-only).
- **"RVs over/rigs over N ft not recommended" is a direct usable max_rig_ft =
  N** (confirmed again dozens of times this run, AZ's original pattern) —
  but **a reviewer's or agency's OWN N-ft rig succeeding is reinforcement,
  not an undercut**, distinct from a caution ABOUT that number: "RVs to ~22
  ft (a reviewer drove an 18-ft rig in without incident)" keeps 22 ft, same
  logic as "some 35-ft rigs reported" keeping a stated 30 ft cap.
- **A number for a specific NAMED SUBSET of sites (the largest site, "site
  003", the sites that take trailers) is usable as `max_rig_ft` for the
  record** even when most sites are smaller — the field means "the longest
  rig that fits somewhere," so "largest RV site fits 30 ft (site 003)" or
  "7 with trailer space, max ~33 ft" both give a clean number. This is
  different from a bare RANGE ("18-34 ft", "28-45 ft"), which still gets
  omitted per the standing rule.
- **A closure window stated as calendar dates ("may close Nov 1-Apr 30 under
  MVUM") is convertible to a season the same way a stated open-window is** —
  `year_round: false`, `opens`/`closes` set to the complement of the closure
  (Nov 1-Apr 30 closed → opens 05-01, closes 10-31). Same footing as reading
  an explicit open-window directly.
- **"Dump station/water in the village" / "... in Cedar Grove" (the named
  developed area the campground itself sits within, not a different park)
  still reads as off-site (`false`), not on-site** — extends the "elsewhere"
  rule to a shared area-wide facility serving several campgrounds, not just
  a differently-named location.
- **A temporary "no water/no running water for the 2026 season" notice is
  never encoded as a permanent `false`** — omit the key, consistent with the
  standing temporary-outage rule; came up repeatedly in this NF-heavy run
  (Fish Lake, Dillon Creek, Highway 20 Pioneer Trail).
- **A stated per-park closure that is itself just a one-time current-year
  event ("recreation.gov shows it temporarily closed for hazard-tree
  removal")** is likewise not encoded into `season` — that field is for the
  recurring annual pattern, not this year's outage.
- **Group/reservable-only sites named alongside FCFS individual sites are
  excluded from BOTH the count and the booking read** — the record describes
  the individual sites being scanned, so "individual sites FCFS (group site
  reservable online)" still gets `reservable: false, fcfs: "always"`, same
  as the existing "individual FCFS, group reservable" convention, now seen
  dozens more times without exception.

**Judgment calls settled over the BLM-desert/USACE-reservoir/private-park tail
that closes out California (notes 12342-12408):**
- **BLM LTVA (Long Term Visitor Area) permit systems are not a `booking`
  fact** — "$180 long-term Sep15-Apr15 / $40 short-visit" is a fee-permit
  scheme, not a reservation or FCFS system, so `booking` is left out entirely
  rather than guessing `reservable`/`fcfs` either way. Facilities actually
  present (dump station, showers, water) are still recorded normally.
- **"RVs/trailers to N ft and up" or "accommodates 30 ft-plus RVs" states a
  FLOOR, not a cap, and is NOT usable as `max_rig_ft`** — the field means the
  longest rig that fits, and a phrase describing the shortest rig a site
  guarantees says nothing about the upper limit. Distinct from "sites over
  90 ft" language used to advertise big-rig capacity (private RV parks), which
  IS usable as a (large) `max_rig_ft` since it's marketing the site's actual
  length capacity, not just a minimum.
- **A private RV park's own booking phone line is `platform: "phone"`**, not
  `operator` — reserve `operator` for a distinguishable NAMED third-party or
  concessionaire system; "reserve by phone" at a small family-run park is the
  phone rule, confirmed dozens of times across this Bakersfield/Tehachapi/San
  Diego-backcountry private-park run.
- **"Full/partial hookup" stated together with no other detail still reads as
  the union rule (any full-hookup subset present → water+sewer true for the
  whole record)** — same as the standing AZ/CA-county convention, now
  confirmed for private parks too.
- **Two booking channels named for a resort-scale private park ("reservable
  online or by phone") still gets platform omitted**, same as the federal-
  land rule — this shows up on the biggest private parks in the corpus
  (482-site Desert Hot Springs resort) and the rule holds without exception.

**PHASE 5 (Good Sam) DONE 2026-09-20** — `goodsam_discounts.py`, rules in doc §7. 1,784
entries written: `good_sam` 336 true / 1,326 false, `military` 757 true. Three things this
file should carry that the doc says more briefly:

- **The doc's own premise was wrong and that is the reusable lesson.** §4.4 had said
  presence in the Good Sam Algolia index effectively IS the network flag. It is the whole
  printed directory — 14,993 campgrounds including national forests — and `isGsPark` is on
  1,896 of them. Checking the claim cost one query and changed the answer by 8x. The pattern
  is [[feedback-absent-is-not-unknown]] wearing a different hat: a source that lists
  something is not asserting the thing you want.
- **The subset guard is the one rule to keep if the matcher is ever rewritten.** Name
  similarity scored 1.00 on `Camp Eagle Nest` vs `Eagle Nest Lake State Park` (1.7 km),
  `Rufus RV Park` vs `Rufus Landing Recreation Area`, `Thousand Trails Crescent Bar` vs
  `Crescent Bar Recreation Area` — a private park's name contained in a public one's, three
  times, each writing a discount onto a public campground. Containment is not identity; past
  the close band a match must be WHOLE (token sets equal, or spelling/punctuation apart).
- **Coverage is the ceiling, not the matcher.** Only 336 of 1,896 network parks reached an
  entry, and 1,267 of the misses have no entry within 3 km — AK (out of scope) plus the
  membership/residential parks [[feedback-exclude-seasonal-residential]] deliberately keeps
  out. Don't read the ratio as a matching failure.

**Where it stands after phase 5.** Coverage: rating 92.2%, hookups 84.3%, booking 80.4%,
sites 78.3%, facilities 63.2%, season 30.5% (all note-derived — the rec.gov CALENDAR walk
of §7 phase 4 has never been run at scale, and per [[reference-recgov-calendar-limits]] it
must ACCUMULATE across runs months apart, so starting it early is worth more than starting
it well). `discounts` now 13.9%. Remaining: phase 6 registry rows (30 rows / 45.3% of
entries after `state:GA` and `state:MA`, 2026-09-20; 31 agency rows and 857 entries left,
**all now at ZERO nights slept** — the nights signal is spent, so `policy_priority.py` says
pick by entry count (state:OR 55, provincial:MB 53, state:OK 52, provincial:SK 52,
provincial:QC 47, state:UT 44 ...) or by a trip actually being planned) and phase 7.

**`state:SD` (2026-09-20) was REPORTED, not checked, and re-doing it moved five things** —
the 90-day window is 90 days *except Custer at a year*, four parks cannot be reserved at all,
same-day booking exists at exactly two campgrounds, the $10 non-resident charge is a per-SITE
BOOKING FEE (the registry's first `nonresident.per: "stay"`), and the park entrance licence —
which camping fees never include, $10/$15 daily, $40/$60 annual, Custer's own $25 seven-day —
was missing entirely. `policy_priority.py` counts a reported row as covered, so **read
`method` before trusting a row's silence**; several early rows are still `reported`. SD's park
pages publish per-park rates ($16 basic / $23 modern + a flat $7 electrical fee), so 57 entries
got their own figures, the 8 Custer campgrounds their own tier/window/closing dates, and the
State Fairgrounds `policy_ref: "none"` (state-owned, run by the Fair).

**`state:MA` (2026-09-20) is the template for a state that publishes per-campground data.**
DCR names every campground in its fee table and its season schedule, so the row got the
shape and the 22 ENTRIES got their own rates and dates (doc §3, §5.1). It also added
`fees.surcharges.water` — Salisbury and Scusset sell water ($4) and electric ($6) separately
on one site. MA's non-resident rate is ~3.2x the resident one ($17->$54 inland, $22->$70
coastal), charged as the CAMPING rate so no pass avoids it, which is what AWH's Loraine note
("High surcharge for out-of-state") was about. A Good Sam map
filter was NOT added — 13.9% coverage is far below the 76-90% that justified the rating
filter; re-measure before choosing the next one.

See [[feedback-absent-is-not-unknown]], [[feedback-responsive-all-screens]],
[[reference-recgov-calendar-limits]] and [[reference-js-testing-without-node]] (how the
shared JS was verified with no browser — the rating filter's tests lift the predicates
verbatim out of the template and run them in quickjs against the real file).
