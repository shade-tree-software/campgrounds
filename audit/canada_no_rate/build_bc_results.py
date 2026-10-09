# build_bc_results.py -> audit/bc_private/results_norate.json (+ --wf after append_state.py:
# audit/bc_private/waterfront_norate_results.json for apply_waterfront_audit.py).
# Same shape as build_on_results.py, for the British Columbia follow-up adds: adds_work.json
# (st == BC), bc_wf_calls.jsonl (pin, waterfront call, evidence, elevation; the per-image log is
# bc_wf_log.md), notes/inclusion lines below (written by hand 2026-10-09). All ten are private
# (Ashnola is a Lower Similkameen Indian Band campground - First Nations parks are private in BC).
import json, os, sys

ST = 'BC'
MIN_ID = 15172
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
adds = {k: v for k, v in json.load(open(os.path.join(HERE, 'adds_work.json'))).items() if v['st'] == ST}
calls = {json.loads(l)['key']: json.loads(l) for l in open(os.path.join(HERE, 'bc_wf_calls.jsonl'))}
ver = {}
for l in open(os.path.join(REPO, 'audit/bc_private/verdicts.jsonl')):
    r = json.loads(l)
    ver[r['name']] = r

NOTES = {
 'Sunshine Valley RV Resort': "Holiday Trails Resorts park at 14850 Alpine Blvd in Sunshine Valley on Hwy 3, about 20 km east of Hope near Manning Park: 110 fully serviced 50A RV sites (back-ins, pull-throughs and ATV sites), tent camping and 10 cabins; Great Room event hall; open year-round to members and the public. A Tuesday mid-October 2026 night sells online at C$49 for a full-hookup site plus a C$7 reservation fee and tax. Booked online (RezExpert), 7-day cancellation, 19+ to book; Good Sam/BCAA discounts by phone. Caveat (2026-10-08): summer 2027 rates were not yet loaded, so the C$49 quote is a shoulder-season night.",
 "Barney's Lakeside Resort": "Fishing resort on Puntzi Lake at 3556 Puntzi Lake Rd, Chilanko Forks (off Hwy 20 in the Chilcotin, west of Williams Lake): 9 extra-large full-hookup pull-through RV sites, 2 partial (water/power) and 4 dry sites - a row of RV lots along the shore - plus tent spots, cabins and a 7-bedroom lodge; showers, flush toilets, sani-dump (C$20), boat house, fish-cleaning house, boat launch and docks; boat, kayak, canoe and paddleboard rentals. Online rates: full-hookup RV lots from C$50 a night, semi-hookup C$45, dry sites C$40; no minimum on RV lots (2 nights on the luxury cabins only). Booked online.",
 'Baily Bridge Campsites': "Small campground on the Bella Coola River at 2375 Saloompt Road, Hagensborg (Bella Coola Valley, off Hwy 20): 27 numbered campsites, 15A/30A powered and unpowered, in old forest between the river and the road, water fill-up at the main entrance, rustic cabins, a boat launch and a sandy beach; river fishing and hiking nearby. Online engine (October 2026): 30A or 15A powered campsites from C$40 a night, unpowered C$35. Booked online. Caveat (2026-10-09): summer 2027 was not yet loaded; the Hwy 20 'Hill' into the valley has steep gravel grades.",
 'Bella Coola Valley Campground': "Family-run campground (est. 2021) at 1875 Highway 20, Hagensborg, beside the Augsburg Church in the Bella Coola Valley: full-hookup 20A sites 1-9 for small and mid-size units, 30A full-hookup sites 15-16 for rigs over 30 ft, power-only 20A sites, tent sites along two small creeks, and three spruce cabins; shower house with flush toilets, coin showers and laundry, sani-station. Posted nightly prices including tax: full hookup C$42.00 per unit, power-only C$36.75, unserviced C$31.50. Reservations by e-mail, text or phone (site numbers first-come; no long-term stays). Season May-October. Caveat: the Hwy 20 'Hill' into the valley has steep gravel grades.",
 'Cedar Falls Campground': "Forested campground at 7063 Tillicum Rd outside Vernon, a short walk from BX Falls and the BX Trail: 56 numbered sites, about 29 of them RV sites (15A, 15A + water, 30A, 30A + water and a few full hookups; many for rigs to 40 ft), plus tent sites and a cabin; washrooms and showers cleaned daily, laundry; some long-term pads. A Tuesday July 2027 night sells online at C$45 (15A + water), C$52 (30A + water), C$40 unserviced, before tax. Booked online (Campspot).",
 'Snaʕsnulax̌tn (Ashnola) Campground': "Lower Similkameen Indian Band campground at the pow-wow grounds, 1400 Ashnola Road off Hwy 3 about 10 minutes from Keremeos, in pine parkland by the river below the Ashnola Mountains: about 55 sites on 33 acres, indoor showers and restrooms, cook house and arbour. 2026 rate: campground sites C$35 a night (corridor sites C$20); cash only. Book by phone or text. Season 1 May-15 Oct 2026. Caveat (2026-10-09): hookups are not confirmed on any source - plan to dry camp.",
 'Gold Panner Campground': "Campground at 423 Hwy 6, Cherryville, between Vernon/Lumby and the Arrow Lakes, beside Cherry Creek: about 45 RV sites - dry, 15A, 30A, 30A + water and 30A full-hookup back-ins and pull-throughs for rigs to 55-60 ft - plus tent and hike-in sites, cabins, trails and RV storage; dry camping in fall and winter. A Tuesday July 2027 night sells online at C$49.55 (15A), C$51.45 (30A), C$54.30 (30A + water), C$56.20 (full hookup), before tax. Booked online (Campspot). Caveat (2026): the full-hookup septic was noted as temporarily unavailable.",
 'Kayanara Guest Ranch': "Farm-stay guest ranch at 3446 Hendrix Rd, Eagle Creek (South Cariboo, near Canim Lake and 100 Mile House): 6 full-hookup RV sites (3 with 50A, 3 with 30A, 2 pull-throughs) with picnic tables and fire pits, a residential-style bathroom, laundry, store and playground, plus cabins. A Tuesday July 2027 night sells online at C$44 for a standard full-hookup RV site; 10-35% off longer stays. Single nights bookable online with a 50% deposit.",
 'Lake Front RV Resort': "RV park at 6310 Stickle Rd on the west side of Hwy 97 at the north edge of Vernon, on the shore of Swan Lake: 47 full-service 50A, 6 full-service 30A and 28 half-service (30A + water) sites, the westernmost row along the lake, plus 16 permanent manufactured homes on the highway side; washrooms, showers, laundry, sani-dump (C$10), dog run, dock and canoe rentals. Posted daily rates: half service C$50, full service C$65, + 5% tax; monthly stays by inquiry. Booked online (Cloudbeds).",
 'Heritage Campsite & RV Park': "Campground and RV park at 3961 Hwy 97, Monte Lake (between Westwold and Falkland, 30 minutes from Kamloops), on a pine slope across the highway from the lake: up to 40 sites with 30A power, water and sewer, big rigs and pull-throughs; showers, toilets, laundry, Wi-Fi, tipi rentals; no wood fires. Posted (May 2026): full hookup C$45 nightly, C$270 weekly, C$850 monthly, plus taxes; tenting C$20. Book by phone or e-mail. Open year-round. Caveat (2026-10-09): long-stay residents share the park - about 25 units sit on the pads in mid-April imagery, as many as in June - so perhaps 15 sites turn over to travellers.",
}

SHARE = {
 'Sunshine Valley RV Resort': '110 full-service sites priced by the night in the engine (members and public)',
 "Barney's Lakeside Resort": '15 RV lots priced by the night in the booking widget, no RV minimum',
 'Baily Bridge Campsites': '27 numbered campsites + cabins, powered sites priced by the night in the engine',
 'Bella Coola Valley Campground': '~30 numbered sites priced by the night; "we do not offer long-term stays"',
 'Cedar Falls Campground': '~29 RV + 15 tent sites in the engine of 56 (some long-term pads)',
 'Snaʕsnulax̌tn (Ashnola) Campground': '~55 nightly sites, May-October season',
 'Gold Panner Campground': '~45 transient RV sites in the engine',
 'Kayanara Guest Ranch': '6 RV sites, single nights bookable online',
 'Lake Front RV Resort': '81 RV sites on daily rates beside 16 permanent manufactured homes (~15% of lots; monthly by inquiry)',
 'Heritage Campsite & RV Park': '~25 of up to 40 pads hold units in mid-April 2025 imagery and ~20 in June 2024 (year-round long-stay residents), leaving ~15 traveller sites (~35-40%)',
}

SOURCE = {
 'Sunshine Valley RV Resort': 'operator booking engine quote (RezExpert)',
 "Barney's Lakeside Resort": 'operator booking widget (Wix Hotels) with nightly RV-lot rates',
 'Baily Bridge Campsites': 'operator booking engine quote (Wix Hotels)',
 'Bella Coola Valley Campground': 'operator site live with posted nightly rates (tax included)',
 'Cedar Falls Campground': 'operator booking engine quote (Campspot)',
 'Snaʕsnulax̌tn (Ashnola) Campground': 'operator site live with the 2026 posted rate',
 'Gold Panner Campground': 'operator booking engine quote (Campspot)',
 'Kayanara Guest Ranch': 'operator booking engine quote (SiteMinder)',
 'Lake Front RV Resort': 'operator rate page + booking engine quote (Cloudbeds)',
 'Heritage Campsite & RV Park': 'operator rate page live (May 2026) with nightly rates',
}

CAVEAT = {
 'Sunshine Valley RV Resort': 'caveat (2026-10-08): shoulder-season quote, summer 2027 not loaded',
 'Baily Bridge Campsites': 'caveat (2026-10-09): October quote, summer 2027 not loaded',
 'Snaʕsnulax̌tn (Ashnola) Campground': 'caveat (2026-10-09): hookups not confirmed, cash only',
 'Gold Panner Campground': 'caveat (2026): full-hookup septic temporarily unavailable',
 'Heritage Campsite & RV Park': 'caveat (2026-10-09): long-stay residents hold over half the pads',
}

READ = {'Sunshine Valley RV Resort': '2026-10-08'}


def main():
    missing = [k for k in adds if k not in NOTES or k not in SHARE or k not in SOURCE or k not in calls]
    if missing:
        sys.exit('missing note/share/source/call for: %s' % missing)
    out = []
    for k, a in adds.items():
        c, v = calls[k], ver[k]
        base = v['base_rate']
        q = a['quality'].split(';')[0].strip()
        inc = ('%s (C$%s, read %s, no_rate follow-up); %s; %s%s; C$%s ~ US$%d'
               % (SOURCE[k], base, READ.get(k, '2026-10-09'), SHARE[k], q,
                  ' with phone' if a.get('phone') else '', base, round(float(base) * 0.72)))
        if k in CAVEAT:
            inc += '; ' + CAVEAT[k]
        out.append({
            'name': a['display_name'],
            'location': c['pin'],
            'elevation_meters': c['elevation_meters'],
            'website': a['website'],
            'phone': a.get('phone', ''),
            'note': NOTES[k] + ' --Claude',
            'inclusion_evidence': inc,
            'waterfront': c['waterfront'],
            'wf': c['wf'],
            'decision': 'add',
            'ownership': a.get('ownership', 'private'),
            'worklist_name': k,
        })
    p = os.path.join(REPO, 'audit/bc_private/results_norate.json')
    json.dump(out, open(p, 'w'), ensure_ascii=False, indent=1)
    print('wrote', p, len(out))


def wf_results():
    cg = json.load(open(os.path.join(REPO, 'campgrounds.json')))
    res = json.load(open(os.path.join(REPO, 'audit/bc_private/results_norate.json')))
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
    p = os.path.join(REPO, 'audit/bc_private/waterfront_norate_results.json')
    json.dump(rows, open(p, 'w'), ensure_ascii=False, indent=1)
    print('wrote', p, len(rows))


if __name__ == '__main__':
    wf_results() if '--wf' in sys.argv else main()
