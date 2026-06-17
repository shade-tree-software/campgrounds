#!/usr/bin/env python3
"""One-time migration: move per-entry waterfront audit evidence from git commit
messages into a `waterfront_evidence` field on each campground entry.

Pass 1: parse per-entry lines (with a structured id prefix) from curated audit /
        add-with-audit commits.  Most-recent commit wins.
Pass 2: GA entries come from the structured /tmp results (richest source).

Report-only unless --write is passed.  Surgical text insertion only (no re-dump).
"""
import json, re, subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CG = os.path.join(REPO, "campgrounds.json")

# Curated commits carrying per-entry waterfront evidence.  Bucket-only lines in
# these bodies are ignored by the parser (non-numeric prefix); that's Pass-3's job.
COMMITS = [
    # state-by-state pre-gate re-audit + gate audits
    "683cb8b", "9954f1d", "4c88654", "b38465f", "eeb694e", "317fbd7",
    "2fa26f5", "7dc3872", "08ab8a0", "49c7c78",
    # WI / MI / IA / NE sweeps (per-entry change lines only; confirmed-unchanged not enumerated)
    "5c6025a", "93c2b62", "94dc7f4", "bcf7803",
    "35f5f25", "a56256a", "6b37f74", "4e31287", "5da9588", "3126a2b",
    # TN
    "dbcf9cf",
    # New England per-state gate audits
    "053666b", "c8691f9", "8f32c79", "32ea296", "7d005f5", "178d83d",
    # NC adds-with-audit
    "b5ad8c0", "8724156", "d6b8657", "fdec3b6",
    # SC adds-with-audit
    "2ca0026", "03e410c", "7ae8f85", "9a48e81",
    # KS / CO adds-with-audit (per-entry waterfront evidence folded in)
    "1c1d763", "c0f101d", "4049c78", "c3dd2dd", "8a5f968",
]

def load_ids():
    d = json.load(open(CG, encoding="utf-8"))
    return d, {e["id"] for e in d if e.get("kind") == "campground"}

# Pass 3: bucket-sweep ranges (each block == one add batch the sweep audited).
# The audit was already applied, so each entry's CURRENT waterfront value is the
# audit outcome; we record that it was swept + cite the commit for bucket detail.
SWEEP_RANGES = [
    (2669, 2753, "3126a2b", "NE state"),
    (2888, 2942, "5da9588", "IA state"),
    (3447, 3597, "bcf7803", "WI local-government"),
    (3598, 3737, "35f5f25", "MI state"),
    (3738, 3804, "a56256a", "MI federal/state-forest"),
    (3805, 3910, "6b37f74", "MI private/federal"),
    (3911, 4050, "4e31287", "MI local"),
]

def commit_date(h):
    return subprocess.check_output(["git", "-C", REPO, "log", "-1", "--format=%ct", h]).decode().strip()

def commit_ym(h):
    return subprocess.check_output(["git", "-C", REPO, "log", "-1", "--format=%cs", h]).decode().strip()[:7]

def body(h):
    return subprocess.check_output(["git", "-C", REPO, "log", "-1", "--format=%b", h]).decode()

# id from a line's structured PREFIX only (never from evidence prose)
RE_PIPE   = re.compile(r"^\s*(\d{2,5})\s*\|")          # 2239 | name | final: ev
RE_BRACK  = re.compile(r"^\s*\[(\d{2,5})\]")            # [2890] name: ...
RE_DASHID = re.compile(r"^\s*-\s*(\d{2,5})\b")          # - 1517 name ...: ev
RE_PAREN  = re.compile(r"^\s*-\s*.+?\((\d{2,5})\)\s*:") # - Name (4540): ev

def parse_line(line, valid_ids):
    """Return (id, evidence) or None.  Evidence = text after the delimiting colon."""
    m = RE_PIPE.match(line)
    if m:
        cid = int(m.group(1))
        # pipe format: id | name | final: evidence   -> evidence after the final ': '
        rest = line.split("|", 2)
        ev = rest[2].split(":", 1)[1].strip() if len(rest) == 3 and ":" in rest[2] else ""
        return (cid, ev) if cid in valid_ids else None
    for rx in (RE_BRACK, RE_PAREN, RE_DASHID):
        m = rx.match(line)
        if m:
            cid = int(m.group(1))
            if cid not in valid_ids:
                return None
            if ":" not in line:
                return None
            ev = line.split(":", 1)[1].strip()
            return (cid, ev)
    return None

def build_ev_map(data, valid_ids):
    ev_map, src_map = {}, {}
    # newest commit wins -> process oldest first, overwrite with guard
    commits = sorted(COMMITS, key=lambda h: int(commit_date(h)))
    trans_rx = re.compile(r"^[\w' ]+ -> [\w' ]+\.?$")   # pure value transition, no prose
    for h in commits:
        lines = [raw.rstrip() for raw in body(h).splitlines()]
        i = 0
        while i < len(lines):
            line = lines[i]
            r = parse_line(line, valid_ids) if line.strip() else None
            if not r:
                i += 1
                continue
            cid, ev = r
            # join wrapped continuation lines: indented, non-blank, not a new entry
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if not nxt.strip():
                    break
                if not (nxt[0].isspace()):           # unindented -> new content
                    break
                if parse_line(nxt, valid_ids):        # next entry
                    break
                ev += " " + nxt.strip()
                j += 1
            i = j
            ev = ev.strip()
            if not ev or len(ev) < 6:
                continue
            if trans_rx.match(ev):                    # transition-only stub -> let Pass3/4 fill
                continue
            # overwrite only if newer evidence is real prose
            if cid in ev_map and len(ev) < 25 and len(ev_map[cid]) >= 25:
                continue
            ev_map[cid] = ev
            src_map[cid] = h[:7]

    # Pass 2: GA from structured /tmp results (overrides parsed GA prose)
    ga_added = 0
    for path in ("/tmp/ga_results_all.json", "/tmp/gasf_results_all.json"):
        if os.path.exists(path):
            for e in json.load(open(path)):
                ev_map[e["id"]] = e["evidence"]
                src_map[e["id"]] = "GA-audit"
                ga_added += 1
    pass12 = len(ev_map)

    # Pass 3: synthesize traceable notes for bucket-sweep entries not already
    # covered per-entry.  Current waterfront value == the audit outcome.
    by_id_all = {e["id"]: e for e in data}
    for lo, hi, h, label in SWEEP_RANGES:
        ym = commit_ym(h)
        for cid in range(lo, hi + 1):
            if cid in ev_map or cid not in valid_ids:
                continue
            wf = by_id_all[cid].get("waterfront", "not waterfront")
            ev_map[cid] = (f"audited {ym} ({label} evidence-gate sweep, commit {h}); "
                           f"waterfront '{wf}' set by that satellite/per-site-map sweep "
                           f"(per-entry bucket detail in the commit message)")
            src_map[cid] = h

    # Pass 4: any ON-WATER value still lacking evidence + not --AWH was set by a
    # deliberate sweep-era assessment (inline-assessed add or a confirming state
    # audit).  Trace it to the commit that set the value via one git-blame pass
    # and cite that commit.  (not-waterfront entries without recoverable evidence
    # stay field-less == not-audited, per the field's contract.)
    out = subprocess.check_output(
        ["git", "-C", REPO, "blame", "--line-porcelain", "--", CG]).decode(errors="replace")
    line_commit, ln, cur = {}, 0, None
    for L in out.split("\n"):
        if re.match(r"^[0-9a-f]{40} ", L):
            cur = L.split()[0]
        elif L.startswith("\t"):
            ln += 1; line_commit[ln] = cur
    raw = open(CG, encoding="utf-8").read().split("\n")
    wf_commit, cur = {}, None
    for i, l in enumerate(raw, 1):
        mm = re.match(r'\s*"id":\s*(\d+),', l)
        if mm: cur = int(mm.group(1))
        if '"waterfront":' in l and cur not in wf_commit:
            wf_commit[cur] = line_commit.get(i)
    subj_cache = {}
    for e in data:
        if e.get("kind") != "campground":
            continue
        cid = e["id"]
        wf = e.get("waterfront", "not waterfront")
        if wf == "not waterfront" or cid in ev_map or "--AWH" in (e.get("note") or ""):
            continue
        h = wf_commit.get(cid)
        if not h:
            continue
        h7 = h[:7]
        if h7 not in subj_cache:
            subj_cache[h7] = subprocess.check_output(
                ["git", "-C", REPO, "log", "-1", "--format=%s", h]).decode().strip()
        ev_map[cid] = (f"waterfront '{wf}' assessed in commit {h7} ({subj_cache[h7][:70]}); "
                       f"on-water value recorded at that commit (no separate per-entry evidence string)")
        src_map[cid] = h7
    return ev_map, src_map, pass12, ga_added


def main():
    write = "--write" in sys.argv
    diagnose = "--diagnose" in sys.argv
    data, valid_ids = load_ids()
    ev_map, src_map, pass12, ga_added = build_ev_map(data, valid_ids)
    by_id = {e["id"]: e for e in data}

    if diagnose:
        import collections
        raw = open(CG, encoding="utf-8").read().split("\n")
        lineno, cur = {}, None
        for i, l in enumerate(raw, 1):
            mm = re.match(r'\s*"id":\s*(\d+),', l)
            if mm: cur = int(mm.group(1))
            if '"waterfront":' in l and cur not in lineno:
                lineno[cur] = i
        resid = [e for e in data if e.get("kind") == "campground"
                 and e.get("waterfront", "not waterfront") != "not waterfront"
                 and e["id"] not in ev_map and "--AWH" not in (e.get("note") or "")]
        buckets = collections.Counter()
        for e in resid:
            ln = lineno.get(e["id"])
            if not ln:
                buckets["(no line)"] += 1; continue
            h = subprocess.check_output(["git", "blame", "-L", f"{ln},{ln}", "--", CG]).decode().split()[0].lstrip("^")
            subj = subprocess.check_output(["git", "log", "-1", "--format=%s", h]).decode().strip()
            buckets[f"{h[:7]} {subj[:55]}"] += 1
        print(f"residual unsupported on-water (no evidence, no --AWH): {len(resid)}")
        for k, n in buckets.most_common():
            print(f"  {n:4d}  {k}")
        return

    print(f"Pass1+2: {pass12} ids mapped to evidence ({ga_added} from GA /tmp results)")
    print(f"Total with Pass3: {len(ev_map)} ids")
    from collections import Counter
    st = Counter(by_id[i]["state"] for i in ev_map if i in by_id)
    print("By state:", dict(sorted(st.items(), key=lambda x: -x[1])))
    import random
    random.seed(1)
    print("\n--- SAMPLES ---")
    for cid in random.sample(list(ev_map), 10):
        e = by_id[cid]
        print(f"[{cid}] {e['state']} {e['name']} | wf={e.get('waterfront')} | src={src_map[cid]}")
        print(f"     {ev_map[cid][:140]}")

    if not write:
        print("\n(report only — pass --write to apply)")
        return

    # ---- surgical insertion: add waterfront_evidence after the waterfront line ----
    raw = open(CG, encoding="utf-8").read()
    lines = raw.split("\n")
    out = []
    cur_id = None
    inserted = 0
    id_rx = re.compile(r'^\s*"id":\s*(\d+),')
    wf_rx = re.compile(r'^(\s*)"waterfront":\s*"(.*?)",?\s*$')
    for ln in lines:
        m = id_rx.match(ln)
        if m:
            cur_id = int(m.group(1))
        out.append(ln)
        wm = wf_rx.match(ln)
        if wm and cur_id in ev_map:
            indent = wm.group(1)
            ev = ev_map[cur_id].replace("\\", "\\\\").replace('"', '\\"')
            base = ln.rstrip()
            if base.endswith(","):                       # waterfront has following fields
                out.append(f'{indent}"waterfront_evidence": "{ev}",')
            else:                                          # waterfront was the last field
                out[-1] = base + ","                       # give it a trailing comma
                out.append(f'{indent}"waterfront_evidence": "{ev}"')
            inserted += 1
    new = "\n".join(out)
    json.loads(new)  # validate
    open(CG, "w", encoding="utf-8").write(new)
    print(f"\nWROTE {inserted} waterfront_evidence fields; JSON valid.")

if __name__ == "__main__":
    main()
