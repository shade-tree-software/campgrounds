# fix_qc_reverify_20261009.py [--apply]   (dry run by default)
# Corrections after re-viewing the imagery behind the QC no_rate adds (ids 15126-15164).
# The session that wrote them had image reads that may not have rendered ("[media removed:
# request limit]" in its context by the time it was summarized), so every flagged waterfront
# call, pin, plan count and off-season-frame claim was re-viewed on 2026-10-09 against the same
# saved frames/plans plus one fresh z17 frame (St-Come), each read confirmed to render. The log
# of what each image showed is audit/canada_no_rate/qc_reverify_20261009.md.
# Outcome: every waterfront call stands; one pin moves (St-Paulin: entrance-road junction ->
# central loops); St-Edouard's "~100 traveller sites" was an overcount (~45 traveller 3-service +
# ~15 water/electric + 21 unserviced); a few distances/quantities are tightened. Evidence strings
# gain a stamp naming only what was re-viewed (2 Rivieres' and Chaudiere's waterfront calls rest on
# z18 frames that were never in doubt, so only their inclusion lines change).
# Edits campgrounds.json line-by-line (only the touched field lines change) and keeps the inputs
# the builder reads (qc_wf_calls.jsonl, build_qc_results.py, adds_work.json) in step, so a
# rebuild cannot bring the old text back. Verdict-row corrections are appended separately with v.py.
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
APPLY = '--apply' in sys.argv
SAT_MAP = '; satellite + site map re-viewed 2026-10-09'
SAT = '; satellite re-viewed 2026-10-09'
MAP = '; site map re-viewed 2026-10-09'

# id -> {field: new value | ('sub', old, new) | ('append', text)}
EDITS = {
 15126: {'waterfront_evidence': ('append', SAT_MAP)},
 15127: {
  'location': '46.41577,-73.06582',
  'elevation_meters': 157.0,
  'waterfront_evidence': "satellite (Esri z17) at 46.4140,-73.0634, re-viewed 2026-10-09: the loops and pool sit west of the Chemin de la Belle-Montagne access road; the Rivière du Loup runs ~200 m east beyond that road and a wooded strip; not waterfront (pin moved 2026-10-09 from the entrance-road junction onto the central loops by the pool)",
 },
 15128: {
  'waterfront_evidence': "operator 2024 site plan + satellite (Esri z15/z17) at 46.3273,-73.1402, re-viewed 2026-10-09: the plan puts the traveller 3-service sites Île 1-3 at the edge of an island in the park's dammed pond (the satellite shows the island with structures near its shore); a seasonal row lines the pond's SE road; the main rows, where the pin sits, are ~150 m south (Google's point is the zoo road to the north); pond",
  'inclusion_evidence': ('sub', '2024 plan colours ~100 traveller sites of ~450', '2024 plan colours ~45 traveller 3-service sites, ~15 water/electric and 21 unserviced beside ~370 seasonal (re-counted 2026-10-09)'),
  'note': ('sub', 'roughly 100 traveller sites and a large seasonal section', 'roughly 45 traveller 3-service sites plus water/electric and unserviced sites beside a large seasonal section'),
 },
 15129: {
  'waterfront_evidence': "satellite (Esri z17) centred on Google's point 48.3876,-70.5887, re-viewed 2026-10-09: hillside lanes around a small pond above the Sainte-Rose-du-Nord village; the Saguenay fjord shore (tidal flat) is ~175-300 m south of the loops beyond village houses and streets; the small artificial swimming pond ~115 m north of the pin has no pads at its edge; default down; not waterfront",
 },
 15130: {'waterfront_evidence': ('append', SAT_MAP)},
 15131: {'waterfront_evidence': ('append', SAT_MAP)},
 15132: {'waterfront_evidence': ('append', SAT_MAP)},
 15133: {
  'waterfront_evidence': [('sub', '~40-60 m from the shore', '~40-50 m from the shore'), ('append', SAT)],
  'inclusion_evidence': ('sub', 'roadside section by the wave pool half empty', 'roadside section by the wave pool partly empty'),
 },
 15156: {'waterfront_evidence': ('append', MAP)},
 15157: {
  'inclusion_evidence': ('sub', 'stored trailers on ~2/3 of 200+ pads, western rows empty', '~120-150 stored trailers on 200+ pads, the western loops mostly empty (re-viewed 2026-10-09)'),
 },
 15159: {
  'waterfront_evidence': "operator 2026 plan + satellite (Esri z17/z18) at 46.2846,-73.7952, re-viewed 2026-10-09: the loops run NE from Rang Versailles under pines; the Rivière L'Assomption runs along the park's east side ~50-75 m beyond the nearest visible rows through dense pine, reached by the plan's 'accès à la rivière' path (access, not frontage); the plan's three small sites 1-3 drawn in the riverbank strip can't be resolved under the canopy; default down; not waterfront",
 },
 15161: {
  'inclusion_evidence': ('sub', 'separate block of ~35-45 empty pads of 178', 'separate block of ~30-45 empty pads of 178 (re-viewed 2026-10-09)'),
 },
 15162: {'waterfront_evidence': ('append', MAP)},
 15164: {'waterfront_evidence': ('append', MAP)},
}

# builder inputs, keyed by worklist name
KEY = {15127: 'Camping Belle Montagne', 15128: 'Camping St-Edouard', 15129: 'Camping la Descente des Femmes',
       15133: 'Camping Lac et Foret', 15157: 'Camping 2 Rivieres', 15159: 'Camping Au Soleil St-Côme',
       15161: 'Camping Parc de la Chaudiere'}
SHARE_SUBS = [
 ('2024 plan colours ~100 traveller sites of ~450', '2024 plan colours ~45 traveller 3-service sites, ~15 water/electric and 21 unserviced beside ~370 seasonal (re-counted 2026-10-09)'),
 ('roadside section by the wave pool half empty', 'roadside section by the wave pool partly empty'),
 ('stored trailers on ~2/3 of 200+ pads, western rows empty', '~120-150 stored trailers on 200+ pads, the western loops mostly empty (re-viewed 2026-10-09)'),
 ('separate block of ~35-45 empty pads of 178', 'separate block of ~30-45 empty pads of 178 (re-viewed 2026-10-09)'),
 ('roughly 100 traveller sites and a large seasonal section', 'roughly 45 traveller 3-service sites plus water/electric and unserviced sites beside a large seasonal section'),
]


def new_value(cur, op):
    ops = op if isinstance(op, list) else [op]
    v = cur
    for o in ops:
        if isinstance(o, tuple) and o[0] == 'sub':
            if o[1] not in v:
                sys.exit('substring not found: %r' % o[1])
            v = v.replace(o[1], o[2])
        elif isinstance(o, tuple) and o[0] == 'append':
            if not v.endswith(o[1]):
                v = v + o[1]
        else:
            v = o
    return v


def edit_campgrounds():
    p = os.path.join(REPO, 'campgrounds.json')
    lines = open(p, encoding='utf-8').read().split('\n')
    cg = {e['id']: e for e in json.load(open(p, encoding='utf-8'))}
    idx = {}
    for i, l in enumerate(lines):
        m = re.match(r'^    "id": (\d+),$', l)
        if m and int(m.group(1)) in EDITS:
            idx[int(m.group(1))] = i
    changed = 0
    for cid, fields in EDITS.items():
        i = idx[cid]
        j = i
        while not re.match(r'^  \},?$', lines[j]):
            j += 1
        for f, op in fields.items():
            k = next(n for n in range(i, j) if lines[n].startswith('    "%s": ' % f))
            val = new_value(cg[cid][f], op)
            comma = ',' if lines[k].endswith(',') else ''
            nl = '    "%s": %s%s' % (f, json.dumps(val, ensure_ascii=False), comma)
            if nl != lines[k]:
                print('%d %s:\n   - %s\n   + %s' % (cid, f, lines[k].strip()[:300], nl.strip()[:300]))
                lines[k] = nl
                changed += 1
    out = '\n'.join(lines)
    json.loads(out)  # still valid JSON
    if APPLY and changed:
        open(p, 'w', encoding='utf-8').write(out)
    print('campgrounds.json: %d field lines %s' % (changed, 'written' if APPLY else 'would change'))
    return {e['id']: e for e in json.loads(out)}


def edit_inputs(cg):
    # qc_wf_calls.jsonl: pin / elevation / wf follow the corrected entries
    p = os.path.join(HERE, 'qc_wf_calls.jsonl')
    rows = [json.loads(l) for l in open(p, encoding='utf-8')]
    adds = json.load(open(os.path.join(HERE, 'adds_work.json'), encoding='utf-8'))
    byname = {e['name']: e for e in cg.values() if e.get('state') == 'QC' and 15126 <= e['id'] <= 15164}
    n = 0
    for r in rows:
        e = byname.get(adds.get(r['key'], {}).get('display_name'))
        if not e or e['id'] not in EDITS:
            continue
        for f, src in (('pin', 'location'), ('elevation_meters', 'elevation_meters'), ('wf', 'waterfront_evidence')):
            if f in r and r[f] != e[src]:
                r[f] = e[src]
                n += 1
    if APPLY:
        open(p, 'w', encoding='utf-8').write(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
    print('qc_wf_calls.jsonl: %d values %s' % (n, 'written' if APPLY else 'would change'))
    # build_qc_results.py NOTES / SHARE text
    p = os.path.join(HERE, 'build_qc_results.py')
    src = open(p, encoding='utf-8').read()
    n = 0
    for old, new in SHARE_SUBS:
        if old in src:
            src = src.replace(old, new)
            n += 1
    if APPLY:
        open(p, 'w', encoding='utf-8').write(src)
    print('build_qc_results.py: %d substitutions %s' % (n, 'written' if APPLY else 'would change'))
    # adds_work.json facts line for St-Edouard
    p = os.path.join(HERE, 'adds_work.json')
    a = adds['Camping St-Edouard']
    old = '2024 plan: ~100 traveller sites (3-service + water/electric) plus a large seasonal section'
    if old in a['facts']:
        a['facts'] = a['facts'].replace(old, '2024 plan: ~45 traveller 3-service sites, ~15 water/electric and 21 unserviced plus ~370 seasonal (re-counted 2026-10-09)')
        if APPLY:
            json.dump(adds, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('adds_work.json: St-Edouard facts %s' % ('written' if APPLY else 'would change'))


if __name__ == '__main__':
    edit_inputs(edit_campgrounds())
