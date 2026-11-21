# mkpara_sk.py SCRATCH p3-NNN -> SCRATCH/p3-NNN_para.txt (sk_head.txt + one line per entry)
import json,sys
S,N=sys.argv[1],sys.argv[2]; sys.path.insert(0,'.'); import campground_store; by={x['id']:x for x in campground_store.load('campgrounds.json')}
head=open('audit/verify/kit/sk/sk_head.txt',encoding='utf-8').read().rstrip('\n')
ids=[x['entry']['id'] for x in json.load(open(f'audit/verify/batches/{N}.json'))]
parts=[]
for i in ids:
    e=by[i]; wf=e.get('waterfront'); own=e.get('ownership'); r=e.get('rating') or {}
    f=e.get('fees') or {}; lo,hi=f.get('nightly_low'),f.get('nightly_high')
    bits=[own]
    if wf!='not waterfront': bits.append(f'stored {wf}')
    bits.append((f'stored C${lo:g}'+(f'-{hi:g}' if isinstance(hi,(int,float)) and hi!=lo else '')) if isinstance(lo,(int,float)) else 'no rate stored')
    if own=='private': bits.append(f"RV Life {'$'*(r.get('price_tier') or 0) or 'none'}")
    if not e.get('phone'): bits.append('no phone stored')
    tail=[]
    if own=='private':
        if not isinstance(lo,(int,float)): tail.append('find a posted nightly rate or engine quote')
        elif lo>69: tail.append('stored rate is over the C$69 gate - confirm the cheapest electric night for a 23-ft rig and any gateway')
        elif lo>=55: tail.append('rate is near the gate - confirm a dated base rate')
        tail.append('Google rating, long-stay tests')
    if own=='local' and 'regional park' in e['name'].lower(): tail.append('regional park: measure the nightly share')
    w=(e.get('website') or '')
    if own=='provincial' and 'campgroundDetails.do' not in w: tail.append('no campgroundDetails.do link stored - give it')
    if wf!='not waterfront': tail.append(f'check the stored {wf} value hard')
    if 'koa' in e['name'].lower(): tail.append('KOA: price with koa.py as for any private park')
    parts.append(f"{i} {e['name']} ({', '.join(bits)})"+(': '+'; '.join(tail) if tail else '')+'.')
open(f'{S}/{N}_para.txt','w',encoding='utf-8').write(head+'\nTHIS BATCH: '+' '.join(parts)+'\n'); print(N,len(ids))
