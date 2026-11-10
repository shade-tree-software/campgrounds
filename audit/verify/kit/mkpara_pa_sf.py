# mkpara_pa_sf.py SCRATCH BATCH EXTRA_FILE PREV_FILE: fill kit/para_pa_sf_generic.txt for one PA
# state forest batch (list comes from batches/BATCH.json), then run mkbrief_mo.py on the result.
import json, os, subprocess, sys
K = os.path.dirname(os.path.abspath(__file__))
S, b, xf, pf = sys.argv[1:5]
batch = json.load(open(os.path.join(K, '..', 'batches', b + '.json')))
lst = '; '.join(f"{d['entry']['id']} {d['entry']['name'].replace(' State Forest Campsites', ':').replace(' State Forest Campsite', ':')}" for d in batch)
t = open(os.path.join(K, 'para_pa_sf_generic.txt')).read().strip()
t = t.replace('__LIST__', lst).replace('__EXTRA__', open(xf).read().strip()).replace('__PREV__', open(pf).read().strip())
out = os.path.join(S, b + '_para.txt'); open(out, 'w').write(t)
subprocess.check_call([sys.executable, '-I', os.path.join(K, 'mkbrief_mo.py'), S, b, out])
