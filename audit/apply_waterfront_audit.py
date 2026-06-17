#!/usr/bin/env python3
"""Apply waterfront-audit results to campgrounds.json with surgical text edits
(never re-dumps the file). Usage: apply_waterfront_audit.py <results.json>"""
import json, os, re, sys

CG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'campgrounds.json')
results = json.load(open(sys.argv[1]))
raw = open(CG).read()

def edit_block(raw, eid, field, new_value_literal):
    """Replace `"field": <...>` inside the entry block for id eid."""
    anchor = f'"id": {eid},'
    i = raw.index(anchor)
    j = raw.find('"id":', i + len(anchor))
    if j == -1:
        j = len(raw)
    block = raw[i:j]
    pat = re.compile(r'("%s":\s*)("(?:[^"\\]|\\.)*"|[-\d.]+)' % field)
    m = pat.search(block)
    if not m:
        raise SystemExit(f'id {eid}: field {field} not found')
    new_block = block[:m.start()] + m.group(1) + new_value_literal + block[m.end():]
    return raw[:i] + new_block + raw[j:]

def upsert_evidence(raw, eid, evidence):
    """Set the entry's waterfront_evidence (replace if present, else insert it
    immediately after the waterfront line). The evidence string is the audit's
    proof; a non-empty value is what marks an entry as waterfront-audited."""
    anchor = f'"id": {eid},'
    i = raw.index(anchor)
    j = raw.find('"id":', i + len(anchor))
    if j == -1:
        j = len(raw)
    block = raw[i:j]
    lit = json.dumps(evidence)
    if '"waterfront_evidence"' in block:
        nb = re.sub(r'("waterfront_evidence":\s*)("(?:[^"\\]|\\.)*")',
                    lambda m: m.group(1) + lit, block, count=1)
        return raw[:i] + nb + raw[j:]
    out = []
    for l in block.split('\n'):
        out.append(l)
        mm = re.match(r'^([ \t]*)"waterfront":\s*"(?:[^"\\]|\\.)*"(,?)\s*$', l)
        if mm:
            indent, comma = mm.group(1), mm.group(2)
            if comma == ',':
                out.append(f'{indent}"waterfront_evidence": {lit},')
            else:                                   # waterfront was the last field
                out[-1] = l.rstrip() + ','
                out.append(f'{indent}"waterfront_evidence": {lit}')
    return raw[:i] + '\n'.join(out) + raw[j:]

changed_wf = changed_coord = wrote_ev = 0
for r in results:
    eid = r['id']
    if r['final'] != r['current']:
        edit_block(raw, eid, 'waterfront', '_PROBE_')  # dry probe to fail early
        raw = edit_block(raw, eid, 'waterfront', json.dumps(r['final']))
        changed_wf += 1
    if r.get('coord_fix'):
        raw = edit_block(raw, eid, 'location', json.dumps(r['coord_fix']))
        if r.get('elevation_meters') is not None:
            raw = edit_block(raw, eid, 'elevation_meters', str(float(r['elevation_meters'])))
        changed_coord += 1
    if r.get('evidence'):                            # record the proof in-line
        raw = upsert_evidence(raw, eid, r['evidence'])
        wrote_ev += 1

data = json.loads(raw)  # validate before writing
by_id = {e['id']: e for e in (data if isinstance(data, list) else data['campgrounds']) if isinstance(e, dict)}
for r in results:
    e = by_id[r['id']]
    assert e['waterfront'] == r['final'], (r['id'], e['waterfront'], r['final'])
    if r.get('coord_fix'):
        assert e['location'] == r['coord_fix'], (r['id'], e['location'])
    if r.get('evidence'):
        assert e.get('waterfront_evidence') == r['evidence'], (r['id'], 'evidence mismatch')

open(CG, 'w').write(raw)
print(f'OK: {changed_wf} waterfront values changed, {changed_coord} coordinates fixed, '
      f'{wrote_ev} evidence strings written, JSON valid, {len(results)} entries verified')
