"""PA state park findings from DCNR's statewide camping table + each park's site types on the
booking site. python3 pa_findings.py DL_DIR OUT_JSON"""
import collections, glob, json, os, re, sys
dl, out_path = sys.argv[1], sys.argv[2]
rows = [e for e in json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'campgrounds.json'), encoding='utf-8')) if e.get('kind') == 'campground']
TABLE = "https://www.pa.gov/agencies/dcnr/recreation/where-to-go/state-parks/state-park-prices/camping.html"
RV = {"Modern Non-Electric": ("modern", None), "Modern Electric": ("modern", "electric"), "Full-Hookup": ("modern", "full"),
      "Rustic Non-Electric": ("rustic", None), "Rustic Electric": ("rustic", "electric"),
      "Modern-Rustic Non-Electric": ("modern-rustic", None), "Modern-Rustic Electric": ("modern-rustic", "electric")}
parks = {}
for f in glob.glob(os.path.join(dl, 'pa_88*.json')):
    d = json.load(open(f)); parks[d['parkId']] = d
def has(e):
    f = e.get('fees') or {}
    return f.get('nightly_low') is not None or f.get('nightly_high') is not None
out, skipped = [], []
for e in rows:
    if e['state'] != 'PA' or e['ownership'] != 'state' or has(e): continue
    u = next((w for w in (e.get('website') or '').split() if 'parkId=' in w), None) or {1059: 'parkId=880317'}.get(e['id'])
    pid = re.search(r'parkId=(\d+)', u).group(1) if u else None
    d = parks.get(pid)
    if not d: skipped.append((e['id'], e['name'], 'no listing')); continue
    c = collections.Counter(r['cells'][1] for r in d['sites'] if len(r['cells']) > 1 and r['cells'][1] in RV)
    if not c: skipped.append((e['id'], e['name'], 'no RV site types: ' + str(collections.Counter(r['cells'][1] for r in d['sites'] if len(r['cells']) > 1)))); continue
    loops = {RV[t][0] for t in c}; amen = {RV[t][1] for t in c}
    out.append({"id": e['id'], "name": e['name'], "parkId": pid, "types": dict(c), "loops": sorted(loops), "amen": sorted(a or 'none' for a in amen)})
json.dump({"parks": out, "skipped": skipped}, open(out_path, 'w'), indent=1)
for x in out: print(x['id'], x['name'][:40], x['loops'], x['amen'], x['types'])
print('skipped:'); [print('  ', s) for s in skipped]
