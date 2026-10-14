# camplife_api.py OUT.jsonl ID:URL [ID:URL ...]
# camplife_api.py OUT.jsonl --entries ENTRIES.json [--only ID,ID,...]      (ENTRIES: [{id, website}, ...])
# CampLife prices read from CampLife's own booking API (2026-10-14, written to price the tier-only entries that link to
# camplife.com). AWS WAF answers plain HTTP with a challenge, so every call is a fetch() made inside a camplife.com page
# open in the one driver browser (drv_server.py; `drv.py quit` when done). The calls are the booking page's own
# (camplife.com/<id>/reservation/step1), none of which needs the UI:
#  - GET /api/campground/search/events/<encoded name>: the park record (id, address, phone, email, description). This
#    is how a camplife.com/campground/<Name> link becomes an id.
#  - GET /api/reservation/session?campgroundIdOrAlias=<id or alias>: the booking setup - site types (name, equipment
#    and amenity ids), the amenity and equipment names, and siteMap, every site sold online with its type. It points
#    the server-side session at that park, so it comes before the calls below.
#  - POST /api/campground/<id>/availability {checkinDate, checkoutDate (MM-DD-YYYY), numAdults 2, ...}: the open sites'
#    ids, or a 400 whose errors.general[].message is the park's own ("The park is open April 15th-October 15th.  We
#    begin accepting reservations on January 1.").
#  - GET /api/campground/<id>/site/<siteId>: the site's description, maxLength, width, amenity and equipment ids.
#  - POST /api/invoice/estimate {reservation: {checkinDate, checkoutDate, siteId, occupancy 2 adults}}: the quote,
#    resSubTotal (before tax) and items (taxes, and any charge the park names).
#
# Per park: the record and the session; then one night from each date in DATES (the RoverPass pass's: a Tuesday and a
# Saturday in October 2026, January 2027 and June 2027). If none opens a site, FALLBACK dates, stopping at the first
# two that do. On the first open date every open site is quoted for one night (up to ALL_MAX of them, else PER_TYPE of
# each site type, spread through the open list), and on later open dates PER_TYPE of each type, each quoted site's
# record read once. Then two nights from the first open date (a Tuesday where there is one) on the cheapest and the
# dearest site that fits a 23-ft rig: a charge once a stay hides inside resSubTotal unlabelled (Artillery Ridge PA's
# $17.50), and only the pair tells it from the nightly rate. One JSON line per park; camplife_tier_build.py reads them.
#
# PACE: one call per CL_PAUSE seconds (default 0.8). A WAF challenge (a 202, or HTML where JSON was due) reloads the
# park's booking page and retries once; a second stops the run without writing that park, so the same command resumes
# (parks already in OUT are skipped).
import datetime, json, os, re, socket, sys, time

SOCK = os.environ.get('DRV_SOCK') or os.path.expanduser('~/.cache/ekko-drv.sock')
PAUSE = float(os.environ.get('CL_PAUSE', '0.8'))
DATES = ["2026-10-20", "2026-10-17", "2027-01-26", "2027-01-30", "2027-06-08", "2027-06-12"]
FALLBACK = ["2026-10-15", "2026-10-24", "2026-11-03", "2026-11-14", "2026-12-08", "2027-03-16", "2027-04-20",
            "2027-05-11"]
ALL_MAX = 15
PER_TYPE = 3
HOME = 'https://www.camplife.com/%s/reservation/step1'


class Blocked(Exception):
    pass


def call(**req):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(240)
    s.connect(SOCK)
    s.sendall((json.dumps(req) + '\n').encode())
    buf = b''
    while not buf.endswith(b'\n'):
        c = s.recv(1 << 20)
        if not c:
            break
        buf += c
    r = json.loads(buf.decode())
    if not r['ok']:
        raise RuntimeError(str(r['out'])[:300])
    return r['out']


PAGE = {'cg': None}


def load(cg):
    try:
        call(cmd='goto', url=HOME % cg, wait='8000')
    except RuntimeError as ex:      # a slow page still loads behind a goto timeout
        if 'Timeout' not in str(ex):
            raise
        call(cmd='wait', wait='8000')
    PAGE['cg'] = cg


def api(method, path, body=None):
    js = ("(async()=>{const r=await fetch(%s,{method:%s,headers:{'content-type':'application/json'}%s});"
          "const t=await r.text();return JSON.stringify({s:r.status,c:r.headers.get('content-type')||'',t:t})})()"
          % (json.dumps(path), json.dumps(method), (',body:' + json.dumps(json.dumps(body))) if body is not None else ''))
    for attempt in (1, 2):
        time.sleep(PAUSE)
        try:
            r = json.loads(call(cmd='eval', js=js, max='50000000'))
        except (RuntimeError, ValueError) as ex:
            r = {'s': 0, 'c': '', 't': str(ex)}
        waf = r['s'] in (0, 202, 403, 405) or ('json' not in r['c'] and r['t'].lstrip()[:1] == '<')
        if not waf:
            try:
                return r['s'], json.loads(r['t']) if r['t'].strip() else None
            except ValueError:
                return r['s'], {'_text': r['t'][:500]}
        if attempt == 2:
            raise Blocked('%s %s answered %s %s' % (method, path, r['s'], r['t'][:120]))
        time.sleep(10)
        load(PAGE['cg'] or 1045)


def mdy(d):
    y, m, dd = d.split('-')
    return '%s-%s-%s' % (m, dd, y)


def nxt(d, n=1):
    return (datetime.date.fromisoformat(d) + datetime.timedelta(n)).isoformat()


def ref_of(url):
    u = url.strip()
    m = re.search(r'camplife\.com/(\d+)(?:[/?#]|$)', u) or re.search(r'cgId=(\d+)', u)
    if m:
        return 'id', m.group(1)
    m = re.search(r'camplife\.com/campground/([^/?#]+)', u)
    if m:
        return 'name', m.group(1)
    m = re.search(r'camplife\.com/([^/?#]+)/reservation', u)
    if m:
        return 'alias', m.group(1)
    m = re.search(r'camplife\.com/([^/?#]+)', u)
    return ('name', m.group(1)) if m else (None, None)


def fits(info):
    ml = (info or {}).get('maxLength')
    return not ml or ml >= 23


def read(eid, url):
    rec = {'id': eid, 'url': url, 'read': datetime.date.today().isoformat()}
    kind, ref = ref_of(url)
    rec['ref'] = [kind, ref]
    cg = int(ref) if kind == 'id' else None
    if kind == 'name':
        st, j = api('GET', '/api/campground/search/events/' + ref)
        cg = ((j or {}).get('campground') or {}).get('id')
        if cg:
            rec['record'] = j.get('details')
    if cg is None and ref:          # an alias, or a name the search doesn't know
        st, j = api('GET', '/api/reservation/session?campgroundIdOrAlias=' + ref)
        cg = ((j or {}).get('campground') or {}).get('id')
    if not cg:
        rec['error'] = 'no campground for %s %s' % (kind, ref)
        return rec
    rec['cg'] = cg
    if PAGE['cg'] is None:
        load(cg)
    st, s = api('GET', '/api/reservation/session?campgroundIdOrAlias=%s' % cg)
    if not s or not s.get('config'):
        rec['error'] = 'no booking setup (session answered %s)' % st
        rec['session'] = s
        return rec
    c = s['config']
    rec['name'] = (s.get('campground') or {}).get('name')
    rec['currency'] = (s.get('campground') or {}).get('currency')
    rec['config'] = {k: c.get(k) for k in ('siteTypes', 'maxSites', 'encodedName', 'campgroundPhone',
                                           'campgroundAddress', 'allowFlexibleDates', 'defaultCountry')}
    rec['config']['amenities'] = {str(a['id']): a['name'] for a in c.get('amenities') or []}
    rec['config']['equip'] = {str(e['id']): e['name'] for e in c.get('equipTypes') or []}
    rec['siteMap'] = {k: [v.get('name'), v.get('typeName')] for k, v in (s.get('siteMap') or {}).items()}
    if 'record' not in rec and c.get('encodedName'):
        st, j = api('GET', '/api/campground/search/events/' + c['encodedName'])
        rec['record'] = (j or {}).get('details')
        # the search may land on another park of the same name; the session is the authority
        if ((j or {}).get('campground') or {}).get('id') != cg:
            rec['record_mismatch'] = ((j or {}).get('campground') or {}).get('id')
        api('GET', '/api/reservation/session?campgroundIdOrAlias=%s' % cg)
    dates, sites, quotes = {}, {}, []

    def avail(d, n=1):
        st, j = api('POST', '/api/campground/%s/availability' % cg,
                    {'flexible': False, 'displayStartDate': '', 'checkinDate': mdy(d), 'checkoutDate': mdy(nxt(d, n)),
                     'cgAmenity': [], 'numAdults': 2, 'amenities': []})
        j = j or {}
        out = {'status': st, 'open': [x.get('id') for x in j.get('sites') or []]}
        msgs = [m.get('message') for v in (j.get('errors') or {}).values() for m in (v or []) if isinstance(m, dict)]
        if msgs:
            out['errors'] = msgs
        return out

    def quote(d, sid, n=1):
        if str(sid) not in sites:
            st, info = api('GET', '/api/campground/%s/site/%s' % (cg, sid))
            sites[str(sid)] = info
        st, j = api('POST', '/api/invoice/estimate',
                    {'reservation': {'checkinDate': mdy(d), 'checkoutDate': mdy(nxt(d, n)), 'siteId': sid,
                                     'occupancy': {'numAdults': 2, 'numChildren': 0, 'numPets': 0, 'numVehicles': 0},
                                     'equipment': {}, 'addOns': [], 'vehicles': []}})
        inv = (j or {}).get('invoice') or {}
        q = {'date': d, 'nights': n, 'site': sid, 'type': (rec['siteMap'].get(str(sid)) or [None, None])[1],
             'sub': inv.get('resSubTotal'), 'total': inv.get('total'), 'items': inv.get('items')}
        if not inv:
            q['answer'] = j if st != 200 else None
            q['status'] = st
        quotes.append(q)
        return q

    for d in DATES:
        dates[d] = avail(d)
    if not any(v['open'] for v in dates.values()):
        rec['fallback'] = []
        for d in FALLBACK:
            if d < rec['read']:
                continue
            rec['fallback'].append(d)
            dates[d] = avail(d)
            if sum(1 for v in dates.values() if v['open']) >= 2:
                break
    rec['dates'] = dates
    opened = sorted(d for d, v in dates.items() if v['open'])
    for k, d in enumerate(opened):
        ids = dates[d]['open']
        if k == 0 and len(ids) <= ALL_MAX:
            pick = ids
        else:
            by = {}
            for sid in ids:
                by.setdefault((rec['siteMap'].get(str(sid)) or [None, '?'])[1], []).append(sid)
            pick = []
            for t, xs in by.items():
                m = min(PER_TYPE, len(xs))
                pick += sorted(set(xs[int(i * (len(xs) - 1) / max(1, m - 1))] for i in range(m)), key=xs.index)
        for sid in pick:
            quote(d, sid)
    # two nights on the cheapest and the dearest fitting site of the first open date (a Tuesday where there is one)
    tues = [d for d in opened if datetime.date.fromisoformat(d).weekday() == 1]
    d0 = tues[0] if tues else (opened[0] if opened else None)
    if d0:
        one = [q for q in quotes if q['date'] == d0 and q['nights'] == 1 and q['sub'] is not None
               and fits(sites.get(str(q['site'])))]
        if one:
            lo, hi = min(one, key=lambda q: q['sub']), max(one, key=lambda q: q['sub'])
            for q in ([lo] if lo['sub'] == hi['sub'] else [lo, hi]):
                two = avail(d0, 2)
                if q['site'] in two['open']:
                    quote(d0, q['site'], 2)
                else:
                    quotes.append({'date': d0, 'nights': 2, 'site': q['site'], 'unavailable': True})
    rec['sites'] = sites
    rec['quotes'] = quotes
    return rec


def main():
    out = sys.argv[1]
    args = sys.argv[2:]
    if '--entries' in args:
        es = json.load(open(args[args.index('--entries') + 1], encoding='utf-8'))
        only = set(args[args.index('--only') + 1].split(',')) if '--only' in args else None
        todo = []
        for e in es:
            if only is not None and str(e['id']) not in only:
                continue
            u = [x for x in (e.get('website') or '').split('\n') if 'camplife.com' in x.lower()]
            if u:
                todo.append((e['id'], u[0]))
    else:
        todo = [(int(a.split(':', 1)[0]), a.split(':', 1)[1]) for a in args]
    done = set()
    if os.path.exists(out):
        done = {json.loads(l)['id'] for l in open(out, encoding='utf-8') if l.strip()}
    n = 0
    with open(out, 'a', encoding='utf-8') as fh:
        for eid, url in todo:
            if eid in done:
                continue
            try:
                rec = read(eid, url)
            except Blocked as ex:
                print('STOPPED at %s %s: %s; run the same command again to resume' % (eid, url, ex), flush=True)
                break
            fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
            fh.flush()
            n += 1
            opened = [d for d, v in (rec.get('dates') or {}).items() if v['open']]
            subs = sorted({q['sub'] for q in rec.get('quotes') or [] if q.get('nights') == 1 and q.get('sub') is not None})
            print(eid, rec.get('cg'), rec.get('name') or rec.get('error'), '| open', opened,
                  '| one-night', (subs[0], subs[-1]) if subs else '-', flush=True)
    print(n, 'parks written')


if __name__ == '__main__':
    main()
