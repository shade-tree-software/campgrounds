#!/usr/bin/env python3
"""Draft decisions.json from scan_2026-10-12.json and pages_2026-10-12.json (2026-10-12).

    python3 -I audit/hookups_recheck/draft.py [CAMPGROUNDS_JSON]

Point it at the campgrounds.json the decisions were drafted from (the parent of the commit that
applied them, e.g. `git show <commit>^:campgrounds.json > /tmp/cg.json`): run against a later file it
drafts from values already changed. It overwrites decisions.json.

A pattern pass proposes each held key's verdict with the sentence it rests on: RIDB's site catalog
(recgov_hookups.derive) first, then "no hookups" / "no electricity" / "no (potable) water" in the
rec.gov description, the amenity list or the agency page; a key no source states is removed, but
only if the note doesn't state it either (ids.json `unsupported`). Every entry was then read and
corrected by hand in overrides.py (wrong facility matched, a temporary water alert, a shared
listing page, park-wide NPS statements, operator wording the patterns miss). decisions.json is the
record; this script is how it was made.
"""
import importlib.util, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
A = HERE + "/"
ids=json.load(open(A+'ids.json'))['entries']
scan=json.load(open(A+'scan_2026-10-12.json',encoding='utf-8'))
pages=json.load(open(A+'pages_2026-10-12.json',encoding='utf-8'))
rows={r['id']:r for r in json.load(open(sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,'campgrounds.json'),encoding='utf-8'))}
spec=importlib.util.spec_from_file_location('ov',A+'overrides.py'); ov=importlib.util.module_from_spec(spec); spec.loader.exec_module(ov)
NOHOOK=re.compile(r"\bno (rv |electric(al)? |water |utility )?hook[\s-]*ups?|non[\s-]*hook[\s-]*up|hook[\s-]*ups? (are |is )?not (available|provided)|without (any )?hook[\s-]*ups|there are no (rv |utility )?hook|no utility hook|no utilities",re.I)
NOELEC=re.compile(r"\bno (water,? |running water,? )?(electricity|electric|power)\b|(electricity|electric hook[\s-]*ups?|power) (is |are )?not (available|provided)|water and electric(al)? hook[\s-]*ups are not available|no water,? electricity|no water or electricity|without electricity",re.I)
NOWATER=re.compile(r"potable water is not available|\bno (potable |drinking |running )?water\b(?! hook)|(drinking|potable) water is not (available|provided)|water is not available|bring (your|their) own (drinking )?water|no water is (available|provided)|does not have (potable |drinking )?water",re.I)
def sents(t): return [s.strip(' |') for s in re.split(r'(?<=[.!?])\s+|\s\|\s',t or '') if s.strip(' |')]
out={}
for it in ids:
    i=it['id']; r=rows[i]; s=scan.get(str(i),{}); p=pages.get(str(i),{})
    held=r.get('hookups') or {}
    srcs=[]
    if s.get('fid') and s.get('match')=='linked' or (s.get('match') or '').startswith('nearest'):
        srcs.append(('ridb',f"recreation.gov facility {s.get('fid')} ({s.get('facility_name')})",sents(s.get('description'))+[f"amenities: {', '.join(s.get('amenities') or [])}"]))
    if p.get('url') and not p.get('error'):
        srcs.append(('page',p['url'],sents(p.get('amenity_block'))+list(p.get('snippets') or [])))
    cat=s.get('catalog') or {}
    def find(rx):
        for kind,name,ss in srcs:
            for x in ss:
                if rx.search(x): return kind,name,x
        return None
    nh=find(NOHOOK); ne=find(NOELEC); nw=find(NOWATER)
    dec={'set':{},'remove':[],'why':{}}
    for key in ('electric','water','sewer'):
        if key not in held: continue
        if key in cat:
            dec['set'][key]=cat[key]; dec['why'][key]=('catalog',f"campsite catalog of facility {s.get('fid')}",f"types {s.get('rv_site_types')}"); continue
        hit=None
        if key=='electric': hit=nh or ne
        elif key=='water': hit=nh or ne if (ne and re.search('water',ne[2],re.I)) else (nh or nw)
        else: hit=nh
        if hit:
            dec['set'][key]={'electric':0,'water':False,'sewer':False}[key]; dec['why'][key]=hit
        elif key in it['unsupported']:
            dec['remove'].append(key)
    out[i]=dec
props={str(k):v for k,v in out.items()}
CAT={('electric',0):'every RV site typed NONELECTRIC',('water',False):"every RV site's Water Hookup is No",('sewer',False):"every RV site's Sewer Hookup is No"}
out={}
for it in ids:
    i=str(it['id']); p=props[i]; s=scan.get(i,{}); pg=pages.get(i,{})
    o=ov.OVERRIDES.get(int(i))
    checked=[]
    if s.get('fid'): checked.append(f"recreation.gov facility {s['fid']} ({s.get('facility_name')}; {s.get('match')}): catalog, description, amenities")
    else: checked.append('no RIDB facility found within 3 mi')
    if pg.get('url'): checked.append(pg['url']+(f" ({pg['error']})" if pg.get('error') else ''))
    if o and o.get('replace'):
        d={'set':o.get('set',{}),'remove':o.get('remove',[]),'source':o.get('source',''),'derived':o.get('derived',False)}
        checked+=o.get('checked_extra',[])
    else:
        parts=[];derived=False
        for k,w in p['why'].items():
            if o and k in o.get('why',{}): w=o['why'][k]
            kind=w[0]
            if kind=='catalog':
                parts.append(f"recreation.gov campsite catalog, facility {s.get('fid')}: {CAT[(k,p['set'][k])]}"); derived=True
            elif kind=='ridb':
                parts.append(f"recreation.gov facility {s.get('fid')} description: '{w[2]}'")
            else:
                parts.append(f"{w[1]}: '{w[2]}'")
        seen=[];[seen.append(x) for x in parts if x not in seen]
        d={'set':p['set'],'remove':p['remove'],'source':'; '.join(seen)+' (read 2026-10-12)' if seen else '','derived':derived}
        if o:
            for k in ('set','remove'):
                if k in o: d[k]=o[k]
            if 'source' in o: d['source']=o['source']
            if 'derived' in o: d['derived']=o['derived']
            checked+=o.get('checked_extra',[])
    d['checked']='; '.join(checked)
    if not d['set']: d.pop('source',None); d.pop('derived',None)
    out[i]=d
doc={'as_of':'2026-10-12','why':json.load(open(A+'ids.json'))['why'],'entries':out}
json.dump(doc,open(A+'decisions.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(out),'decisions;',sum(1 for d in out.values() if d['set']),'with values set;',sum(len(d['remove']) for d in out.values()),'keys removed')
