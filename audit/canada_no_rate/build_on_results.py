# build_on_results.py -> audit/on_private/results_norate.json (+ --wf after append_state.py:
# audit/on_private/waterfront_norate_results.json for apply_waterfront_audit.py).
# Same shape as build_qc_results.py, for the Ontario follow-up adds: adds_work.json (st == ON),
# on_wf_calls.jsonl (pin, waterfront call, evidence, elevation), notes/inclusion lines below
# (written by hand 2026-10-08). Ownership comes from the record (Lakefield is a township park).
import json, os, sys

ST = 'ON'
MIN_ID = 15165
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
adds = {k: v for k, v in json.load(open(os.path.join(HERE, 'adds_work.json'))).items() if v['st'] == ST}
calls = {json.loads(l)['key']: json.loads(l) for l in open(os.path.join(HERE, 'on_wf_calls.jsonl'))}
ver = {}
for l in open(os.path.join(REPO, 'audit/on_private/verdicts.jsonl')):
    r = json.loads(l)
    ver[r['name']] = r

NOTES = {
 'Lakefield Campground': "Township of Selwyn campground on 12-acre Hague Point at Lakefield, between the Otonabee River and the Lakefield Marsh: about 25 transient serviced sites (30A hydro and water) beside a larger seasonal section; beach, canoe/kayak launch and rentals, camper docks, comfort station, playground. 2026 rates: serviced C$55.11, unserviced C$46.08 a night + HST. Booked online (Let's Camp); 2-night minimum only on holiday weekends.",
 'Lifestylecamping': "RV park on the sandy shore of Wabigoon Lake in the City of Dryden (Trans-Canada Hwy 17, midway between Winnipeg and Thunder Bay); RV Life lists it under an old name (Lifestylecamping). 25 sites with 30A, water (drawn from the lake - boil to drink) and sewer, plus small-unit and tent sites; city boat launch next door, trails into town, limited washrooms. 2026 daily rates: treeside C$45, lakeview C$46, lakeside C$48, pull-through C$54. Reservation requests by form, e-mail or phone (1 Mar-1 Oct), full prepayment, one night at a time welcome. Season 1 May-15 Oct.",
 'Happy Holiday Campground and Cottages': "15-acre wooded campground on Lake Duncan at North Temagami (Hwy 11): large drive-thru RV sites (30A or 15A with grey water), tent sites, two cottages and rental trailers; laundromat. Posted rates: 30A C$53, 15A C$45 a night + tax; seasonal, weekly or nightly stays. Booking by phone.",
 'Gibbs Camping & RV Resort': "Good Sam Park on Shallow Lake beside Trans-Canada Hwy 11 at Mattice-Val Côté (between Hearst and Kapuskasing): 3-service RV lots and pull-throughs, tent lots, RV rentals, pool, chip stand, fishing; seasonal contracts too. 2027 daily RV-lot rates for 4 people: 3-service C$60 weekdays / C$70 Fri-Sun, pull-through C$80; long weekends may need 3 days. Summer reservations 15 May-15 Sep through the website or phone. Caveat (2026-10-08): the seasonal share was not measured.",
 'Aintree Trailer Park': "Family campground in Kincardine a short walk from the Lake Huron beach: 150 seasonal sites (1-5 year waitlist) and about 21 overnight sites - two-point back-in (30A, water, up to 40 ft), full-service back-in and drive-through, small-trailer/tent sites. 2026 rates including tax: two-point back-in C$71 (C$62.83 before HST), full service C$75 a night; one night to a few months. Booked online, one-day deposit per week. Season 7 May-Thanksgiving Monday.",
 'Green Acres Manitoulin - Family Campground': "Family campground and restaurant on Sheguiandah Bay of Georgian Bay (Hwy 6, Manitoulin Island): 22 numbered beachfront overnight sites on the shared sand beach, a few in-park sites, tent areas and seasonal blocks; water + 30A, washrooms/showers, boat launch, fish-cleaning station. Overnight rates: in-park C$57.99, beachfront C$59.99 a night + HST. Booked online (Let's Camp) or by phone.",
 'South Bay Park': "Campground on Dunlop Lake 10 km north of Elliot Lake: about 124 sites, 17 of them nightly RV sites (15A or 30A with water, no sewer, some pull-through, rigs to 35 ft) beside seasonal sites, tent sites and 63 boat docks; canoe, paddleboat, kayak and fishing-boat rentals, canteen, recreation hall. A July 2027 weeknight sells online at C$58 (15A water) or C$60 (30A); unserviced C$53. Booked online (Campspot).",
 'Pine Point Resort': "Fishing resort on Lac des Mille Lacs at Upsala near Trans-Canada Hwy 17 (west of Thunder Bay): about 24 full-hookup and 5 water/electric campsites in two inland rows, tent sites and cottages; docks, boat rentals, bait shop, gas bar, fish-cleaning station, laundromat, groceries. Posted campsite rates per night for 2 adults: full hookup C$56, water/electric C$52, + 13% HST (the operator's 2024 rate sheet, still the posted one in 2026). Reservations by e-mail or phone with a non-refundable deposit.",
}

SHARE = {
 'Lakefield Campground': 'township site map colours ~25 transient serviced sites; 2-night minimum only on holiday weekends',
 'Lifestylecamping': '25 full-hookup sites priced by the night, no seasonal tier on the rate page',
 'Happy Holiday Campground and Cottages': 'drive-thru RV sites "for seasonal, weekly or nightly visits"',
 'Gibbs Camping & RV Resort': 'seasonal share not measured (summer imagery only)',
 'Aintree Trailer Park': '150 seasonal + ~21 overnight sites in the CampLife engine (~12%)',
 'Green Acres Manitoulin - Family Campground': 'site map numbers 22 beachfront overnight sites beside the seasonal blocks',
 'South Bay Park': '17 nightly RV sites in the engine of ~124 (~14%)',
 'Pine Point Resort': '~29 full-hookup and water/electric campsites on the map; nightly, weekly and monthly rates',
}

SOURCE = {
 'Lakefield Campground': 'Township of Selwyn rate page live with nightly rates',
 'Gibbs Camping & RV Resort': 'operator site live with a 2027 daily rate table',
 'Pine Point Resort': 'operator site live with its (2024) nightly rate sheet',
 'South Bay Park': 'operator booking engine quote (Campspot)',
}


def main():
    missing = [k for k in adds if k not in NOTES or k not in SHARE or k not in calls]
    if missing:
        sys.exit('missing note/share/call for: %s' % missing)
    out = []
    for k, a in adds.items():
        c, v = calls[k], ver[k]
        base = v['base_rate']
        q = a['quality'].split(';')[0].strip()
        out.append({
            'name': a['display_name'],
            'location': c['pin'],
            'elevation_meters': c['elevation_meters'],
            'website': a['website'],
            'phone': a.get('phone', ''),
            'note': NOTES[k] + ' --Claude',
            'inclusion_evidence': '%s (C$%s, read 2026-10-08, no_rate follow-up); %s; %s%s; C$%s ~ US$%d'
                                  % (SOURCE.get(k, 'operator site live with nightly rates'), base, SHARE[k], q,
                                     ' with phone' if a.get('phone') else '', base, round(float(base) * 0.72)),
            'waterfront': c['waterfront'],
            'wf': c['wf'],
            'decision': 'add',
            'ownership': a.get('ownership', 'private'),
            'worklist_name': k,
        })
    p = os.path.join(REPO, 'audit/on_private/results_norate.json')
    json.dump(out, open(p, 'w'), ensure_ascii=False, indent=1)
    print('wrote', p, len(out))


def wf_results():
    cg = json.load(open(os.path.join(REPO, 'campgrounds.json')))
    res = json.load(open(os.path.join(REPO, 'audit/on_private/results_norate.json')))
    byname = {e['name']: e for e in cg if e.get('state') == ST and e['id'] >= MIN_ID}
    rows = []
    for r in res:
        e = byname.get(r['name'])
        if not e:
            print('not appended:', r['name'])
            continue
        rows.append({'id': e['id'], 'name': e['name'], 'current': e.get('waterfront'),
                     'final': r['waterfront'], 'coord_fix': None, 'elevation_meters': None,
                     'evidence': r['wf'], 'confidence': 'high'})
    p = os.path.join(REPO, 'audit/on_private/waterfront_norate_results.json')
    json.dump(rows, open(p, 'w'), ensure_ascii=False, indent=1)
    print('wrote', p, len(rows))


if __name__ == '__main__':
    wf_results() if '--wf' in sys.argv else main()
