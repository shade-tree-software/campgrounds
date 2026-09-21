# Waterfront audit (multi-state)

This folder's instructions + apply script serve **two** purposes:

1. **Re-audit** of legacy `waterfront` values that predate the evidence gate
   (commits 4f3160e / 9c28772) — COMPLETE, see below.
2. **New-state sweep stage** (current standard): most states from here on are
   added fresh with little/no prior data, so the audit is folded into the sweep
   instead of run later. Add entries with `waterfront: "not waterfront"` as a
   placeholder, then run these same subagents over the new ids and apply — so
   entries land correctly marked the first time. The per-state sweep pipeline is
   in `../docs/campground-curation.md` ("Waterfront audit is a built-in sweep stage"); the mechanics
   below (batching, subagent prompt, apply, commit) are identical for both uses.

Re-audit scope (purpose 1): all entries with `waterfront != "not waterfront"`
whose `note` is NOT tagged `--AWH` (those are firsthand-confirmed), and that are
NOT named/described as dispersed (per AWH 2026-06-10: skip dispersed sites).
Worked eastward from IL. **Git log is the progress record** — look for
"Audit all NN <ST> waterfront designations" commits to see which states are done.

**COMPLETE (2026-06-11).** Done: MO, IL, IN, KY, OH, WV, PA, NY, plus the
scattered remainder (NJ, VT, MD, VA, FL, RI, ME, AL, NH, MA, CA, MN, TN, DE —
33 entries, one combined commit "Audit the remaining 33 waterfront
designations"). Every pre-gate designation has been re-verified; per-entry
evidence lives in the audit commit messages.

**KS (2026-06-11):** different case — the whole KS state/federal/local/private
set was added fresh this session with `waterfront` deferred to `not waterfront`,
then run through this same satellite/per-site-map gate as a forward audit (not a
re-audit). 128 water-adjacent candidates audited (30 pure in-town / fairground
parks left `not waterfront` without a look); 28 changes, 13 coord fixes. Commit
"Audit all 128 KS waterfront designations against the evidence gate" carries the
per-entry evidence. This established the new-state sweep stage (purpose 2 above)
as the standard going forward.

## Per-state workflow

1. Extract the state's entries to audit and split into **one-entry batch files**
   (see the batch-size note below):
   `{id, name, location, waterfront, ownership, website}` per entry, written to
   `/tmp/<st>_batch_<n>.json`. **Optimize the seam:** when the entries were just
   added in the same session, carry forward the research pass's per-entry
   waterfront `lead` object (`{map_url, water_body, candidate_sites, note}`) into
   each batch entry so the audit verifies the already-found per-site map instead
   of re-discovering it (see the "Lead packet" section of
   `waterfront_audit_instructions.md`). The lead is a head start, never a verdict
   — the satellite look stays mandatory and the gate still decides.
2. Run subagents SEQUENTIALLY, one batch each, one agent at a time — parallel
   batches hit the session limit and lose work; parallelize only on an explicit
   per-stage user OK. Each agent gets:
   "Read audit/waterfront_audit_instructions.md and follow it exactly. Your
   batch file is /tmp/<st>_batch_<n>.json. Return ONLY the JSON array."
   The instructions make the satellite look mandatory/asymmetric, default down,
   and require a one-line evidence string per entry. Tell agents to keep Esri
   export requests at size=1000,1000 or smaller (one agent died on a >32MB fetch).
   **Batch size: ONE entry per agent** (AWH 2026-09-15; this file said ~8 until
   then). A batch is all-or-nothing — if the session limit lands mid-run, every
   candidate in it is lost — so the batch size sets how much work a single bad
   moment can destroy. Measured: one add-stage research agent handling 7 WV
   campgrounds consumed **half a session** without returning, which is half a
   session a limit one minute later would have taken with it. Sequential fixes
   the collateral damage from parallel failure; small fixes the other half,
   where a huge sequential batch never offers a safe place to stop. The cost is
   real and accepted: the instructions file and the WebFetch/WebSearch load are
   paid once per batch, so more batches burn more in total. Granularity is the
   point, throughput is not. **Persist each agent's JSON the moment it returns**
   — a checkpoint that lives only in the conversation dies with the session
   exactly like in-flight work. The measurement came from the ADD stage, which
   is much the heavier of the two (many fetches per candidate against this
   stage's satellite look plus maybe one map); if AWH ever wants to ramp back
   up, the waterfront audit is the place to try it first.

3. Consolidate agent outputs into one results JSON array, then apply with
   `python3 audit/apply_waterfront_audit.py <results.json>` — surgical text edits
   (waterfront / location / elevation_meters by id, **plus the `waterfront_evidence`
   field from each result's `evidence` string**), never a re-dump; validates with
   `json.load` and verifies every change before writing.
4. The `waterfront_evidence` JSON field is the durable per-entry audit record
   and the SINGLE thing to check: non-empty == audited, empty/absent == not
   audited (no need to also scan the `note`). Firsthand owner audits (`--AWH`)
   were backfilled with an evidence string on 2026-06-17; keep that invariant
   for any new `--AWH` call. Echo the per-entry
   evidence in the commit message too (MO/IL/IN-style: summary buckets + a line
   per audited entry) for convenient `git log` grepping, but the field — not the
   commit — is the source of truth. (Evidence was migrated out of commit messages
   into the field on 2026-06-17 via `audit/migrate_evidence_to_json.py`, after a
   GA stage shipped unaudited because the commit-only record was easy to skip.)

## Findings pattern so far (MO, IL, IN, KY, OH, WV, PA, NY)

- ~40-50% of pre-gate designations change, almost all downward.
- ~Half of audited entries had mis-pinned coords (park office, entrance road,
  day-use area, open field). Agents repin onto the campground loop and refresh
  elevation from Open-Meteo; apply script writes both.
- Upgrades are allowed only with counting evidence (legible satellite pads at
  waterline, per-site map, rec.gov shoreline flags) and do happen (~2-4/state).
- USACE campgrounds usually confirm via rec.gov per-site "Lakefront" flags;
  state parks usually downgrade (loops inland of the lake they're named for).

---

## Inclusion (validity) audit — sibling tool

Separate from the waterfront audit: verifies an entry is a **real, currently-operating, drive-in RV campground fitting a 23-ft rig** (catches cabins-only / tent-only / hike-in / group-only / day-use / fairground-event-only / membership / residential-seasonal / closed / under-23ft / duplicate). The waterfront audit does NOT check this.

- **`inclusion_audit_instructions.md`** — subagent gate. Authority = operator/agency page + reservation-system per-site site-type list; aggregators inflate cabin/day-use parks into fake "RV sites" — never keep on an aggregator alone.
- **`apply_inclusion_audit.py <results.json>`** — stamps `inclusion_evidence` on `keep` verdicts; **reports** `remove`/`review` candidates without auto-deleting (human reviews the remove list before excising; check `trip_data/` for `campground_id` refs first).
- Durable record: the **`inclusion_evidence`** JSON field (non-empty == validity-audited & confirmed keep).
- **In a new-state sweep this is recorded at ADD time** (the research agent emits `inclusion_evidence` since it already vets keep/drop) — no separate pass needed. The standalone subagents here are for **retroactive** re-vetting of states added before that discipline. **PA was the pilot** (2026-06-25): 169 entries audited, 11 removed (5 cabins/day-use/tent-only state parks, 3 under-20ft state-forest sites, 1 hike-in, 1 defunct, 1 unconfirmable FCFS). See `../docs/campground-curation.md` "Inclusion (validity) audit is a built-in sweep stage".

## The federal gap list (RIDB), 2026-09-21

Every per-state sweep marked COMPLETE is complete **against RV Life**, whose
index silently omits real agency campgrounds. `audit/ridb_gap_2026-09-21.json`
is the mechanical federal cross-check: 585 RIDB campgrounds with no entry in
`campgrounds.json`. See `reference_rvlife_index_has_gaps` for how it was
measured and `reference_ridb_gap_pipeline` for how to work it.

- **`ridb_gap_triage.py`** — `--fetch` pulls each facility's record and
  per-campsite catalog (cache `trip_data/ridb_gap_cache.json`, gitignored);
  `--report` is free; `--write <out>` refreshes the work list. Five verdicts
  and only `no_rv` is a drop — `thin`, `mgmt_only` and `no_catalog` are three
  different kinds of *unknown* and folding any of them into `no_rv` drops
  campgrounds the catalog never described.
- **`sat_look.py`** — stitches Esri imagery around a facility and plots its
  campsites' own coordinates with a scale bar, which is what lets the
  waterfront gate's mandatory look work under canopy. `-z 18 --span 1` to
  settle a close call. **Verify every pin by finding the loop in the image:**
  Zapata Falls' RIDB coordinate is at a highway junction 600 m away and was
  not flagged `coord_suspect`.
- **`ridb_gap_<ST>_decisions.json`** — one per state worked, recording added /
  excluded / dropped and *which kind of no* each was. The triage reads these,
  so progress lives in the data and `--report` always says what is left.

State of play: **AR and CO done (26 of 178 `likely_rv`), 152 to sweep**,
heaviest CA 36, OR 23, UT 16, OK 14. The **182 `no_catalog`** rows (FS 113,
BLM 63) need a different method entirely — no per-site data means no size
gate and no inclusion evidence from the catalog, so they are closer to a
conventional sweep than to what AR and CO were.
