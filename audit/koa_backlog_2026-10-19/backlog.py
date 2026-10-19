"""KOA backlog (AWH 2026-10-19: the KOA brand skip is retired; vet KOAs like any private park).

RV Life KOAs rated 4*+ that private_gap_list.held() finds no database entry for, matched to koa.com's
own directory slug (koa_directory.json, read off koa.com/campgrounds/ through the driver browser).
Writes backlog.json."""
import json, os, re, sys, difflib
from urllib.parse import quote
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import private_gap_list as pg  # noqa: E402

OUT_OF_SCOPE = {'AK', 'HI', 'YT', 'NT', 'NU'}
# RV Life name -> koa.com slug, checked by hand where the names differ (None = not in KOA's directory today:
# a park that left the franchise, or RV Life's stale duplicate of one that is)
OVERRIDES = {'Tucson / Lazydays KOA Resort': 'tucson', 'Willcox / Cochise, AZ KOA Holiday': 'willcox',
             'Alamosa KOA Journey': 'alamosa', 'Lake Oconee KOA/North Shore Landing': 'lake-oconee',
             'Coloma / St. Joseph KOA Holiday': 'coloma', 'Cody KOA Holiday': 'cody',
             'Mylan Park KOA Holiday Campground': 'morgantown', 'Lava Hot Springs West KOA': None,
             'Allendale / West Grand Rapids KOA': None, 'Higgins Lake / Roscommon KOA': None, 'Weidman KOA': None,
             'Wapakoneta KOA Journey': None, 'Buffalo / I-40 / Exit 143 KOA Journey': None,
             "Chain O'Lakes Resort Park & Campground/KOA": None}


def norm(s):
    s = s.lower().replace('&', ' and ')
    s = re.sub(r'\b(koa|holiday|journey|resort|campground|kampground)\b', ' ', s)
    return ' '.join(re.findall(r'[a-z0-9]+', s))


db = pg.entries()
hits, page = [], 0
while True:
    d = pg.rv_query(f"query=KOA&hitsPerPage=1000&page={page}"
                    f"&attributesToRetrieve={quote(','.join(pg.RV_ATTRS))}&attributesToHighlight=")
    hits += d['hits']; page += 1
    if page >= d.get('nbPages', 1):
        break
directory = json.load(open(os.path.join(HERE, 'koa_directory.json')))
dnorm = {norm(r['name']): r for r in directory}
out, skipped = [], {'under 4*': 0, 'in db': 0, 'closed/out of scope': 0}
for p in hits:
    n = p.get('cg_name') or ''
    if not re.search(r'\bKOA\b', n):
        continue
    st = p.get('region_abbvr')
    if st in OUT_OF_SCOPE or p.get('closed') or p.get('temp_closed'):
        skipped['closed/out of scope'] += 1; continue
    g = p.get('_geoloc') or {}
    ok, why = pg.held(n, g.get('lat'), g.get('lng'), db)
    if ok:
        skipped['in db'] += 1; continue
    if (p.get('star_rating') or 0) < 4:
        skipped['under 4*'] += 1; continue
    k = norm(n)
    m = dnorm.get(k)
    score = 1.0 if m else 0
    if n in OVERRIDES:
        s = OVERRIDES[n]
        m = next((r for r in directory if r['slug'] == s), None) if s else None
        score = 1.0 if m else 0
    elif not m:
        best = difflib.get_close_matches(k, list(dnorm), n=1, cutoff=0.6)
        if best:
            m = dnorm[best[0]]; score = round(difflib.SequenceMatcher(None, k, best[0]).ratio(), 2)
    out.append({'rv_id': p['objectID'], 'name': n, 'state': st, 'lat': g.get('lat'), 'lng': g.get('lng'),
                'stars': p.get('star_rating'), 'reviews': p.get('cg_rating_count'), 'price_level': p.get('price_level'),
                'avg_rate': p.get('avg_rate'), 'sites': p.get('cg_site_count'), 'url': 'https://campgrounds.rvlife.com' + (p.get('url') or ''),
                'koa_name': m and m['name'], 'slug': m and m['slug'], 'match': score})
out.sort(key=lambda r: (r['state'], r['name']))
json.dump(out, open(os.path.join(HERE, 'backlog.json'), 'w'), indent=1, ensure_ascii=False)
print(len(out), skipped, 'unmatched:', sum(1 for r in out if not r['slug']),
      'fuzzy:', sum(1 for r in out if r['slug'] and r['match'] < 1))
