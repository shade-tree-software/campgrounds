#!/usr/bin/env python3
"""Append WA research-agent results to campgrounds.json (textual append, preserves
formatting; never full-rewrites). Usage: python3 append_wa.py <results.json> [...]

Each results file is a JSON array of {decision, name, location, elevation_meters,
ownership, website, phone, note, inclusion_evidence, waterfront, lead}. Only
decision=="add" rows are appended. waterfront is stored as the placeholder; the
waterfront audit fills waterfront_evidence later. Leads are saved to
/tmp/wa_leads.json keyed by new id for the audit stage."""
import json, sys, os

CG = '/home/andrew/Dev/campgrounds/campgrounds.json'
LEADS = '/tmp/wa_leads.json'

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
        print('usage: append_wa.py <results.json> [...]'); sys.exit(1)
    rows=load_results(paths)
    if not rows:
        print('no add rows'); return

    data=json.load(open(CG))
    next_id=max(e['id'] for e in data)+1

    # dedup guard: warn/skip if a new entry sits within ~150 m of an existing WA
    # campground (RV Life lists some campgrounds twice under different city tags,
    # and agents can't see across batches). ~0.0015 deg lat/lng ~= 150 m.
    def parse(loc):
        try:
            a,b=loc.split(','); return float(a),float(b)
        except Exception:
            return None
    wa_coords=[]
    for e in data:
        if e.get('state')=='WA':
            p=parse(e.get('location','') or '')
            if p: wa_coords.append((p,e['id'],e.get('name','')))

    leads={}
    if os.path.exists(LEADS):
        leads=json.load(open(LEADS))

    entries=[]
    skipped_dups=[]
    for r in rows:
        p=parse(r['location'])
        if p:
            dup=None
            for (q,eid,enm) in wa_coords:
                if abs(p[0]-q[0])<0.0015 and abs(p[1]-q[1])<0.0015:
                    dup=(eid,enm); break
            if dup:
                skipped_dups.append((r['name'],dup)); continue
        e={'id':next_id,'kind':'campground','name':r['name'],
           'location':r['location'],'elevation_meters':r['elevation_meters'],
           'state':'WA','ownership':r['ownership'],
           'waterfront':r.get('waterfront','not waterfront'),
           'inclusion_evidence':r.get('inclusion_evidence',''),
           'website':r.get('website',''),'phone':r.get('phone',''),
           'note':r.get('note','')}
        e={k:e[k] for k in FIELD_ORDER}
        entries.append(e)
        if p: wa_coords.append((p,next_id,r['name']))  # catch within-batch dups too
        if r.get('lead'):
            leads[str(next_id)]=r['lead']
        next_id+=1

    if skipped_dups:
        print('SKIPPED as duplicates (within ~150 m of an existing WA entry):')
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
