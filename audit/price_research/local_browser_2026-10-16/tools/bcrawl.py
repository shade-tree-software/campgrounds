"""Browser pass over unpriced ids: home page + up to 3 rate-ish links; keep $ lines. args: ids.json out.jsonl"""
import json, re, subprocess, sys
DRV = '/home/andrew/Dev/campgrounds/audit/private_gap_browser/drv.py'
def drv(*a):
    try:
        return subprocess.run(['python3', DRV, *a], capture_output=True, text=True, timeout=200).stdout
    except Exception as e:
        return f'ERROR: {e}'
ids = json.load(open(sys.argv[1])); out = sys.argv[2]
d = {r['id']: r for r in json.load(open('/home/andrew/Dev/campgrounds/campgrounds.json'))}
done = set()
try:
    for l in open(out): done.add(json.loads(l)['id'])
except FileNotFoundError: pass
SKIP = re.compile(r'facebook\.com|koa\.com|sunoutdoors\.com|tripadvisor|passport-america|travelwisconsin|ndtourism|visitpa|travelok|visitfredericksburg|utahscanyoncountry|albertacampgroundguide', re.I)
for i in ids:
    if i in done or i not in d: continue
    r = d[i]
    urls = [u.strip() for u in re.split(r'[\s,]+', r.get('website') or '') if u.strip().startswith('http')]
    urls = [u for u in urls if not SKIP.search(u)][:2]
    rec = {'id': i, 'name': r['name'], 'pages': []}
    seen = set()
    queue = list(urls)
    n = 0
    while queue and n < 5:
        u = queue.pop(0)
        if u in seen: continue
        seen.add(u); n += 1
        g = drv('goto', f'url={u}', 'wait=' + __import__('os').environ.get('WAIT','5000'), 'timeout=40000')
        if not g.strip():
            sys.exit('driver not answering; stopping without writing ' + str(i))
        if g.startswith('ERROR'):
            rec['pages'].append({'url': u, 'err': g[:200]}); continue
        t = drv('text', r'grep=\$\s?\d|\d+\.\d\d\s*\$|per night|nightly|/night', 'ctx=1', 'max=5000')
        rec['pages'].append({'url': u, 'title': g.strip()[:150], 'lines': t[:5000]})
        if n <= len(urls):
            ln = drv('links', r'grep=rate|pric|fee|rv|camp|site|reserv|book|stay|tarif', 'max=4000')
            host = re.sub(r'^https?://(www\.)?', '', u).split('/')[0]
            for row in ln.splitlines():
                h = row.rsplit(' -> ', 1)[-1].strip()
                if host in h and h not in seen and not re.search(r'\.(jpg|png|pdf)$|#|mailto|tel:', h, re.I) and re.search(r'rate|pric|fee|tarif', h + row, re.I):
                    queue.append(h)
    with open(out, 'a') as f: f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    print(i, r['name'][:40], len(rec['pages']), flush=True)
