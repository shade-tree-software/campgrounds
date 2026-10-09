# apply_absent.py BATCH.json PROPOSALS.json [--dry-run]: session note-scan helper (2026-10-09). BATCH = an
# extract_fields.py --dump file; PROPOSALS = [{id, group:{...}}] read in session. Drops any group the entry
# already has (derived / rec.gov / agency values are never overwritten), applies the rest via --apply-file,
# which stamps note_scan on EVERY entry in the batch (empty answers included).
# apply.py BATCH.json PROPOSALS.json : drop groups the entry already has, write the rest via extract_fields --apply-file
import json,sys,subprocess,os
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
cg={e['id']:e for e in json.load(open(os.path.join(ROOT,'campgrounds.json')))}
batch=[r['id'] for r in json.load(open(sys.argv[1]))]
props={p['id']:p for p in json.load(open(sys.argv[2]))}
out=[];dropped=0
for i in batch:
    p=props.get(i,{'id':i})
    q={'id':i}
    for g,v in p.items():
        if g=='id': continue
        if cg[i].get(g): dropped+=1; continue
        q[g]=v
    out.append(q)
f=sys.argv[2].replace('.json','_f.json'); json.dump(out,open(f,'w'),ensure_ascii=False)
print('entries',len(out),'groups kept',sum(len(q)-1 for q in out),'dropped (already set)',dropped)
mode=sys.argv[3:] 
r=subprocess.run([sys.executable,'extract_fields.py','--apply-file',f]+mode,cwd=ROOT,capture_output=True,text=True)
print(r.stdout[-1500:],r.stderr[-800:])
