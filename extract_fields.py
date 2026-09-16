#!/usr/bin/env python3
"""Read structured fields out of campground note prose (doc §7 phase 3).

The notes are the richest thing in `campgrounds.json` and the least searchable.
Roughly a third of them name a toilet type, a site count, a season or a booking
channel in plain English — facts the schema can hold but nothing can filter on
while they live in a sentence. This pass reads each note once and writes what it
actually says into `hookups` / `sites` / `facilities` / `season` / `booking`.

**Extraction is additive: the note is never touched** (doc §6). The structured
fields are an index derived from the prose, not a replacement for it — "longer
rigs may curb-park (32-ft limit suggested)" has no field, and gutting the note
to populate one would lose it permanently. The single exception to that rule,
the templated RV Life tail, was phase 2's job and is already done.

Three rules carry most of the design:

**Absent is unknown** (doc §2.1). The model writes a key only when the note
SAYS so. It never writes `false` for "not mentioned" — and the difference is not
cosmetic, because the map filter shipped for phase 2's fields treats a missing
key as "cannot rule out" and a present `false` as a checked fact. One careless
default here is indistinguishable from twelve thousand verifications.

**A human always outranks this.** A group whose `provenance` says `manual` or
`reported` is never overwritten, however confident the model is.

**Every run is resumable and every batch is durable.** The work is chunked, each
chunk is written to disk before the next one starts, and progress lives in the
data (`note_scan`) rather than in a cursor file — so an interrupted run resumes
by simply being run again, and a killed process loses at most one batch.

Run it in small pieces and commit between them:

    ./extract_fields.py --report                 # what is left, costs nothing
    ./extract_fields.py --limit 20 --dry-run     # see what it WOULD write
    ./extract_fields.py --limit 200              # do 200, write as it goes
    git add -u && git commit

Needs `ANTHROPIC_API_KEY` (the repo's .env carries it) and `pip install
anthropic`. `--dry-run` still calls the API — the proposals are the thing worth
looking at — it just writes nothing.
"""

import argparse
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import os
import re
import signal
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import campground_schema as cs  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
CAMPGROUNDS_JSON = os.path.join(ROOT, "campgrounds.json")

MODEL = "claude-opus-5"
MAX_TOKENS = 8000

# Notes per request. Small on purpose. A batch is the unit of durability — it is
# written to disk before the next one starts — so a big batch risks more work on
# a kill, and the per-call overhead it would save is already paid for by caching
# the system prompt. 12 notes is ~1,200 tokens in and ~700 out.
BATCH = 12

# Default cap per RUN, so an unattended invocation cannot turn into an hour-long
# job that is awkward to stop and awkward to commit.
DEFAULT_LIMIT = 200

# Batches in flight at once. The run is latency-bound — almost all of its wall
# clock is spent waiting on the model — so this is what decides whether the
# library takes an afternoon or half an hour. Measured on this data:
#
#     1 worker    ~53 entries/min        16 workers  ~338/min
#     4 workers   ~82/min                (no 429s at any of these)
#
# It scales nearly linearly because a wave is pure waiting, and the default is
# nonetheless 8 rather than 16: rate limits are per-account and per-tier, this
# was measured on one account on one afternoon, and a default that 429s on
# somebody else's key is a worse failure than a slower run. Raise it with
# --workers once you have watched a run come back clean.
WORKERS = 8

# The groups this pass is allowed to write. `rating` is phase 2's and mechanical;
# `fees` and `discounts` are excluded because doc §7 measured them at 0.1-1.2%
# in note prose — an extraction pass aimed at them returns almost nothing and
# invites the model to infer a price from adjectives.
TARGET_GROUPS = ("hookups", "sites", "facilities", "season", "booking")

# Groups whose provenance marks a human reading. Never overwritten (doc §3:
# verified > derived > inherited).
HUMAN_METHODS = {"manual", "reported"}

# MEASURED, not assumed. Reading a fact off a sentence looks like a task that
# should run fine at `low`, and it does not. A/B on the same 24 entries: `low`
# costs ~$4.30 per 1,000 against ~$6.90, and differed on 7 of 24 — but four of
# those were facts `low` simply missed (an explicit "reserve May-Sept", a "water
# station", a "no hookups" that should set water and sewer false, a stated
# May-Sep season), against two where it was rightly more cautious about an
# approximate rig length. Omissions are the expensive failure here: the point of
# the pass is coverage, and the caution that earned `low` its two wins was
# recovered by tightening the max_rig_ft rule in the prompt instead. Re-run the
# A/B before changing this.
EFFORT = "high"


SYSTEM = """\
You extract structured facts from short descriptions of RV campgrounds. Each
description was written by hand or by an earlier research pass; you are turning
what it already says into fields, not researching the campground.

Return a JSON array, one object per input, each `{"id": <id>, ...groups}`. Emit
ONLY the groups and keys listed below. Return the array and nothing else.

THE RULE THAT MATTERS MOST: absent means unknown. Write a key ONLY when the
description states or plainly implies it. If it is silent, OMIT the key. Never
write false, 0, null or "" to mean "not mentioned" — a stored false is a claim
that somebody checked and there are none, and it is indistinguishable from a
real verification forever after. An object with no keys at all is a perfectly
good answer for a description that is pure marketing prose. Most inputs should
yield only two or three keys.

Do not infer from the campground's name, its agency, or what is typical. "USFS
campground" does not imply vault toilets. "Resort" does not imply a pool. Only
what this description says.

GROUPS AND KEYS

hookups   electric: highest amps AT A SITE — one of 0, 20, 30, 50 and NOTHING
                    else. "50/30-amp" -> 50. "electric sites" with no amperage
                    -> OMIT (do not guess 30). "no hookups" -> 0.
                    NEVER round an odd amperage up to reach an allowed value:
                    "15-amp electric only" is not 20-amp service, and a rig that
                    needs 30 cannot draw either. If the stated amperage is not
                    one of the four, OMIT the key — the description keeps the
                    detail, and a wrong number here is a rig that arrives and
                    cannot plug in.
          water:    bool, piped to the site. A communal spigot is NOT this.
          sewer:    bool, at the site.
          dump:     bool, a dump station on the property (independent of sewer).
                    One described as elsewhere ("city sani-dump nearby", "dump
                    station ~6 blocks away") -> false: the note says where it
                    is, and it is not here.
          "full hookup(s)" -> water true and sewer true; electric only if the
          amperage is actually stated.
          "no hookups" / "primitive" / "non-electric" -> electric 0 (and, for
          "no hookups" specifically, water false and sewer false).

sites     count:        integer, total campsites. "34 single-family sites" -> 34.
                        If the description breaks sites into types, use the total
                        only when it is stated or is an unambiguous sum.
          max_rig_ft:   integer, the longest rig that fits. An approximate
                        figure is still a figure: "rigs to ~45 ft" -> 45,
                        "sites to ~85 ft" -> 85. OMIT only when the description
                        UNDERCUTS its own number or gives no number at all:
                        "max RV ~40 ft (tight spacing, best for smaller rigs)",
                        "reviewers say it tightens over ~24 ft (sites 4/7/8 no
                        large RVs)", "RV length cap not published". The test is
                        whether the note contradicts itself, not whether it
                        hedges. A pad dimension ("40x15 pads") is not a rig
                        limit.
          pull_through: bool. "some pull-throughs" -> true.

facilities showers, flush_toilets, vault_toilets, laundry, camp_store, wifi:
                        bool, each only if named.
          potable_water: bool. "drinking water" or communal spigots -> true.
          Note "restrooms" alone does NOT tell you flush vs vault — omit both.

season    year_round:  bool. "open year round" -> true. A stated closed season
                       -> false.
          opens/closes: "MM-DD", only when a day-level date is given ("open
                       May 15 to Oct 1"). A tilde still counts: "Open ~Apr
                       15-Oct 15" -> "04-15" / "10-15". The dates shift a little
                       each year (often to land on a weekend), but the shape of
                       the season is known. OMIT when the dates are alternatives
                       or vague ("Apr 15/May 1-Oct 15/31", "roughly mid-May").
                       A month with no day is not a date — omit it.

booking   reservable: bool, whether sites can be booked ahead.
          platform:   one of recreation.gov, reserveamerica, usedirect,
                      goingtocamp, campspot, roverpass, hipcamp, sepaq, operator,
                      phone, none — ONLY when the description identifies the
                      channel. `operator` means the campground's or agency's own
                      booking system, and needs to be pointed at ("book on their
                      website", "via the county's OneGov portal"). A bare
                      "reservable online" or "bookable" names no channel: set
                      reservable true and OMIT platform. `phone` for call-only.
          fcfs:       one of never, always, after_cutoff, some_sites.
                      "first-come first-served" with no reservations -> always
                      (and reservable false). "17 reservable / 17 FCFS" ->
                      some_sites (and reservable true). Do NOT write `never`
                      just because the description mentions reservations —
                      `never` is a claim that no site is ever FCFS.
          max_stay_nights: integer, only if a stay limit is stated.

WORKED EXAMPLES

In: {"id": 1, "note": "Carson NF campground on the Red River along NM-578 near
Red River, ~8,600 ft; 23 sites, drinking water, vault toilets; first-come
first-served. Sites back to the river; reviewers note maneuvering tightens over
~24 ft (sites 4/7/8 no large RVs) but smaller-to-mid rigs fit."}
Out: {"id": 1, "sites": {"count": 23}, "facilities": {"potable_water": true,
"vault_toilets": true}, "booking": {"reservable": false, "fcfs": "always"}}
(no max_rig_ft: the note undercuts its own 24 ft in the same breath)

In: {"id": 2, "note": "Small quiet RV park off US-287 N in Grapeland set in ~8
acres of pines; ~20 extra-large 40x15 concrete full-hookup pads (50/30/20-amp),
some pull-through, on-site laundry, fiber internet. Nightly-bookable."}
Out: {"id": 2, "hookups": {"electric": 50, "water": true, "sewer": true},
"sites": {"count": 20, "pull_through": true}, "facilities": {"laundry": true,
"wifi": true}, "booking": {"reservable": true}}
(no platform: "nightly-bookable" names no channel. No sites.count from "~8
acres" — that is area; the 20 comes from "~20 ... pads". "40x15" is a pad
dimension, not a rig limit, so no max_rig_ft.)

In: {"id": 3, "note": "Chequamegon-Nicolet NF on the east shore of Spectacle
Lake. 34 single-family sites; up to 40 ft. Non-electric, vault toilets, drinking
water, 500-ft sandy swim beach. 17 reservable online / 17 FCFS."}
Out: {"id": 3, "hookups": {"electric": 0}, "sites": {"count": 34,
"max_rig_ft": 40}, "facilities": {"vault_toilets": true, "potable_water": true},
"booking": {"reservable": true, "fcfs": "some_sites"}}

In: {"id": 4, "note": "Bayfront RV resort & marina on 17 acres at Palacios on
Tres Palacios Bay; full-hookup RV sites, floating marina slips, fishing pier,
pool/hot tub, clubhouse; short- and long-term stays. Reservable online."}
Out: {"id": 4, "hookups": {"water": true, "sewer": true}, "booking":
{"reservable": true}}
(no electric: "full-hookup" with no amperage stated. No sites.count: "17 acres"
is area. A pool and a clubhouse are not keys in the vocabulary — drop them.)
"""


# ── Selection ───────────────────────────────────────────────────────────────

def note_sig(note):
    """Stable short hash of the note text a scan read."""
    return hashlib.sha256((note or "").encode("utf-8")).hexdigest()[:16]


def human_verified(entry, group):
    """True when a person's reading of this group must not be overwritten."""
    block = (entry.get(cs.PROVENANCE) or {}).get(group) or {}
    return block.get("method") in HUMAN_METHODS


def needs_scan(entry):
    """Whether this entry's note still has to be read.

    Incrementality lives here. An entry is done when the note it was scanned
    against is byte-for-byte the note it has now — so editing a note re-queues
    exactly that entry and nothing else, and a note nobody has touched is never
    paid for twice.
    """
    note = (entry.get("note") or "").strip()
    if not note:
        return False
    if all(human_verified(entry, g) for g in TARGET_GROUPS):
        return False
    scan = entry.get(cs.NOTE_SCAN) or {}
    return scan.get("sig") != note_sig(entry.get("note"))


def load_rows():
    with open(CAMPGROUNDS_JSON, encoding="utf-8") as fh:
        return json.load(fh)


def candidates(rows, state=None, ids=None):
    out = []
    for r in rows:
        if r.get("kind") == "family":
            continue
        if ids is not None:
            if r.get("id") in ids:
                out.append(r)
            continue
        if state and (r.get("state") or "").upper() != state.upper():
            continue
        if needs_scan(r):
            out.append(r)
    return out


# ── The model call ──────────────────────────────────────────────────────────

def build_batch(entries):
    return json.dumps([{"id": e["id"], "note": (e.get("note") or "").strip()}
                       for e in entries], ensure_ascii=False, indent=None)


def parse_reply(text):
    """Pull the JSON array out of a reply, tolerantly.

    Deliberately NOT structured outputs. A JSON schema for these groups would
    need `required` and `additionalProperties: false` to be worth having, and
    `required` is the opposite of what this pass needs: the whole discipline is
    that the model OMITS what the note does not say. A schema that pushes toward
    filling every field would fight the one rule that matters (§2.1).
    """
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.+?)```", text, re.S)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("["), text.rfind("]")
    if start < 0 or end < start:
        raise ValueError("no JSON array in reply")
    body = text[start:end + 1]
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        # One malformed character should not cost the other eleven entries.
        # Measured at ~1.6% of batches, always a local defect (a stray quote, a
        # trailing comma) rather than a wholesale failure, so fall back to
        # parsing each top-level object on its own and keep the ones that are
        # well-formed. Entries whose object is lost simply come back unanswered,
        # which leaves them queued for the next run — the same path a failed
        # batch already took, just for one entry instead of twelve.
        salvaged = [obj for obj in _top_level_objects(body) if obj is not None]
        if not salvaged:
            raise
        return salvaged


def _top_level_objects(body):
    """Yield each top-level {...} in an array body, parsed, or None if it isn't.

    Brace-counting rather than a regex, because a note quoted back into the
    reply can contain braces; string state is tracked so a brace inside a JSON
    string doesn't unbalance the scan.
    """
    depth = 0
    start = None
    in_string = escaped = False
    for i, ch in enumerate(body):
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                chunk = body[start:i + 1]
                try:
                    yield json.loads(chunk)
                except json.JSONDecodeError:
                    yield None
                start = None


def clean_proposal(proposal):
    """Validate one entry's proposed groups, dropping anything out of vocabulary.

    The model is not trusted to have stayed inside the schema, and a batch must
    not be lost because one field in one entry was hallucinated. Each group is
    staged through `apply_update` against a throwaway dict, so anything the
    vocabulary refuses is dropped with a warning and the rest still lands.
    """
    out, rejected = {}, []
    for group, values in proposal.items():
        if group == "id":
            continue
        if group not in TARGET_GROUPS:
            rejected.append(f"{group} (not a target group)")
            continue
        if not isinstance(values, dict) or not values:
            continue
        kept = {}
        for key, value in values.items():
            # `None` from the model means "unknown", which is the absence of a
            # key — never a write. apply_update would read it as "clear this",
            # which on an entry a human had filled would be a deletion.
            if value is None or value == "":
                continue
            try:
                cs.apply_update({}, {group: {key: value}})
            except cs.SchemaError as e:
                rejected.append(f"{group}.{key}={value!r} ({e})")
                continue
            kept[key] = value
        if kept:
            out[group] = kept
    return out, rejected


# Errors that will not come right by trying the next batch: no credit, a bad or
# unauthorized key, a model this account cannot reach. Everything else — a
# timeout, a 429, a malformed reply — is worth carrying on past.
_FATAL_ERROR = re.compile(
    r"credit balance|authentication|invalid x-api-key|permission|"
    r"not_found_error|billing", re.I)


def fatal(exc):
    """Whether this failure makes every remaining batch pointless.

    Learned the hard way: the account ran out of credit mid-run and the pass
    carried on issuing requests, failing 190 more batches in about a minute
    because each one now returned instantly. Nothing was corrupted — the
    entries stay queued either way — but it buries the real error in a wall of
    identical ones, and on a larger run it would be a long stream of doomed
    requests. A run that cannot succeed should say so once and stop.
    """
    return bool(_FATAL_ERROR.search(str(exc)))


def _safe_extract(client, batch, args):
    """Run one batch, returning the exception rather than raising it.

    A wave must not lose three good batches because the fourth timed out, and
    the entries in a failed batch simply stay queued for the next run.
    """
    try:
        return extract_batch(client, batch, args.model, args.effort)
    except Exception as e:                       # noqa: BLE001 — batch-local
        return e


def extract_batch(client, entries, model, effort=EFFORT):
    """One request. Returns {id: {group: {...}}} plus usage, or raises."""
    resp = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        thinking={"type": "adaptive"},
        output_config={"effort": effort},
        # Identical on every call, so caching turns hundreds of repeats of a
        # ~1,900-token prompt into one.
        system=[{"type": "text", "text": SYSTEM,
                 "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": build_batch(entries)}],
    )
    if resp.stop_reason == "refusal":
        why = getattr(getattr(resp, "stop_details", None), "category", "")
        raise RuntimeError(f"refused{f' ({why})' if why else ''}")
    if resp.stop_reason == "max_tokens":
        # A truncated array would parse as a SHORTER one — some entries silently
        # missing rather than an error — so this must never be salvaged.
        raise RuntimeError("hit max_tokens; batch would be silently short")
    text = "\n".join(b.text for b in resp.content if b.type == "text").strip()
    return parse_reply(text), resp.usage


# ── Writing ─────────────────────────────────────────────────────────────────

def write_deltas(deltas, model, today):
    """Merge this batch into campgrounds.json, re-reading first.

    Re-reading rather than dumping a dict held since startup is the same rule
    `detect_people.py` follows: a long run races the live admin UI on PA, and a
    campground edited there mid-run must not be reverted by a batch that loaded
    the file ten minutes ago.

    The file round-trips byte-identically at indent=2 / ensure_ascii=False, so
    only the entries actually touched show up in the diff.
    """
    rows = load_rows()
    by_id = {r.get("id"): r for r in rows}
    written = 0
    for cid, (groups, sig) in deltas.items():
        entry = by_id.get(cid)
        if entry is None:
            continue
        payload = {g: v for g, v in groups.items() if not human_verified(entry, g)}
        if payload:
            prov = dict(entry.get(cs.PROVENANCE) or {})
            for group in payload:
                prov[group] = {"source": "note prose", "checked": today,
                               "method": "derived"}
            payload[cs.PROVENANCE] = prov
        # Stamped even when the note yielded nothing: that is the record that
        # makes the next run skip it instead of re-billing the same silence.
        payload[cs.NOTE_SCAN] = {"sig": sig, "checked": today, "model": model}
        cs.apply_update(entry, payload)
        written += 1

    tmp = CAMPGROUNDS_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, CAMPGROUNDS_JSON)
    return written


# ── Reporting ───────────────────────────────────────────────────────────────

def report(rows):
    scannable = [r for r in rows
                 if r.get("kind") != "family" and (r.get("note") or "").strip()]
    todo = [r for r in scannable if needs_scan(r)]
    print(f"{len(rows):,} entries, {len(scannable):,} with a note")
    print(f"{len(scannable) - len(todo):,} scanned, {len(todo):,} left\n")
    print(f"{'group':12} {'entries with a value':>22}")
    for group in TARGET_GROUPS:
        n = sum(1 for r in rows if r.get(group))
        print(f"{group:12} {n:>13,} {100 * n / max(len(rows), 1):>7.1f}%")
    if todo:
        by_state = {}
        for r in todo:
            by_state[r.get("state") or "??"] = by_state.get(r.get("state") or "??", 0) + 1
        top = sorted(by_state.items(), key=lambda kv: -kv[1])[:8]
        print("\nremaining by state: "
              + ", ".join(f"{s} {n:,}" for s, n in top))


# ── Working without the API ─────────────────────────────────────────────────
# The API account ran out of credit with 5,145 notes unread (AWH 2026-09-15:
# "we won't be getting more API credits for the time being"), so the same
# extraction can be done by a model reading the notes directly in a session and
# handing back the same JSON. These two modes are that path, and the point of
# routing it through here rather than editing campgrounds.json by hand is that
# EVERY rule still applies: the proposals go through `clean_proposal` and
# `write_deltas` exactly as the API's do, so the vocabulary is enforced, a
# human-verified group is still protected, a null still cannot delete a field,
# and `note_scan` is still stamped so the work is resumable.
#
# Follow the rules in SYSTEM above when reading the notes. They are not
# suggestions — most of them are a specific mistake that was made and caught.

SESSION_MODEL = "claude-opus-5/session"


def dump_queued(rows, count, state=None, path=None):
    """Write the next `count` queued notes as JSON for a reader to work from."""
    todo = candidates(rows, state=state)[:count]
    payload = [{"id": e["id"], "note": (e.get("note") or "").strip()}
               for e in todo]
    text = json.dumps(payload, ensure_ascii=False, indent=1)
    if path:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"{len(payload)} notes -> {path}")
    else:
        print(text)
    return len(payload)


def apply_file(path, model, today, dry_run=False):
    """Apply proposals from a JSON file through the normal validation path."""
    with open(path, encoding="utf-8") as fh:
        proposals = json.load(fh)
    rows = load_rows()
    by_id = {r.get("id"): r for r in rows}
    deltas, with_values, unknown = {}, 0, []
    for proposal in proposals:
        cid = proposal.get("id")
        entry = by_id.get(cid)
        if entry is None:
            unknown.append(cid)
            continue
        groups, rejected = clean_proposal(proposal)
        for r in rejected:
            print(f"  {cid}: dropped {r}", file=sys.stderr)
        deltas[cid] = (groups, note_sig(entry.get("note")))
        if groups:
            with_values += 1
    if unknown:
        print(f"  ignoring {len(unknown)} unknown id(s): {unknown[:8]}",
              file=sys.stderr)
    print(f"{len(deltas)} entries, {with_values} with values"
          + (" [DRY RUN]" if dry_run else ""))
    if dry_run:
        return 0
    written = write_deltas(deltas, model, today)
    print(f"written {written}")
    return written


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                    help=f"max entries this run (default {DEFAULT_LIMIT})")
    ap.add_argument("--batch", type=int, default=BATCH,
                    help=f"notes per request (default {BATCH})")
    ap.add_argument("--state", help="only this state/province")
    ap.add_argument("--ids", help="comma-separated ids, ignores the done-check")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--effort", default=EFFORT,
                    choices=("low", "medium", "high", "xhigh", "max"))
    ap.add_argument("--workers", type=int, default=WORKERS,
                    help=f"batches in flight at once (default {WORKERS})")
    ap.add_argument("--dry-run", action="store_true",
                    help="call the model and print proposals, write nothing")
    ap.add_argument("--report", action="store_true",
                    help="coverage and what is left; no API call")
    ap.add_argument("--dump", type=int, metavar="N",
                    help="write the next N queued notes as JSON and exit; "
                         "no API call (for reading them without the API)")
    ap.add_argument("--out", help="file for --dump")
    ap.add_argument("--apply-file", metavar="PATH",
                    help="apply proposals from a JSON file through the same "
                         "validation and write path; no API call")
    args = ap.parse_args()

    rows = load_rows()
    if args.report:
        report(rows)
        return 0

    today = dt.date.today().isoformat()
    if args.dump is not None:
        dump_queued(rows, args.dump, state=args.state, path=args.out)
        return 0
    if args.apply_file:
        apply_file(args.apply_file, SESSION_MODEL, today,
                   dry_run=args.dry_run)
        return 0

    ids = None
    if args.ids:
        ids = {int(x) for x in args.ids.split(",") if x.strip()}
    todo = candidates(rows, state=args.state, ids=ids)
    total_left = len(todo)
    todo = todo[:args.limit]
    if not todo:
        print("nothing to do — every note in scope has been scanned")
        return 0

    if not (os.environ.get("ANTHROPIC_API_KEY")
            or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        print("ANTHROPIC_API_KEY is not set. Put it in the repo's .env "
              "(export ANTHROPIC_API_KEY=sk-ant-...) or the environment.",
              file=sys.stderr)
        return 2

    import anthropic
    client = anthropic.Anthropic()

    # Ctrl-C between batches stops cleanly; inside one it finishes the write
    # first, so the interrupt costs at most the batch in flight and never a
    # half-written file.
    stopping = {"now": False, "fatal": None}

    def on_sigint(_sig, _frm):
        if stopping["now"]:
            raise KeyboardInterrupt
        stopping["now"] = True
        print("\n-- stopping after this batch (Ctrl-C again to abort now) --",
              file=sys.stderr)

    signal.signal(signal.SIGINT, on_sigint)

    batches = [todo[i:i + args.batch] for i in range(0, len(todo), args.batch)]
    in_tok = out_tok = cached = cache_write = 0
    scanned = written = failed = 0
    values_found = 0

    print(f"{total_left:,} entries left overall; doing {len(todo):,} "
          f"in {len(batches)} batch(es) of {args.batch}"
          f"{' [DRY RUN]' if args.dry_run else ''}\n")

    # Batches run concurrently but are WRITTEN IN WAVES: every request in a
    # wave completes, then one write applies all of them. That keeps the API
    # time overlapped (the run is latency-bound, not CPU-bound — 4 workers take
    # it from ~3.7 hours to under an hour) while leaving exactly one writer, so
    # the read-modify-write in write_deltas stays race-free without a lock. The
    # blast radius of a kill grows from one batch to one wave, which at the
    # defaults is 48 entries out of 12,689 — still small, and still recoverable
    # by simply running again.
    waves = [batches[i:i + args.workers]
             for i in range(0, len(batches), args.workers)]
    done_batches = 0

    for wave in waves:
        results = []
        if args.workers == 1:
            results = [(wave[0], _safe_extract(client, wave[0], args))]
        else:
            with cf.ThreadPoolExecutor(max_workers=len(wave)) as pool:
                futures = {pool.submit(_safe_extract, client, b, args): b
                           for b in wave}
                for fut in cf.as_completed(futures):
                    results.append((futures[fut], fut.result()))

        deltas = {}
        for batch, outcome in results:
            done_batches += 1
            if isinstance(outcome, Exception):
                print(f"batch {done_batches}/{len(batches)}: FAILED ({outcome})",
                      file=sys.stderr, flush=True)
                failed += len(batch)
                if fatal(outcome):
                    # Say it once and stop the run, rather than reprinting the
                    # same error for every batch left.
                    stopping["now"] = True
                    stopping["fatal"] = str(outcome)
                continue
            proposals, usage = outcome
            in_tok += usage.input_tokens
            out_tok += usage.output_tokens
            cached += getattr(usage, "cache_read_input_tokens", 0) or 0
            # Counted separately because it is billed at ~1.25x and, on the
            # first call of a run, it is the whole system prompt — leaving it
            # out made a run look several times cheaper than it was.
            cache_write += getattr(usage, "cache_creation_input_tokens", 0) or 0

            by_id = {e["id"]: e for e in batch}
            for proposal in proposals:
                cid = proposal.get("id")
                entry = by_id.get(cid)
                if entry is None:
                    print(f"  ignoring unknown id {cid!r} in reply",
                          file=sys.stderr)
                    continue
                groups, rejected = clean_proposal(proposal)
                for r in rejected:
                    print(f"  {cid}: dropped {r}", file=sys.stderr)
                # An entry the model skipped entirely got no answer, so it is
                # NOT stamped — leaving it queued for the next run rather than
                # silently recorded as read.
                deltas[cid] = (groups, note_sig(entry.get("note")))
                if groups:
                    values_found += 1
                if args.dry_run:
                    summary = ("nothing" if not groups else json.dumps(
                        groups, ensure_ascii=False, sort_keys=True))
                    print(f"  {cid} {entry.get('name', '')[:44]:<44} {summary}")

        scanned += len(deltas)
        if not args.dry_run and deltas:
            written += write_deltas(deltas, args.model, today)

        print(f"{done_batches}/{len(batches)} batches | "
              f"{scanned:,}/{len(todo):,} scanned | "
              f"{values_found:,} with values"
              f"{'' if args.dry_run else ' — written'}", flush=True)
        if stopping["now"]:
            break

    cost = None
    if "opus" in args.model:                      # $5/$25 per MTok, cache 1.25x/0.1x
        cost = ((in_tok + 1.25 * cache_write + 0.1 * cached) / 1e6 * 5
                + out_tok / 1e6 * 25)
    print(f"\nscanned {scanned:,}  |  yielded values {values_found:,}  |  "
          f"failed {failed:,}"
          + ("" if args.dry_run else f"  |  written {written:,}"))
    if stopping["fatal"]:
        print(f"\nSTOPPED — this run could not continue:\n  {stopping['fatal']}\n"
              "Whatever was scanned is written and committed-ready; the rest "
              "stays queued.\nFix the cause and run the same command again.",
              file=sys.stderr)
    print(f"tokens: {in_tok:,} in, {cache_write:,} cache-write, "
          f"{cached:,} cache-read, {out_tok:,} out"
          + (f"  ~${cost:.2f}" if cost else ""))
    if scanned:
        per = (cost / scanned) if cost else 0
        print(f"~${per * 1000:.2f} per 1,000 entries at this batch size"
              if per else "")
    if not args.dry_run and written:
        print("\nreview and commit:  git diff --stat && git add -u && git commit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
