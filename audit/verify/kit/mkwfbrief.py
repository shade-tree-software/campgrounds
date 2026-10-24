# mkwfbrief.py SCRATCH BATCH: write SCRATCH/<BATCH>_prompt.txt from wf_brief.txt (waterfront re-audit;
# batch inputs live in audit/verify/waterfront/<BATCH>.json, e.g. wf-mt-2)
import sys,os
K=os.path.dirname(os.path.abspath(__file__)); R=os.path.abspath(os.path.join(K,'..','..','..')); S=sys.argv[1]; b=sys.argv[2]
os.makedirs(f'{S}/{b}',exist_ok=True)
open(f'{S}/{b}_prompt.txt','w').write(open(f'{K}/wf_brief.txt').read().replace('/home/user/campgrounds',R).replace('__SCRATCH__',S).replace('BATCH',b))
print('ok',b)
