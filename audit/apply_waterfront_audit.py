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

changed_wf = changed_coord = 0
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

data = json.loads(raw)  # validate before writing
by_id = {e['id']: e for e in (data if isinstance(data, list) else data['campgrounds']) if isinstance(e, dict)}
for r in results:
    e = by_id[r['id']]
    assert e['waterfront'] == r['final'], (r['id'], e['waterfront'], r['final'])
    if r.get('coord_fix'):
        assert e['location'] == r['coord_fix'], (r['id'], e['location'])

open(CG, 'w').write(raw)
print(f'OK: {changed_wf} waterfront values changed, {changed_coord} coordinates fixed, JSON valid, {len(results)} entries verified')
