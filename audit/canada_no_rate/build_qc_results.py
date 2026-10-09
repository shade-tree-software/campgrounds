# build_qc_results.py -> audit/qc_private/results_norate.json (+ the waterfront results that
# apply_waterfront_audit.py reads, once the ids are known: run with --wf after append_state.py).
# Inputs: adds_work.json (one record per follow-up add), qc_wf_calls.jsonl (pin, waterfront call,
# evidence, elevation per add), the notes / inclusion lines below (written by hand 2026-10-08).
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
adds = {k: v for k, v in json.load(open(os.path.join(HERE, 'adds_work.json'))).items() if v['st'] == 'QC'}
calls = {json.loads(l)['key']: json.loads(l) for l in open(os.path.join(HERE, 'qc_wf_calls.jsonl'))}
ver = {}
for l in open(os.path.join(REPO, 'audit/qc_private/verdicts.jsonl')):
    r = json.loads(l)
    ver[r['name']] = r

# DEM reads 0 m on the beach-side pin (sea cell); the street 25 m inland reads 3 m.
ELEV_FIX = {'Camping du Rivage': 3.0}
# Website lines that are not the campground's own or booking site.
DROP_SITE = ('bonjourquebec.com',)

NOTES = {
 'Camping Baie Du Diable': "Large campground (316 sites, a big seasonal share) on the point between the Baskatong reservoir and its Baie du Diable arm near Ferme-Neuve, with a long sand beach and a marina; full-hookup Pionniers section on the point, 30A Aventuriers section to the north-east. Posted rates C$50 water+electric / C$60 full hookup + tax (2024 table, still the operator's list in 2026; the official 2026 maximum is the same C$60). Reservations by phone only, 30% non-refundable deposit. Season mid-May to early October.",
 'Camping Belle Montagne': "Formerly Camping Belle-Montagne, now one of the five Camping au Soleil parks: about 138 sites at Saint-Paulin (Mauricie), part seasonal, with a pool. One night sold online at C$60 + tax on every hookup type (October 2026 quote; 2026 posted traveller rates C$60-70). Open 9 May-19 Oct 2026.",
 'Camping St-Edouard': "About 450-site family campground beside the Zoo de St-Édouard at Saint-Édouard-de-Maskinongé, roughly 45 traveller 3-service sites plus water/electric and unserviced sites beside a large seasonal section; heated pools and a pond with island sites. 2-service C$59.14 / 3-service C$60.89 a night + tax (operator rate page, 2026). 2 nights on weekends, 3 on holidays, one-night deposit. Season 7 May-26 Sep 2027.",
 'Camping la Descente des Femmes': "46-site village campground at Sainte-Rose-du-Nord on the Saguenay fjord (26 three-service 15A RV sites, 20 tent sites), with an artificial swimming pond. 3-service sites C$45 a night for up to 4 people (operator reservation page; the official 2026 maximum is C$45). RV sites by phone reservation, tents first-come; cash only. Season June to mid-October; the operator site was last updated in 2024.",
 'Camping la Detente': "Large family campground in Drummondville (Saint-Charles sector) off A-20 exit 181, about 400 sites with a big seasonal section; pool and a swimming pond ringed by 3-service sites. 2-service C$45 / 3-service C$50 a day, taxes included (2026 price list). Phone reservations 10:00-21:00.",
 'Camping Lac-Aux-Sables': "About 300-site campground at the Lac-aux-Sables village beach (Mauricie), roughly 75-80 traveller sites and the rest seasonal; the beach row (204-209) faces the public beach across a car-free road. 2026 transient rates: 2-service C$52.62, 3-service C$58.18, beach-row 3-service C$64.26 a day + tax. Online reservations need 2 nights, but same-day single nights are accepted; beach-row sites go Friday-to-Friday in peak summer, by phone. Open 15 May-12 Oct 2026.",
 'Camping Lac Frontiere (Border Lake)': "About 120-site campground on spring-fed Lac Crystal (no motorboats) at Stanstead, 1 km from the Vermont border on Route 143; 23 trailer sites and 9 two-service van/camper sites are sold online, the rest seasonal; pool and splash pad. Travel-trailer sites C$52-56 a night + C$3.75 one-time fee + tax; single nights bookable online. Season 8 May-27 Sep 2026.",
 'Camping Lac et Foret': "About 200-site campground on Lac Croche at Sainte-Thècle (Route 153), with a heated wave pool, farmyard and BMX track; the lake and docks are reached by a path. Traveller rates 2-service 20A C$57, 30A C$63, 3-service C$67-70 a night + C$4.50 booking fee. Booked online; 2-night weekend and 3-night holiday minimums.",
 'Camping Lac-des-Plaines': "About 200-site family campground around a sand-beach swimming lake at Sainte-Anne-des-Plaines, roughly 40-50 traveller sites (2- and 3-service) and the rest seasonal; restaurant, mini-golf. 2026 traveller rate C$69 a day for 2- or 3-service 30A (lakeside and 50A C$72). 2-night weekend and 3-night holiday minimums, 50% deposit. Open 21 Apr-21 Oct 2026.",
 'Camping Domaine Du Lac Libby': "About 350-site wooded campground on Lac Libby at Saint-Étienne-de-Bolton (A-10 exit 100), roughly 90 traveller sites (0-, 2- and 3-service) and a seasonal section; beach on the lake; cannabis-free. 2026: water+electric C$53, full hookup C$55, Mont des Huards 30/50A C$68 a night + tax; booked online. Caveat (2026-10-08): the only date the online engine could be tested (Thanksgiving week) required 2 nights; the operator posts per-night rates and no written minimum, so the weekday single-night policy is unconfirmed.",
 'Camping Plage des Sables': "About 250-site campground around a man-made swimming lake with a beach and inflatable water park on Route 116 at Princeville, roughly 76 traveller sites (concrete 50A pads and a lake-view row) and the rest seasonal; direct access to the Parc linéaire des Bois-Francs bike trail. 2026 traveller 3-service 50A C$68 a night + tax (beach sector C$75-78). 2-night weekend and 3-night holiday minimums, 50% deposit.",
 'Camping Du Parc': "About 170-site campground on Route 351 at Saint-Mathieu-du-Parc, near La Mauricie National Park; swimming pond with a beach, pool and splash pad; seasonal sites full with a waitlist. 2026: 2-service 20A C$55, 30A C$58, 3-service C$64 a day + tax. Online bookings need 2 nights; single nights by phone 48 hours ahead. Open 15 May-12 Oct 2026.",
 'Camping St-Boniface': "Small family campground (about 70 sites, part seasonal) on Route 153 at Saint-Boniface near Shawinigan, with a pool, chalets and rental trailers. 2026 traveller rates 2-service C$49 / 3-service C$54 a day + tax. Online booking new for 2026. Season 15 May-12 Oct 2026.",
 'Camping Vallee Bleue Resort, Enr.199426': "About 250-site campground around a lake with a beach and a lagoon pool at West Brome, near Bromont and Sutton on the wine route; roughly 48 traveller sites (including lakeshore 3-service sites 510-515) and the rest seasonal. 2026 peak rates: 2-service 15A C$58.27, 3-service 30A C$67.84 (waterfront C$71.32) a night + reservation fee + tax. Open 1 May-15 Oct 2026.",
 'Camping Causapscal Chez Moose': "84-site campground on five terraces at Causapscal in the Matapédia valley (Route 132), with 3-service sites 70-85 ft long; July is rented by the day only. Official 2026 maximum C$52 a night (2025 operator table C$40-48, taxes included; 2027 not yet posted). Booked online. Season early June to early September.",
 'Camping Sainte-Emilie': "Campground on the Rivière Noire at Sainte-Émélie-de-l'Énergie (Lanaudière), formerly Camping Ste-Émélie; about 60 traveller sites open online in July, riverside 2-service sites, a supervised beach, a dog beach and a Level-2 EV charger. 2026: 2-service C$56-57, riverside C$63, 3-service C$61 a night; single July 2027 nights sold online from C$59. Season about 10 May-14 Oct.",
 "Le Domaine de l'Ange Gardien": "About 110-site campground beside the family sugar shack and tubing hill at L'Ange-Gardien (Outaouais), 25 min from Ottawa-Gatineau; 3-service 30A sites 30-73 ft, pool and swimming pond. Single nights sold online: July 2027 3-service 30A C$54, 50A C$57.50 (2025 rate page 2-service C$51-55 + tax).",
 'Camping Soleil': "About 305-site family campground at Kinnear's Mills (Chaudière-Appalaches) along the Osgood River, roughly 75 traveller sites (2- and 3-service) and the rest seasonal; pool, splash pad, outdoor stage. Posted traveller rates 2-service C$62 / 3-service C$70 a night; a July 2027 weeknight sells online at C$65 (2-service 30A) + C$4.50 booking fee + tax.",
 'Camping Ecologique de Frelighsburg': "About 120-site campground on the Rivière aux Brochets at Frelighsburg on the wine route, 0.5 km from the West Berkshire (Vermont) crossing; riverside sites, pool, mini-farm. Before tax: 2-service 30A C$51, 3-service C$56, 50A C$63 a day. Booked online; 2-night weekend and 3-night holiday minimums.",
 'Camping des Etoiles': "Seaside campground on Route 132 at Hope Town on the Baie des Chaleurs (Gaspésie): full-hookup 30/50A sites, including pull-throughs, run down toward the bluff over the bay. 2026 high season (1 Jul-19 Aug) 3-service 30A C$49 a night + fees + tax; single nights sold online. Season 1 Jun-15 Sep.",
 'Camping la Rochelle': "Family campground at Trois-Rivières beside a bike path, with a pool, BMX and pickleball; a large seasonal section plus about 75 bookable 3-service traveller sites. Posted water+electric C$55 / full hookup C$60 + tax; the online engine sells one July 2027 weeknight on a 3-service 30A site at C$62 + C$4 fee (2-service sites need 2 nights).",
 'Camping la Pinede': "23-hectare campground at Lac-Simon (Petite-Nation, Outaouais): 25 traveller sites with 2-3 services (30A) along the river frontage and 120 seasonal sites; beaches, trails, mini-farm. 2-service C$60 weeknights / C$70 weekends, 3-service C$65 / C$75 a night. Online booking with an account, or a request form; pump-out C$30 for 2-service sites.",
 'Camping Horizon': "200+-site family campground on Route 125 at Saint-Roch-de-l'Achigan (Lanaudière), near Terrebonne; about 35 traveller sites (2- and 3-service), the rest seasonal; pool, splash pad. 2-service C$52 / 3-service C$65 a day + tax (2 adults + 2 children). Booked online.",
 'Camping Oasis': "About 460-site family campground at Sainte-Cécile-de-Milton near Granby, roughly 55 traveller sites and the rest seasonal; swimming lake with a beach, pool and spas, chalets. 2026: 2-service C$59.50, 3-service C$65 a night + tax (C$10 extra on a few holiday nights). Booking by request form or phone; 2-night minimum only on discounted nights.",
 'Camping du Rivage': "38-site seaside campground on the St. Lawrence beach at Sainte-Anne-des-Monts (Gaspésie), 2 km from downtown and 20 min from Parc national de la Gaspésie; 15/30A water+electric or full-hookup sites, dump station. RV 2-service C$55 / 3-service C$60 a night, taxes included (C$47.84 / C$52.19 before tax; the official 2026 maximum is C$52.19). Booking by phone or e-mail. Season mid-May to mid-October.",
 'Camping Beau-Soleil, Enr.200561': "Family campground at Weedon (Haut-Saint-François) on Route 112, with open pull-through traveller loops beside a seasonal section, a pool and a pond. Traveller 2-service C$45, 3-service 30A C$49, 50A C$60 a night. Booked online or by phone (2027 bookings from 1 March).",
 'Camping de la Demi-Lieue': "Camping Union network campground on the St. Lawrence at Saint-Jean-Port-Joli, 360+ sites including a seasonal section; pool. 2026: 2-service C$56.60, 3-service C$64.00, riverside 2-service C$67.29 a night + tax. Online reservations need 2 nights, but the same-day Nuitée Express (bought after 16:00, out by 09:00, 20% off) and walk-ins sell single nights. Season from 15 May.",
 'Camping du Gouffre': "Camping Union network campground on a bend of the Rivière du Gouffre at Baie-Saint-Paul (Charlevoix), with pull-through, central and riverside sections. 2026: 2-service C$56.60, 3-service C$64.00 a night + tax. Online reservations need 2 nights; the same-day Nuitée Express (after 16:00, out by 09:00, 20% off) and walk-ins sell single nights.",
 'Camping Domaine des Erables - Parkbridge': "Parkbridge RV resort with 600+ sites at Saint-Roch-de-Richelieu (Montérégie, 45 min from Montréal): about 130 Voyageur sites (2-3 services, 30/50A, pull-throughs, many along the trout-fishing pond) beside a large seasonal section; pool, splash pad. Online engine, Tuesday 13 Jul 2027: Voyageur full service 30A C$57 a weeknight (C$73 Fri-Sat), 50A C$60, + GST/QST.",
 'Camping Domaine Ensoleille': "65-unit seaside campground on Route 138 at Baie-Trinité (Îlets-Caribou, Côte-Nord, Whale Route), above a tidal bay of the St. Lawrence with a sandy beach; unserviced seaside sites, 1-service panoramic sites and 3-service 20/30A sites (some for 40 ft+); restaurant, store. Official 2026 maximum C$54.95 a night for any campsite; booked online. Season mid-May to late September.",
 'Camping Sainte Madeleine, Enr.199662': "282-site campground beside Autoroute 20 exit 120 at Sainte-Madeleine (traffic noise on the east side), about 200 sites seasonal and 77 sold online; the Rivière Huron runs through the park; pool, splash pad, disc golf. 2026: one night C$55 water+electric, C$59 3-service + tax (10% off before 4 June and after 14 September); a July 2027 weeknight sells online at C$59. Season about May to September.",
 'Camping 2 Rivieres': "200+-site campground at the confluence of two rivers at Saint-Gédéon-de-Beauce (Route 204), part seasonal; heated pool, canteen, dek hockey, BMX and ninja courses, river fishing; new owners since 2021. 2026: 2-service C$56-58, 3-service 30A C$62 a night + tax (2 adults + 2 children). Serviced sites are booked by contacting the office; only rustic field sites sell online.",
 'Camping la Mine de Cuivre': "About 140-site campground at Eastman (Eastern Townships) around a pond, with 47 sites sold online and the rest seasonal; heated pool, splash pad, outdoor cinema. 2026: 2-service 30A C$58, 3-service C$64 a night in high season, tax extra (2 adults + 2 children); one-night stays at the nightly rate. Several 2-service sites cap at 24-28 ft.",
 'Camping Au Soleil St-Côme': "Camping au Soleil park at Saint-Côme (Lanaudière), 142 sites and mostly seasonal: the traveller section is about 17 sites (2- and 3-service, 30A and 50A pull-throughs) sold online one night at a time; pool, restaurant, river access. 2026 indicative rates 2-service C$65, 3-service C$65-75 + tax; a mid-October 2026 weeknight sold at C$60 (2-service) + C$5 booking fee. Season 1 May-31 Oct.",
 'Domaine Parc-Estrie - Parkbridge': "Parkbridge RV resort at Magog: about 490 RV sites, roughly 135 of them Voyageur (traveller) sites and the rest seasonal/annual; pool, splash pad, clay tennis, pickleball, restaurant, Route Verte bike path alongside. Online engine, Tuesday 13 Jul 2027: partial service (water/electric) 30A C$41, full service C$55, 50A C$70 a weeknight before tax (C$57-76 Fri-Sat).",
 'Camping Parc de la Chaudiere': "Camping Union network campground on the east bank of the Chaudière River at Scott (Beauce), 20 min from Quebec City; 178 sites, mostly seasonal, with a separate traveller section and separately priced riverside sites; pool, water slide. 2026: 2-service 30A C$55.50, 3-service C$63.50, riverside C$74 a night + tax. Online reservations need 2 nights; the same-day Nuitée Express (after 16:00, out by 09:00, 20% off) and walk-ins sell single nights. Season 15 May-12 Oct 2026.",
 "Camping de l'Estrie": "About 200-site campground at Shefford between Granby and Bromont, roughly 47 traveller sites (2- and 3-service, some 50A) and the rest seasonal; lakeside sites on a small pond, pool, splash pad, pump track, RV mechanics. 2027 before tax: 2-service C$57, 3-service C$65 (lakeside/50A C$72) in high season, and a July 2027 weeknight sells online at those prices; 3 nights on long weekends. Traveller season 30 Apr-11 Oct 2027.",
 'Camping des Chutes Hunter': "366-site campground at Frelighsburg, 5 km from the Vermont border, with at least 52 serviced traveller sites sold online one night at a time; pool, beach, restaurant, pickleball. 2026 traveller rates: 2-service C$46, 3-service 30A C$52, 50A C$56 a night (7th night free); official 2026 maximum C$58.95. Season 2 May-13 Oct 2026.",
 'Camping la Gervaisie': "About 118-site campground at Saint-Tite, mostly traveller (about 80 traveller sites, 24 seasonal, rental trailers), every site 3-service; heated pool, beach and boat rentals on Lac Trottier across the lane. 2026 traveller rate C$65.25 a night + tax. Reservations by phone only (from 1 April, 50% non-refundable deposit, balance by debit or cash); 2 nights on weekends, 3 on holidays and during the Festival Western in September.",
}

# One line per add: what was measured for the inclusion audit (rate source, traveller share).
SHARE = {
 'Camping Baie Du Diable': 'posted 2024 table matches the official 2026 maximum; phone booking; no off-season frame showing trailers on nearly every pad',
 'Camping Belle Montagne': '40 traveller RV sites free on a fall weeknight in the engine',
 'Camping St-Edouard': '2024 plan colours ~45 traveller 3-service sites, ~15 water/electric and 21 unserviced beside ~370 seasonal (re-counted 2026-10-09)',
 'Camping la Descente des Femmes': '26 three-service RV sites; official 2026 maximum C$45',
 'Camping la Detente': '2025 plan leaves large non-seasonal blocks (11-40, 1A-10B, 800s/900s, pond loops, most of 196-352)',
 'Camping Lac-Aux-Sables': '~75-80 traveller sites of ~300 on the 2024 plan; same-day single nights',
 'Camping Lac Frontiere (Border Lake)': '23 trailer + 9 two-service sites sold online of ~120',
 'Camping Lac et Foret': '30 Sep 2022 imagery: lakeside loop packed (seasonal), roadside section by the wave pool partly empty',
 'Camping Lac-des-Plaines': '~40-50 traveller sites of ~200',
 'Camping Domaine Du Lac Libby': '~90 traveller sites of ~350; weekday single-night policy unconfirmed',
 'Camping Plage des Sables': '~76 traveller sites of ~250',
 'Camping Du Parc': '22 Apr 2023 pre-opening orthophoto: pull-in Les Prés section nearly empty; single nights by phone 48 h ahead',
 'Camping St-Boniface': '22 Apr 2023 pre-opening orthophoto: stored trailers on many but clearly not nearly all pads; 4-star Camping Québec',
 'Camping Vallee Bleue Resort, Enr.199426': '~48 traveller sites of ~250 (~19%)',
 'Camping Causapscal Chez Moose': 'July rented by the day only; official 2026 maximum C$52',
 'Camping Sainte-Emilie': '61 sites free for a July 2027 night in the engine',
 "Le Domaine de l'Ange Gardien": '27 three-service 30A sites free for a July 2027 night in the engine',
 'Camping Soleil': '2022 map: ~75 traveller sites of ~305',
 'Camping Ecologique de Frelighsburg': '26 Apr 2024 pre-opening orthophoto: ~30-40 stored trailers of ~120 sites, riverside sites empty',
 'Camping des Etoiles': '43 sites free for a July 2027 night in the engine',
 'Camping la Rochelle': '75 three-service traveller sites free in the engine',
 'Camping la Pinede': '25 traveller sites beside 120 seasonal (~17%)',
 'Camping Horizon': 'plan legend colours ~35 traveller sites of ~220 (~16%)',
 'Camping Oasis': '~55 traveller sites of ~460 (~12%)',
 'Camping du Rivage': 'official 2026 maximum C$52.19 = the posted C$60 before tax',
 'Camping Beau-Soleil, Enr.200561': '14 Apr 2025 pre-opening imagery: pull-through traveller loops nearly empty',
 'Camping de la Demi-Lieue': '360+ sites incl. a seasonal section; Nuitée Express single nights',
 'Camping du Gouffre': '1 May 2023 pre-opening frame shows most pads empty',
 'Camping Domaine des Erables - Parkbridge': '~130 Voyageur sites of ~600 (~20%) on the resort map',
 'Camping Domaine Ensoleille': 'official 2026 maximum C$54.95 for any campsite',
 'Camping Sainte Madeleine, Enr.199662': '77 sites sold online of 282 (~27%)',
 'Camping 2 Rivieres': 'May 2020 closed-season frame: ~120-150 stored trailers on 200+ pads, the western loops mostly empty (re-viewed 2026-10-09)',
 'Camping la Mine de Cuivre': '47 sites sold online of ~140 (~33%)',
 'Camping Au Soleil St-Côme': '~17 traveller sites of 142 (~12%) free on a mid-October weeknight',
 'Domaine Parc-Estrie - Parkbridge': '~135 Voyageur cells of ~490 on the 2026 resort map (~28%)',
 'Camping Parc de la Chaudiere': 'May 2020 closed-season frame: separate block of ~30-45 empty pads of 178 (re-viewed 2026-10-09)',
 "Camping de l'Estrie": '~47 traveller sites of ~200 on the 2026 map (~24%)',
 'Camping des Chutes Hunter': '52 serviced traveller sites free for a July 2027 night of 366 (>=14%)',
 'Camping la Gervaisie': '~80 traveller sites of ~118 on the 2025 plan',
}

def main():
    out = []
    missing = [k for k in adds if k not in NOTES or k not in SHARE or k not in calls]
    if missing:
        sys.exit('missing note/share/call for: %s' % missing)
    for k, a in adds.items():
        c, v = calls[k], ver[k]
        base = v['base_rate']
        q = a['quality'].split(';')[0].strip()
        sites = '\n'.join(s for s in a['website'].split('\n') if s and not any(x in s for x in DROP_SITE))
        out.append({
            'name': a['display_name'],
            'location': c['pin'],
            'elevation_meters': ELEV_FIX.get(a['display_name'], c['elevation_meters']),
            'website': sites,
            'phone': a.get('phone', ''),
            'note': NOTES[k] + ' --Claude',
            'inclusion_evidence': '%s (C$%s, read 2026-10-08, no_rate follow-up); %s; %s with phone; C$%s ~ US$%d'
                                  % ('official Bonjour Québec 2026 maximum, operator site live'
                                     if v['rate_source'].startswith('Bonjour Quebec')
                                     else 'operator booking engine quote (Parkbridge RMS)'
                                     if 'rmscloud' in v['rate_source']
                                     else 'operator site live with nightly rates',
                                     base, SHARE[k], q, base, round(float(base) * 0.72)),
            'waterfront': c['waterfront'],
            'wf': c['wf'],
            'decision': 'add',
            'ownership': 'private',
            'worklist_name': k,
        })
    p = os.path.join(REPO, 'audit/qc_private/results_norate.json')
    json.dump(out, open(p, 'w'), ensure_ascii=False, indent=1)
    print('wrote', p, len(out))


def wf_results():
    # After append_state.py: map the appended entries (by name + state QC + id >= 15126) to
    # apply_waterfront_audit.py rows.
    cg = json.load(open(os.path.join(REPO, 'campgrounds.json')))
    res = json.load(open(os.path.join(REPO, 'audit/qc_private/results_norate.json')))
    byname = {}
    for e in cg:
        if e.get('state') == 'QC' and e['id'] >= 15126:
            byname[e['name']] = e
    rows = []
    for r in res:
        e = byname.get(r['name'])
        if not e:
            print('not appended:', r['name']); continue
        rows.append({'id': e['id'], 'name': e['name'], 'current': e.get('waterfront'),
                     'final': r['waterfront'], 'coord_fix': None, 'elevation_meters': None,
                     'evidence': r['wf'], 'confidence': 'high'})
    p = os.path.join(REPO, 'audit/qc_private/waterfront_norate_results.json')
    json.dump(rows, open(p, 'w'), ensure_ascii=False, indent=1)
    print('wrote', p, len(rows))


if __name__ == '__main__':
    wf_results() if '--wf' in sys.argv else main()
