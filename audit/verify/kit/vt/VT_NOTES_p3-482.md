# p3-482 Vermont notes (2026-11-16)

## Sources / tools
- Park pages https://www.vtstateparks.com/parks/<slug> all 200 (ricker-pond, silver-lake, stillwater, wilgus, bomoseen, button-bay, elmore, gifford-woods, half-moon-pond). Fees page /fees: RV/Tent $20 resident, $38 non-resident, prime +$2.
- RA full site list without a browser: tools/ra.py <slug>-state-park <parkId> out (campgroundDetails + campsitePaging.do?startIdx=25.. with a cookie jar); tools/rah.py out.raw.html parses type/length/amenity tags (Near Water, Pull-Through).
- campsiteDetails.do?siteId=N gives 'Proximity to Water', 'Max Camping Unit Length' and a site photo at /webphotos/VT/pid<park>/sid<site>/0/540x360.jpg.
- Imagery: tools/satg.py lat lng hw out [label:lat,lng] (Esri with 50/100 m grid).
- RA "Closed through" gives 2027 opening: May 27 (most), Stillwater May 20, Wilgus May 13.

## Per entry
- 4079 Ricker Pond: 26 tent/RV (12 RV, 14 tent-only); 5 sites >20 ft. pond -> lakeview (T29/T31 behind shoreline trees). Pin ~610 m off (at VT232 junction) -> ~44.2446,-72.2462. Season 05-22/10-12.
- 675 Stillwater: 56 tent/RV (box) vs 59 (text); AWH lakefront kept; phone absent->802-584-3822; season manual, 2027 opens May 21.
- 4074 Silver Lake: not waterfront confirmed; 39 tent/RV; season 05-22/09-07.
- 4068 Wilgus: 15 tent/RV; riverview confirmed (steep bank, canopy); pin ~260 m -> 43.3912,-72.4046 (map-scaled); season 05-08/10-12 (2027 May 14).
- 4098 Barrewood: W/E $50 (at gate), W/E/S $55, PPA; Google 4.8/39; ~20 trailers leaf-off of 38 -> maybe half seasonal; keep.
- 4071 Bomoseen: 55 tent/RV; not waterfront kept (cove = lean-tos; T46-48/50 are 20 ft); pin ~290 m -> 43.6552,-73.2282; season 05-22/09-07.
- 4078 Button Bay: 53 tent/RV, max 35 (stored 31); lakeview confirmed (bluff); pin ~600 m -> 44.1818,-73.3576; season 05-22/10-12.
- 4093 Country Village: $50 at gate, military 20%; seasonal limited; Google 4.7/72; reservations page stale (2024); keep.
- 362 Elmore: 44 tent/RV, 23-45 ft; note wrong (replaced); not waterfront; pin ~270 m -> 44.5446,-72.5312; manual season closes 10-14 wrong (10-12); phone absent -> 802-888-2982.
- 4072 Gifford Woods: 22 tent/RV (16 RV), 8 take 28+; season 05-22/10-18; not waterfront; pin OK (~215 m); website fpr -> /parks/gifford-woods.
- 4073 Half Moon Pond: pond KEPT (T14,T17,T25-T29 open grass at water, 25-34 ft); pin ~585 m -> 43.6943,-73.2196; 52 tent/RV; fcfs removed; website -> /parks/half-moon-pond.
