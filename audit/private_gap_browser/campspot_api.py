# campspot_api.py OUT.jsonl [--extra TUE,SAT ...] ID:SLUG [ID:SLUG ...]
# Campspot prices read from Campspot's own API through the one driver browser (2026-10-13, written to price the 421
# tier-only entries that link to Campspot). The site pages campspot_site.py and campspot_market.py read take 10-20 s
# each; the API calls behind them carry the whole breakdown:
#  - /api/gator-core/v2/parks/slug/<slug>: the park record - id, engine slug ('slug') and marketplace slug
#    ('aggregatorSlug'; a marketplace slug resolves too), the guest categories in the park's order ('ageCategories'),
#    currency, and the operator's own latitude/longitude;
#  - /api/gator-core/v2/availability/parks/<id>?checkin&checkout&guests: every site type with its sites (longest rig,
#    amenities), the average nightly price with fees folded in, and failure reasons (RESORT_CLOSED_RULE,
#    RESERVATION_MIN_RULE ...). [] means the park takes no bookings for those dates yet;
#  - /api/gator-core/v2/<id>/campsite-types/availability/<type>/?checkin&checkout&guests: that type's 'pricing' - the
#    site charge before taxes, fees and discounts, any 'packageDiscounts', the park's own fees itemized by name
#    ('feeSummary', the "Campground Fees" line of the site page; a park may call its own fee 'Booking Fee'), Campspot's
#    'externalFees' (its booking fee, 3% with a $3 floor, the platform's and not the park's) and the taxes.
# Every call needs the header 'x-client-type: CONSUMER' ("Unknown request." without it) and a campspot.com page open
# in the driver. The guests string is the park's categories in order with 2 at the Adults one, plus a trailing pets
# slot ('guests0,2,0' for [Children, Adults]); a wrong one returns [] or MIN_MAX_AGE_GROUP_RULE.
#
# PACE: Campspot sits behind a CloudFront firewall that answered "403 Request blocked" after 590 calls in about six
# and a half minutes (2026-10-13, ~450 per 5 min), for this machine's address. So: one call every PAUSE seconds
# (default 3, ~100 per 5 min), and the run STOPS at the first blocked answer - the park being read is not written,
# so the same command picks up where it stopped once the block lifts.
#
# Per park: a Tuesday and a Saturday in each of PAIRS (none on a holiday weekend). A Tuesday on which the park lists
# nothing, or every RV type is closed, skips that pair's Saturday. Each date's list call gives every type's average
# with fees in, so only the types that set the range are priced in full: the cheapest (and each other price within
# 10% of it) and the dearest RV type a 23-ft rig fits. Then two nights from the first date with a park fee, on a type
# that carries it - the quote that tells a per-stay fee from a per-night one. If every date read is closed, the first
# closed one is priced anyway (the builder says so). One JSON line per park; campspot_tier_build.py reads them. Needs
# drv_server.py.
import datetime, json, os, re, socket, sys, time

SOCK = os.environ.get('DRV_SOCK') or os.path.expanduser('~/.cache/ekko-drv.sock')
PAUSE = float(os.environ.get('CS_PAUSE', '3'))
PAIRS = [("2026-10-20", "2026-10-17"), ("2027-01-26", "2027-01-30"), ("2027-06-08", "2027-06-12")]
# read only when no date in PAIRS gives a price: a northern park that closed in mid-October while 2027 is not yet open
# (Woodland Park MI: types on 2026-10-14, nothing from 2026-10-17 on). Tomorrow and the day after next, so a run that
# goes past midnight never asks for a date already gone.
def fallback_pairs():
    today = datetime.date.today()
    return [((today + datetime.timedelta(days=1)).isoformat(), (today + datetime.timedelta(days=3)).isoformat())]


# not a nightly RV site, by name: the same list as campspot_tier_build.py's SKIP - keep the two in step
SKIP = (r"(?i)\bgroup\b|horse|equestrian|\brally\b|^(?!.*\b(rv|camper|trailer)\b).*\btent\b|cabin|lodge|bunkhouse|"
        r"double site|buddy|pavilion|day use|day pass|^(?!.*\b(rv|camper|trailer)\b).*\b(boat slip|dock|slip)\b|"
        r"storage|glamp|yurt|tipi|teepee|cottage|motel|\broom\b|accessible|\bada\b|handicap|"
        # a long-stay product, unless the name also sells it by the night ('50 Amp Daily, Weekly RV Site', Sullivan
        # County IN)
        r"^(?!.*\b(daily|nightly|night|overnight|transient)\b).*(season|monthly|long[- ]term|\bweekly\b|annual|"
        r"yearly|winter stay)")


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


def api(path):
    time.sleep(PAUSE)
    js = ("fetch(%s,{headers:{'x-client-type':'CONSUMER','accept':'application/json, text/plain, */*'}})"
          ".then(r=>r.text())" % json.dumps(path))
    out = call(cmd='eval', js=js, max='8000000')
    try:
        return json.loads(out)
    except ValueError:
        if re.search(r'Request blocked|could not be satisfied|<!DOCTYPE', out):
            raise Blocked(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', out))[:160])
        return {'error': {'errors': [out[:300]], 'errorType': 'NOT-JSON'}}


def plus(d, n):
    return (datetime.date.fromisoformat(d) + datetime.timedelta(days=n)).isoformat()


def reasons(fr):
    return sorted({'%s: %s' % (f.get('errorType'), f.get('reason', '')) for f in fr or []})


def fits(t):
    """An RV site type a 23-ft rig fits: most of its sites take 23 ft or give no length."""
    return (t['code'] == 'rv' and not re.search(SKIP, t['name'] or '')
            and (not t['max_len'] or t['fit_sites'] * 2 >= max(t['sites'], 1)))


def quote(pid, tid, d, n, guests):
    r = api('/api/gator-core/v2/%s/campsite-types/availability/%s/?checkin=%s&checkout=%s&guests=%s'
            '&useCustomParkData=true&includeUnavailable=true' % (pid, tid, d, plus(d, n), guests))
    if 'error' in r:
        return {'type': tid, 'date': d, 'nights': n, 'error': r['error']}
    pr = r.get('pricing') or {}
    fs = pr.get('feeSummary') or {}
    fees = fs.get('itemizedCampgroundFeesWithoutLockFee')
    if fees is None:
        fees = fs.get('itemizedCampgroundFees') or []
    return {'type': tid, 'date': d, 'nights': n, 'availability': r.get('availability'),
            'fail': reasons(r.get('failureReasons')),
            'base': pr.get('tripTotalBeforeTaxesFeesAndDiscounts'),
            'net_avg': pr.get('averagePricePerNightBeforeTaxesAndFees'),
            'avg': pr.get('averagePricePerNight'),
            'discounts': pr.get('packageDiscounts') or [],
            'fees': [[f.get('name'), f.get('feeType'), f.get('price')] for f in fees
                     if f.get('feeType') != 'SITE_LOCK_FEE'],
            'external': [[f.get('name'), f.get('type'), f.get('price')] for f in pr.get('externalFees') or []],
            'taxes': pr.get('totalTaxes'), 'total': pr.get('tripTotal')}


def read_list(rec, pid, d, guests):
    lst = api('/api/gator-core/v2/availability/parks/%s?checkin=%s&checkout=%s&guests=%s'
              '&useCustomParkData=true&includeUnavailable=true' % (pid, d, plus(d, 1), guests))
    if not isinstance(lst, list):
        rec['lists'][d] = {'error': lst.get('error')}
        return []
    rows = []
    for t in lst:
        sites = t.get('campsites') or []
        lens = [(s.get('rvInfo') or {}).get('rvLengthMax') for s in sites]
        tid = str(t['id'])
        if tid not in rec['types']:
            rec['types'][tid] = {
                'name': t.get('name'), 'code': t.get('campsiteCategoryCode'), 'sites': len(sites),
                'max_len': max([x for x in lens if x] or [0]),
                'fit_sites': sum(1 for x in lens if not x or x >= 23),
                'amenities': sorted({a for s in sites for a in s.get('amenities') or []} | set(t.get('amenities') or [])),
                'rv_types': sorted({x for s in sites for x in (s.get('rvInfo') or {}).get('rvTypes') or []})}
        rows.append([tid, t.get('averagePricePerNight'), sum(s.get('availability') == 'AVAILABLE' for s in sites),
                     reasons(t.get('failureReasons')) + reasons([f for s in sites for f in s.get('failureReasons') or []])[:4]])
    rec['lists'][d] = rows
    return rows


def priced_types(rec, rows):
    """The fitting RV types that set the date's range: one per distinct price at or within 10% of the cheapest (a fee
    on some types only can put a type's site charge below one that lists cheaper), and the dearest. A type the list
    gives no price for is quoted too, up to four. Tipton County IN lists 16 RV types at one price: one quote, not 16."""
    fit = [(tid, avg) for tid, avg, *_ in rows if fits(rec['types'][tid])]
    known = sorted(((tid, avg) for tid, avg in fit if avg), key=lambda x: (x[1], x[0]))
    pick, seen = [], set()
    if known:
        lo = known[0][1]
        for tid, a in known:
            if a <= lo * 1.10 + 0.5 and round(a, 2) not in seen:
                pick.append(tid)
                seen.add(round(a, 2))
        pick.append(known[-1][0])
    pick += [tid for tid, a in fit if not a][:4]
    return list(dict.fromkeys(pick))


def main():
    # --extra TUE,SAT (repeatable): another pair read after PAIRS, for a park whose peak PAIRS misses (a beach resort's
    # July and August); the builder reports every month read
    args, extra = sys.argv[1:], []
    while '--extra' in args:
        i = args.index('--extra')
        extra.append(tuple(args[i + 1].split(',')))
        del args[i:i + 2]
    out_path, parks = args[0], [a.split(':', 1) for a in args[1:]]
    if 'campspot.com' not in call(cmd='url'):
        call(cmd='goto', url='https://www.campspot.com/', wait='6000')
    with open(out_path, 'a') as out:
        for eid, slug in parks:
            t0 = time.time()
            rec = {'id': int(eid), 'slug': slug, 'read': datetime.date.today().isoformat(), 'reader': 'v2'}
            try:
                park = api('/api/gator-core/v2/parks/slug/%s' % slug)
                if 'park' not in park:
                    rec['error'] = park.get('error') or park
                    out.write(json.dumps(rec) + '\n')
                    out.flush()
                    print(eid, slug, 'ERROR', json.dumps(rec['error'])[:160], flush=True)
                    continue
                p = park['park']
                cats = [c.get('name') or '' for c in sorted(p.get('ageCategories') or [],
                                                            key=lambda c: c.get('parkAgeCategoryIndex', 0))]
                adult = next((i for i, c in enumerate(cats) if c.lower().startswith('adult')), None)
                if adult is None:
                    adult = next((i for i, c in enumerate(cats) if 'adult' in c.lower()), None)
                rec.update(park_id=p['id'], name=p.get('name'), engine_slug=p.get('slug'),
                           aggregator_slug=p.get('aggregatorSlug'), aggregator=p.get('isAggregatorEnabled'),
                           city=p.get('city'), state=p.get('state'), currency=p.get('currencyUnit'),
                           pets=p.get('petsAllowed'), lat=p.get('latitude'), lng=p.get('longitude'),
                           phone=p.get('phoneNumber'), site=p.get('marketingSite'),
                           closed_dates=park.get('resortClosedDates'), cats=cats)
                if adult is None:
                    rec['error'] = 'no Adults category in %s' % cats
                    out.write(json.dumps(rec) + '\n')
                    out.flush()
                    print(eid, slug, 'ERROR', rec['error'], flush=True)
                    continue
                guests = 'guests' + ','.join(['2' if i == adult else '0' for i in range(len(cats))] + ['0'])
                rec.update(guests=guests, types={}, lists={}, quotes=[])
                pid = p['id']
                pairs, two_done = list(PAIRS) + extra, False
                while pairs:
                    tue, sat = pairs.pop(0)
                    for d in (tue, sat):
                        rows = read_list(rec, pid, d, guests)
                        rv = [x for x in rows if fits(rec['types'][x[0]])]
                        if d == tue and (not rv or all(any('RESORT_CLOSED_RULE' in f for f in x[3]) for x in rv)):
                            break                     # closed or not open yet: the Saturday says the same
                        for tid in priced_types(rec, rows):
                            rec['quotes'].append(quote(pid, tid, d, 1, guests))
                    if not two_done:
                        fee_q = next((q for d in (tue, sat) for q in rec['quotes']
                                      if q['date'] == d and q['nights'] == 1 and q.get('fees')), None)
                        if fee_q:
                            rec['quotes'].append(quote(pid, fee_q['type'], fee_q['date'], 2, guests))
                            two_done = True
                    if not pairs and not rec.get('fallback') and not any(q['nights'] == 1 for q in rec['quotes']):
                        rec['fallback'] = True
                        pairs = fallback_pairs()
                if not any(q['nights'] == 1 for q in rec['quotes']):
                    # every date read was closed: price the first that listed a fitting type anyway; the builder
                    # flags CLOSED DATES ONLY and the note says the park is shut on those dates
                    d = next((d for d, rows in rec['lists'].items() if isinstance(rows, list)
                              and any(fits(rec['types'][x[0]]) for x in rows)), None)
                    if d:
                        for tid in priced_types(rec, rec['lists'][d]):
                            rec['quotes'].append(quote(pid, tid, d, 1, guests))
            except Blocked as b:
                print(eid, slug, 'BLOCKED by Campspot (%s) - stopping; nothing written for this park' % b, flush=True)
                sys.exit(2)
            out.write(json.dumps(rec) + '\n')
            out.flush()
            rv = [t for t in rec['types'].values() if t['code'] == 'rv']
            print(eid, slug, '%s types (%d rv), %d quotes, %.0fs' % (len(rec['types']), len(rv), len(rec['quotes']),
                                                                  time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
