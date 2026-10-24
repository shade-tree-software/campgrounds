# mkbrief.py SCRATCH BATCH ["extra sentence"]: write SCRATCH/<BATCH>_prompt.txt from brief_base.txt
# (phase-7 schema verification brief; the batch paragraph is Montana-specific - edit it for another state)
import json,sys,os
K=os.path.dirname(os.path.abspath(__file__)); R=os.path.abspath(os.path.join(K,'..','..','..'))
S=sys.argv[1]; b=sys.argv[2]; extra=sys.argv[3] if len(sys.argv)>3 else ''
ds=json.load(open(f'{R}/audit/verify/batches/{b}.json'))
ids='; '.join(f"{d['entry']['id']} {d['entry']['name']} ({d['entry']['ownership']})" for d in ds)
os.makedirs(f'{S}/{b}',exist_ok=True)
para=(f"Then work through {R}/audit/verify/batches/{b}.json ({len(ds)} MONTANA entries: {ids}). For EACH entry, in order: research its own pages, "
      f"then write {R}/audit/verify/results/<id>.json immediately, before starting the next. Scratch files go in {S}/{b}/. "
      "Montana State Parks and FWP fishing access sites: fwp.mt.gov pages plus montanastateparks.reserveamerica.com (the booking site; may refuse plain fetches - use bw.py) and FWP's fee pages. "
      f"Earlier MT batches' scratch dirs ({S}/mt-*/) may hold reusable notes. {extra}")
open(f'{S}/{b}_prompt.txt','w').write(open(f'{K}/brief_base.txt').read().replace('__SCRATCH__',S).replace('__BATCH__',para))
print('ok',b,len(ds))
