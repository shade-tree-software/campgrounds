# Waterfront audit (multi-state)

This folder's instructions + apply script serve **two** purposes:

1. **Re-audit** of legacy `waterfront` values that predate the evidence gate
   (commits 4f3160e / 9c28772) — COMPLETE, see below.
2. **New-state sweep stage** (current standard): most states from here on are
   added fresh with little/no prior data, so the audit is folded into the sweep
   instead of run later. Add entries with `waterfront: "not waterfront"` as a
   placeholder, then run these same subagents over the new ids and apply — so
   entries land correctly marked the first time. The per-state sweep pipeline is
   in `CLAUDE.md` ("Waterfront audit is a built-in sweep stage"); the mechanics
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

1. Extract the state's entries to audit and split into batch files of ~8:
   `{id, name, location, waterfront, ownership, website}` per entry, written to
   `/tmp/<st>_batch_<n>.json`. **Optimize the seam:** when the entries were just
   added in the same session, carry forward the research pass's per-entry
   waterfront `lead` object (`{map_url, water_body, candidate_sites, note}`) into
   each batch entry so the audit verifies the already-found per-site map instead
   of re-discovering it (see the "Lead packet" section of
   `waterfront_audit_instructions.md`). The lead is a head start, never a verdict
   — the satellite look stays mandatory and the gate still decides.
2. Fan out subagents (waves of ~5; one batch each). Each agent gets:
   "Read audit/waterfront_audit_instructions.md and follow it exactly. Your
   batch file is /tmp/<st>_batch_<n>.json. Return ONLY the JSON array."
   The instructions make the satellite look mandatory/asymmetric, default down,
   and require a one-line evidence string per entry. Tell agents to keep Esri
   export requests at size=1000,1000 or smaller (one agent died on a >32MB fetch).
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
- **In a new-state sweep this is recorded at ADD time** (the research agent emits `inclusion_evidence` since it already vets keep/drop) — no separate pass needed. The standalone subagents here are for **retroactive** re-vetting of states added before that discipline. **PA was the pilot** (2026-06-25): 169 entries audited, 11 removed (5 cabins/day-use/tent-only state parks, 3 under-20ft state-forest sites, 1 hike-in, 1 defunct, 1 unconfirmable FCFS). See `../CLAUDE.md` "Inclusion (validity) audit is a built-in sweep stage".
