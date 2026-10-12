"""WV findings from the booking site's supplier tiles (June 2027 weeknight prices, 2026-10-12)."""
import os, json, re, sys
d = json.load(open(sys.argv[1])); wkend = json.load(open(sys.argv[2])); out_path = sys.argv[3]
CG = {'P,502,368': 'River Run', 'P,502,369': 'Cokeley', 'P,502,370': 'Riverside', 'P,502,371': 'Beaver Creek',
      'P,502,362': 'Mash Fork', 'P,502,361': 'Blue Jay'}
FULL = 'P,53,738'
# entry id -> (suppliers, campground filter or None, display name)
MAP = {50: (['11067625', '7989192'], 'River Run'), 869: (['11067625'], 'Cokeley'), 216: (['11068632'], None),
       260: (['11067676'], None), 262: (['11067533'], None), 487: (['11067291', '7975480'], None),
       488: (['11067522'], None), 489: (['7989176'], None), 490: (['11068656'], 'Riverside'),
       491: (['11068656'], 'Beaver Creek'), 599: (['11067324'], None), 630: (['11067509', '7988967'], None),
       715: (['11067308'], None), 816: (['11067283', '7975381'], None), 870: (['11067416'], 'Mash Fork'),
       871: (['11068527', '7989221'], None), 872: (['11068539', '7989230'], None),
       873: (['10976261', '11067609'], None), 874: (['11067474'], None), 875: (['14350566'], None),
       876: (['11067393', '7988855'], None), 878: (['7989212'], None), 983: (['11067553', '7989144'], None),
       984: (['11067485'], None), 985: (['11067593', '7989180'], None)}
rows = {e['id']: e for e in json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'campgrounds.json'), encoding='utf-8'))}
def units(sid, stay, cg):
    us = d[sid]['stays'].get(stay) or []
    if stay == 'weekend': us = wkend.get(sid) or []
    return [u for u in us if cg is None or any(CG.get(c) == cg for c in re.findall(r'P,\d+,\d+', u['att']))]
def money(x): return f"${x:.2f}".replace('.00', '')
def rng(ps): return money(min(ps)) + ("–" + money(max(ps)) if max(ps) != min(ps) else "")
out = []
for eid, (sids, cg) in MAP.items():
    ne, el, full = [], [], []
    for sid in sids:
        for u in units(sid, '2027-06-15:2027-06-16', cg):
            if 'Non-electric' in d[sid]['name']: ne.append(u['price'])
            else:
                (full if FULL in u['att'] or 'Full Hookup' in d[sid]['name'] else el).append(u['price'])
    elec = el + full
    fees = {"currency": "USD", "checked": "2026"}
    if ne:
        fees["nightly_low"], fees["nightly_high"] = min(ne), max(ne)
        s = {}
        if el: s["electric"] = round(min(el) - min(ne), 2)
        if full: s["full_hookup"] = round(min(full) - min(ne), 2)
        if s: fees["surcharges"] = s
    else:
        fees["nightly_low"], fees["nightly_high"] = min(elec), max(elec)
    parts = []
    if ne: parts.append(f"Non-electric sites {rng(ne)} a night")
    if el: parts.append(("electric " if ne else "Electric sites ") + rng(el))
    if full: parts.append(("full-hookup " if (ne or el) else "Full-hookup sites ") + rng(full))
    text = ", ".join(parts) + "."
    if not ne: text += " Every reservable RV site has electric."
    # weekend and season differences seen on the booking site, compared site by site
    wkd = {u['unit']: u['price'] for sid in sids for u in units(sid, '2027-06-15:2027-06-16', cg)}
    up = [(u['unit'], u['price']) for sid in sids for u in units(sid, 'weekend', cg) if u['price'] > wkd.get(u['unit'], 1e9)]
    wd = list(wkd.values())
    if up:
        kind = "Non-electric sites cost" if all('Non-electric' in u for u, _ in up) else "Sites cost"
        text += f" {kind} more on a Friday-Saturday stay: {rng([p for _, p in up])} a night averaged over the two nights."
    ap = [u['price'] for sid in sids for u in units(sid, '2027-04-20:2027-04-21', cg)]
    if ap and min(ap) < min(wd): text += f" April prices are lower ({rng(ap)})."
    if eid == 875:
        wk = [u["price"] for sid in sids for u in units(sid, "weekend", cg)]
        fees["nightly_low"], fees["nightly_high"] = min(ap + wd + wk), max(ap + wd + wk)
    sup = " + ".join(f"{d[s]['name']} (supplier {s})" for s in sids)
    text += (" WV State Parks booking site (book.wvstateparks.com) for June 2027 weeknights, read 2026-10-12.")
    fees["note"] = text
    fees = {k: fees[k] for k in ("nightly_low", "nightly_high", "currency", "reservation_fee", "nonresident",
                                 "surcharges", "checked", "note") if k in fees}
    out.append({"id": eid, "name": rows[eid]['name'], "fees": fees,
                "source": f"https://book.wvstateparks.com/ nightly prices for 2027-04-20, 2027-06-15 and a 2027-06-18/20 weekend"
                          f" (read 2026-10-12): {sup}" + (f", {cg} Campground sites" if cg else "")})
out.append({"id": 720, "name": rows[720]['name'], "fees": {
    "nightly_low": 70, "nightly_high": 76, "currency": "USD",
    "surcharges": {"weekend": 4, "premium_site": 6}, "checked": "2026",
    "note": ("Stonewall Resort's 2026 rates: every RV site has full hookups (30/50 A), $70 a night January 1 - May 24 "
             "and November - December, $72 on weeknights June 3 - October 31 and $76 on weekends then; premium "
             "lake-view sites $6 more; holiday weeks $80. Tax and a $2 park enhancement fee are added to every "
             "reservation. Booked by phone (304-269-8889) or at the entrance gate only. Read 2026-10-12.")},
    "source": "https://www.stonewallresort.com/roanoke-west-virginia-accommodations/campgrounds/ (2026 Rates, read 2026-10-12)"})
json.dump(out, open(out_path, 'w'), indent=1, ensure_ascii=False)
for f in out: print(f['id'], f['name'][:34], {k: v for k, v in f['fees'].items() if k != 'note'}, '|', f['fees']['note'][:170])
