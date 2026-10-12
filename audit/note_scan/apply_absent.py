# apply_absent.py BATCH.json PROPOSALS.json [--dry-run] [--rescan]: session note-scan helper (2026-10-09). BATCH = an
# extract_fields.py --dump file; PROPOSALS = [{id, group:{...}}] read in session. Drops any group the entry
# already has (derived / rec.gov / agency values are never overwritten), applies the rest via --apply-file,
# which stamps note_scan on EVERY entry in the batch (empty answers included).
#
# --rescan (2026-10-12) is for entries re-queued because their note was edited: a group whose provenance
# source is "note prose" is re-read from the edited note instead of being kept as it was, so a proposal for
# it is applied, and a proposal's "_unsupported": {group: [keys]} removes keys of such a group that the note
# does not state (the 2026-09-17 hand pass wrote "no hookups" for some notes that never said so). A group
# from any other source (rec.gov, an agency page, a person) is still never touched.
import json,sys,subprocess,os
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CG=os.path.join(ROOT,'campgrounds.json')
rescan='--rescan' in sys.argv
mode=[a for a in sys.argv[3:] if a!='--rescan']
cg={e['id']:e for e in json.load(open(CG,encoding='utf-8'))}
batch=[r['id'] for r in json.load(open(sys.argv[1],encoding='utf-8'))]
props={p['id']:p for p in json.load(open(sys.argv[2],encoding='utf-8'))}

def from_note(e,g):
    return ((e.get('provenance') or {}).get(g) or {}).get('source')=='note prose'

out=[];dropped=0;unsupported={}
for i in batch:
    p=props.get(i,{'id':i})
    q={'id':i}
    for g,v in p.items():
        if g=='id': continue
        if g=='_unsupported':
            if rescan: unsupported[i]=v
            continue
        if cg[i].get(g) and not (rescan and from_note(cg[i],g)): dropped+=1; continue
        q[g]=v
    out.append(q)
f=sys.argv[2].replace('.json','_f.json'); json.dump(out,open(f,'w',encoding='utf-8'),ensure_ascii=False)
print('entries',len(out),'groups kept',sum(len(q)-1 for q in out),'dropped (already set)',dropped)
r=subprocess.run([sys.executable,'extract_fields.py','--apply-file',f]+mode,cwd=ROOT,capture_output=True,text=True)
print(r.stdout[-1500:],r.stderr[-800:])
if unsupported:
    rows=json.load(open(CG,encoding='utf-8'))
    n=0
    for e in rows:
        for g,keys in unsupported.get(e['id'],{}).items():
            if not e.get(g) or not from_note(e,g):
                print('unsupported: skip',e['id'],g,'(absent or not from note prose)'); continue
            for k in keys:
                if k in e[g]:
                    print('unsupported:',e['id'],f'{g}.{k}',json.dumps(e[g][k]),'removed'); n+=1
                    if '--dry-run' not in mode: del e[g][k]
            if not e[g] and '--dry-run' not in mode:
                del e[g]; e['provenance'].pop(g,None)
                if not e['provenance']: del e['provenance']
    if n and '--dry-run' not in mode:
        tmp=CG+'.tmp'
        with open(tmp,'w',encoding='utf-8') as fh:
            json.dump(rows,fh,indent=2,ensure_ascii=False); fh.write('\n')
        os.replace(tmp,CG)
