#!/usr/bin/env python3
"""Apply inclusion-audit results to campgrounds.json with surgical text edits
(never re-dumps the file).  Usage: apply_inclusion_audit.py <results.json>

Each result: {id, name, verdict: keep|remove|review, reason, evidence, confidence}

- verdict 'keep'  -> upsert the entry's `inclusion_evidence` field (the durable
  record that this entry has been inclusion-audited and confirmed a real,
  currently-operating, drive-in RV campground). Non-empty == audited.
- verdict 'remove'/'review' -> NOT modified here. They are printed as a report
  so a human reviews the remove list before any excision (removal is a separate,
  deliberate step, mirroring the 'review the remove list before I excise' rule).
"""
import json, os, re, sys

CG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'campgrounds.json')
results = json.load(open(sys.argv[1]))
raw = open(CG).read()

def upsert_inclusion(raw, eid, evidence):
    """Set the entry's inclusion_evidence (replace if present, else insert it
    after waterfront_evidence / waterfront, else as the last field of the block)."""
    anchor = f'"id": {eid},'
    i = raw.index(anchor)
    j = raw.find('"id":', i + len(anchor))
    if j == -1:
        j = len(raw)
    block = raw[i:j]
    lit = json.dumps(evidence, ensure_ascii=False)
    if '"inclusion_evidence"' in block:
        nb = re.sub(r'("inclusion_evidence":\s*)("(?:[^"\\]|\\.)*")',
                    lambda m: m.group(1) + lit, block, count=1)
        return raw[:i] + nb + raw[j:]
    out, inserted = [], False
    for l in block.split('\n'):
        out.append(l)
        if inserted:
            continue
        mm = (re.match(r'^([ \t]*)"waterfront_evidence":\s*"(?:[^"\\]|\\.)*"(,?)\s*$', l)
              or re.match(r'^([ \t]*)"waterfront":\s*"(?:[^"\\]|\\.)*"(,?)\s*$', l))
        if mm:
            indent, comma = mm.group(1), mm.group(2)
            if comma != ',':
                out[-1] = l.rstrip() + ','
            out.append(f'{indent}"inclusion_evidence": {lit}{"," if comma == "," else ""}')
            inserted = True
    if not inserted:                                   # fallback: last field before '}'
        lines = block.rstrip().split('\n')
        # lines[-1] is the closing brace line; lines[-2] is the last field
        for k in range(len(lines) - 1, -1, -1):
            if lines[k].strip().startswith('"'):
                indent = re.match(r'^([ \t]*)', lines[k]).group(1)
                if not lines[k].rstrip().endswith(','):
                    lines[k] = lines[k].rstrip() + ','
                lines.insert(k + 1, f'{indent}"inclusion_evidence": {lit}')
                break
        return raw[:i] + '\n'.join(lines) + ('\n' if block.endswith('\n') else '') + raw[j:]
    return raw[:i] + '\n'.join(out) + raw[j:]

kept = []
removes = []
reviews = []
for r in results:
    if r['verdict'] == 'keep':
        if not r.get('evidence'):
            raise SystemExit(f"id {r['id']}: keep verdict needs a non-empty evidence string")
        raw = upsert_inclusion(raw, r['id'], r['evidence'])
        kept.append(r['id'])
    elif r['verdict'] == 'remove':
        removes.append(r)
    else:
        reviews.append(r)

data = json.loads(raw)  # validate
by_id = {e['id']: e for e in data if isinstance(e, dict)}
for r in results:
    if r['verdict'] == 'keep':
        assert by_id[r['id']].get('inclusion_evidence') == r['evidence'], (r['id'], 'evidence mismatch')

open(CG, 'w').write(raw)
print(f"OK: {len(kept)} keeps stamped with inclusion_evidence, JSON valid.")
if removes:
    print(f"\n=== REMOVE candidates ({len(removes)}) — review before excising: ===")
    for r in removes:
        print(f"  {r['id']}  [{r.get('reason','')}]  {r['name']}\n        {r['evidence']}")
if reviews:
    print(f"\n=== REVIEW (uncertain, {len(reviews)}) — needs a human/firsthand check: ===")
    for r in reviews:
        print(f"  {r['id']}  {r['name']}\n        {r['evidence']}")
