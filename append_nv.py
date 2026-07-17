#!/usr/bin/env python3
"""Append WA research-agent results to campgrounds.json (textual append, preserves
formatting; never full-rewrites). Usage: python3 append_nv.py <results.json> [...]

Each results file is a JSON array of {decision, name, location, elevation_meters,
ownership, website, phone, note, inclusion_evidence, waterfront, lead}. Only
decision=="add" rows are appended. waterfront is stored as the placeholder; the
waterfront audit fills waterfront_evidence later. Leads are saved to
/tmp/nv_leads.json keyed by new id for the audit stage."""
import json, sys, os

CG = '/home/andrew/Dev/campgrounds/campgrounds.json'
LEADS = '/tmp/nv_leads.json'

FIELD_ORDER = ['id','kind','name','location','elevation_meters','state','ownership',
               'waterfront','inclusion_evidence','website','phone','note']

def load_results(paths):
    rows=[]
    for p in paths:
        data=json.load(open(p))
        for r in data:
            if r.get('decision')=='add':
                rows.append(r)
    return rows

def main():
    paths=sys.argv[1:]
    if not paths:
        print('usage: append_nv.py <results.json> [...]'); sys.exit(1)
    rows=load_results(paths)
    if not rows:
        print('no add rows'); return

    data=json.load(open(CG))
    next_id=max(e['id'] for e in data)+1

    # dedup guard: warn/skip if a new entry sits within ~150 m of an existing NV
    # campground (RV Life lists some campgrounds twice under different city tags,
    # and agents can't see across batches). ~0.0015 deg lat/lng ~= 150 m.
    def parse(loc):
        try:
            a,b=loc.split(','); return float(a),float(b)
        except Exception:
            return None
    import re as _re
    def norm(nm):
        nm=(nm or '').lower()
        nm=_re.sub(r'\b(campground|camp|park|recreation area|rec area|cg)\b','',nm)
        nm=_re.sub(r'[^a-z0-9]+','',nm)
        return nm
    nv_coords=[]
    nv_names={}  # normalized-name -> list of (coord_or_None, id, name)
    for e in data:
        if e.get('state')=='NV':
            p=parse(e.get('location','') or '')
            if p: nv_coords.append((p,e['id'],e.get('name','')))
            n=norm(e.get('name',''))
            if n: nv_names.setdefault(n,[]).append((p,e['id'],e.get('name','')))

    leads={}
    if os.path.exists(LEADS):
        leads=json.load(open(LEADS))

    entries=[]
    skipped_dups=[]
    for r in rows:
        p=parse(r['location'])
        if p:
            dup=None
            for (q,eid,enm) in nv_coords:
                if abs(p[0]-q[0])<0.0015 and abs(p[1]-q[1])<0.0015:
                    dup=(eid,enm); break
            if dup:
                skipped_dups.append((r['name'],dup)); continue
        nn=norm(r['name'])
        if nn and nn in nv_names:
            # only treat a same-name match as a dup when it's also geographically
            # near (~1.5 km) -- distinct campgrounds share names across NV
            # (Fish Lake, Rock Creek, Eightmile, Big Pine, ...)
            namedup=None
            for (q,eid,enm) in nv_names[nn]:
                if p is None or q is None:
                    namedup=(eid,enm); break  # can't range-check -> conservative skip
                if abs(p[0]-q[0])<0.015 and abs(p[1]-q[1])<0.015:
                    namedup=(eid,enm); break
            if namedup:
                skipped_dups.append((r['name'],namedup)); continue
        e={'id':next_id,'kind':'campground','name':r['name'],
           'location':r['location'],'elevation_meters':r['elevation_meters'],
           'state':'NV','ownership':r['ownership'],
           'waterfront':r.get('waterfront','not waterfront'),
           'inclusion_evidence':r.get('inclusion_evidence',''),
           'website':r.get('website',''),'phone':r.get('phone',''),
           'note':r.get('note','')}
        e={k:e[k] for k in FIELD_ORDER}
        entries.append(e)
        if p: nv_coords.append((p,next_id,r['name']))  # catch within-batch dups too
        if nn: nv_names.setdefault(nn,[]).append((p,next_id,r['name']))
        if r.get('lead'):
            leads[str(next_id)]=r['lead']
        next_id+=1

    if skipped_dups:
        print('SKIPPED as duplicates (within ~150 m of an existing NV entry):')
        for nm,(eid,enm) in skipped_dups:
            print(f'  - {nm!r} ~ existing id {eid} {enm!r}')
    if not entries:
        print('no new entries after dedup'); return

    # textual append
    text=open(CG).read().rstrip()
    assert text.endswith(']'), 'unexpected file end'
    body=text[:-1].rstrip()  # up to last entry's closing brace
    blocks=[]
    for e in entries:
        block=json.dumps(e, indent=2, ensure_ascii=False)
        block='\n'.join('  '+line for line in block.split('\n'))
        blocks.append(block)
    out=body+',\n'+',\n'.join(blocks)+'\n]\n'
    open(CG,'w').write(out)

    # validate
    check=json.load(open(CG))
    json.dump(leads, open(LEADS,'w'), indent=1)
    ids=[e['id'] for e in entries]
    print(f'appended {len(entries)} entries, ids {ids[0]}-{ids[-1]}')
    print(f'file now valid, {len(check)} total entries')

if __name__=='__main__':
    main()
