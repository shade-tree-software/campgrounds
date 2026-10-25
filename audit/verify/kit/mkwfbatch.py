# mkwfbatch.py BATCH [--state XX] [--limit N]: build audit/verify/waterfront/<BATCH>.json from the OPEN leads in
# audit/verify/waterfront_leads.md (anything outside a "## Resolved" block), each lead plus the entry's prior
# evidence. Skips ids already in another wf-*.json batch and duplicate lead lines. --list prints open leads by state.
import json, os, re, sys, glob, collections
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
W = f'{R}/audit/verify/waterfront'
args = sys.argv[1:]
def opt(k, d=None):
    return args[args.index(k) + 1] if k in args else d
leads, cur, resolved = collections.OrderedDict(), None, False
for line in open(f'{R}/audit/verify/waterfront_leads.md', encoding='utf-8'):
    if line.startswith('## '):
        resolved = line.startswith('## Resolved'); cur = None; continue
    if resolved: continue
    m = re.match(r'- (?:\*\*)?(\d+)\b', line)
    if m:
        cur = int(m.group(1))
        if cur in leads: cur = None; continue   # duplicate lead line
        leads[cur] = line[2:].strip()
    elif line.startswith('  ') and cur is not None:
        leads[cur] += ' ' + line.strip()
    else:
        cur = None
db = {e['id']: e for e in json.load(open(f'{R}/campgrounds.json', encoding='utf-8'))}
done = set()
for f in glob.glob(f'{W}/wf-*.json'):
    if f.endswith('_results.json'): continue
    done |= {e['id'] for e in json.load(open(f))}
todo = [i for i in leads if i in db and i not in done]
gone = [i for i in leads if i not in db]
if '--list' in args:
    c = collections.Counter(db[i]['state'] for i in todo)
    print(len(todo), 'open leads;', dict(c.most_common()), '| not in DB (dropped?):', gone); sys.exit()
batch = args[0]; st = opt('--state'); n = int(opt('--limit', 8))
pick = [i for i in todo if not st or db[i]['state'] == st][:n]
out = [{k: db[i].get(k) for k in ('id', 'name', 'state', 'location', 'waterfront', 'ownership', 'website')}
       | {'lead': {'note': leads[i], 'prior_evidence': db[i].get('waterfront_evidence') or db[i].get('note', '')}} for i in pick]
assert out and not os.path.exists(f'{W}/{batch}.json'), 'nothing to write or batch exists'
json.dump(out, open(f'{W}/{batch}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', batch, [e['id'] for e in out])
