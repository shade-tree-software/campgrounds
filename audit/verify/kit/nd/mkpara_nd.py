import json,sys
S,N=sys.argv[1],sys.argv[2]; by={x['id']:x for x in json.load(open('campgrounds.json'))}
head=open('audit/verify/kit/nd/nd_head.txt',encoding='utf-8').read().rstrip('\n')
ids=[x['entry']['id'] for x in json.load(open(f'audit/verify/batches/{N}.json'))]
parts=[]
for i in ids:
    e=by[i]; wf=e.get('waterfront'); own=e.get('ownership')
    f=e.get('fees') or {}; lo,hi=f.get('nightly_low'),f.get('nightly_high'); bits=[own,f'stored {wf}', (f'stored ${lo:g}'+(f'-{hi:g}' if isinstance(hi,(int,float)) and hi!=lo else '')) if isinstance(lo,(int,float)) else 'no rate stored']
    if not e.get('phone'): bits.append('no phone stored')
    tail=[]
    if own=='private': tail.append('price gate, Google rating, long-stay tests')
    if wf!='not waterfront': tail.append(f'check the stored {wf} value hard')
    parts.append(f"{i} {e['name']} ({', '.join(bits)})"+(': '+'; '.join(tail) if tail else '')+'.')
open(f'{S}/{N}_para.txt','w',encoding='utf-8').write(head+'\nTHIS BATCH: '+' '.join(parts)+'\n'); print(N,len(ids))
