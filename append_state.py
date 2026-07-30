#!/usr/bin/env python3
"""Append research-agent results to campgrounds.json (textual append, preserves
formatting; never full-rewrites). Replaces the old per-state append_<st>.py copies
(one parameterized script instead of 8 near-identical ones).

Usage: python3 append_state.py --state AZ [--leads /tmp/az_leads.json] <results.json> [...]

Each results file is a JSON array of {decision, name, location, elevation_meters,
ownership, website, phone, note, inclusion_evidence, waterfront, lead}. Only
decision=="add" rows are appended. waterfront is stored as the placeholder; the
waterfront audit fills waterfront_evidence later. Leads are saved to the leads file
keyed by new id for the audit stage."""
import json, sys, os, re, argparse

# repo root = this script's directory; resolves correctly on any machine/clone
_REPO = os.path.dirname(os.path.abspath(__file__))
CG = os.path.join(_REPO, 'campgrounds.json')
# Read-only here (sweeps only ever append campgrounds), but its ids are part of
# the same id space — see next_id below.
FAMILY = os.path.join(_REPO, 'trip_data', 'family.json')

FIELD_ORDER = ['id', 'kind', 'name', 'location', 'elevation_meters', 'state',
               'ownership', 'waterfront', 'inclusion_evidence', 'website',
               'phone', 'note']


def load_results(paths):
    rows = []
    for p in paths:
        for r in json.load(open(p)):
            if r.get('decision') == 'add':
                rows.append(r)
    return rows


def parse(loc):
    try:
        a, b = loc.split(',')
        return float(a), float(b)
    except Exception:
        return None


def norm(nm):
    nm = (nm or '').lower()
    nm = re.sub(r'\b(campground|camp|park|recreation area|rec area|cg)\b', '', nm)
    nm = re.sub(r'[^a-z0-9]+', '', nm)
    return nm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--state', required=True, help='two-letter state/province code, e.g. AZ')
    ap.add_argument('--leads', default=None, help='leads output path (default /tmp/<st>_leads.json)')
    ap.add_argument('results', nargs='+')
    a = ap.parse_args()
    ST = a.state.upper()
    LEADS = a.leads or f'/tmp/{ST.lower()}_leads.json'

    rows = load_results(a.results)
    if not rows:
        print('no add rows'); return

    data = json.load(open(CG))
    # Ids are unique across BOTH location files and never reused, so the high
    # water mark has to account for family.json (gitignored — see CLAUDE.md
    # "Family Locations"). It currently holds the highest id in the database, so
    # taking the max of campgrounds.json alone would re-issue a live id.
    ids = [e['id'] for e in data]
    try:
        ids += [e['id'] for e in json.load(open(FAMILY)) if 'id' in e]
    except FileNotFoundError:
        pass
    next_id = max(ids) + 1

    # dedup guard: skip a new entry within ~150 m of an existing same-state entry
    # (RV Life lists some campgrounds twice under different city tags, and agents
    # can't see across batches). ~0.0015 deg lat/lng ~= 150 m.
    st_coords = []              # (coord, id, name)
    st_names = {}               # normalized-name -> [(coord_or_None, id, name)]
    for e in data:
        if e.get('state') == ST:
            p = parse(e.get('location', '') or '')
            if p:
                st_coords.append((p, e['id'], e.get('name', '')))
            n = norm(e.get('name', ''))
            if n:
                st_names.setdefault(n, []).append((p, e['id'], e.get('name', '')))

    leads = json.load(open(LEADS)) if os.path.exists(LEADS) else {}

    entries = []
    skipped_dups = []
    for r in rows:
        p = parse(r['location'])
        if p:
            dup = None
            for (q, eid, enm) in st_coords:
                if abs(p[0] - q[0]) < 0.0015 and abs(p[1] - q[1]) < 0.0015:
                    dup = (eid, enm); break
            if dup:
                skipped_dups.append((r['name'], dup)); continue
        nn = norm(r['name'])
        if nn and nn in st_names:
            # a same-name match is a dup only when also geographically near (~1.5 km)
            # -- distinct campgrounds share names within a state
            namedup = None
            for (q, eid, enm) in st_names[nn]:
                if p is None or q is None:
                    namedup = (eid, enm); break   # can't range-check -> conservative skip
                if abs(p[0] - q[0]) < 0.015 and abs(p[1] - q[1]) < 0.015:
                    namedup = (eid, enm); break
            if namedup:
                skipped_dups.append((r['name'], namedup)); continue
        e = {'id': next_id, 'kind': 'campground', 'name': r['name'],
             'location': r['location'], 'elevation_meters': r['elevation_meters'],
             'state': ST, 'ownership': r['ownership'],
             'waterfront': r.get('waterfront', 'not waterfront'),
             'inclusion_evidence': r.get('inclusion_evidence', ''),
             'website': r.get('website', ''), 'phone': r.get('phone', ''),
             'note': r.get('note', '')}
        e = {k: e[k] for k in FIELD_ORDER}
        entries.append(e)
        if p:
            st_coords.append((p, next_id, r['name']))   # catch within-batch dups too
        if nn:
            st_names.setdefault(nn, []).append((p, next_id, r['name']))
        if r.get('lead'):
            leads[str(next_id)] = r['lead']
        next_id += 1

    if skipped_dups:
        print(f'SKIPPED as duplicates (within ~150 m of an existing {ST} entry):')
        for nm, (eid, enm) in skipped_dups:
            print(f'  - {nm!r} ~ existing id {eid} {enm!r}')
    if not entries:
        print('no new entries after dedup'); return

    # textual append (never re-dump)
    text = open(CG).read().rstrip()
    assert text.endswith(']'), 'unexpected file end'
    body = text[:-1].rstrip()
    blocks = []
    for e in entries:
        block = json.dumps(e, indent=2, ensure_ascii=False)
        block = '\n'.join('  ' + line for line in block.split('\n'))
        blocks.append(block)
    out = body + ',\n' + ',\n'.join(blocks) + '\n]\n'
    open(CG, 'w').write(out)

    check = json.load(open(CG))          # validate
    json.dump(leads, open(LEADS, 'w'), indent=1)
    ids = [e['id'] for e in entries]
    print(f'appended {len(entries)} entries, ids {ids[0]}-{ids[-1]}')
    print(f'file now valid, {len(check)} total entries')


if __name__ == '__main__':
    main()
