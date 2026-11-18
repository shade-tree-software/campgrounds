# SK notes p3-520 (2026-11-18)
- Sask Parks: plain curl + cookie jar works on campgroundDetails.do; paging = campsitePaging.do?contractCode=SKPP&parkId=N&startIdx=10,20...; per-site campsiteDetails.do gives Type, Site Access (Pull-Thru/Back-In/Roadside/Walk-In), Electricity Hookup (Amps) "15/30", Site Length, Max Equipment Length, Allowed Equipment, GIS lat/lng. No "Proximity to Water" field in SKPP. Script: sk_sites.py SLUG PARKID OUT.json; summary sksum.py OUT.json [loop regex].
- The 2026-10-12 catalog audit/state_park_fees/sk_sites_2026-10-12.json is TRUNCATED (Crooked Lake 40 of 99 sites): re-read live.
- Parks Canada PANP: visit/heures-hours lists each campground's operating season ("Beaver Glen Open from mid-May to mid-October"); fees page visit/tarifs-fees.
- Run result scripts with plain python3 (not -I) so `from w import w` resolves.

## 9169 Crooked Lake - DONE
- live SKPP 99 sites; shore sites 42-51 (nightly roadside) 12-20 m from bank behind shrub band -> lakeview kept (flagged close)
- season guide PDF: sask-parks-camping-season-guide.pdf; listings.csv has Fall/Winter availability per park (Not Available in Fall/Winter strings)
- Esri export 500s at small hw: use satzp.py (z18 tiles + points) instead

## 9296 D-n-R's - DONE (drop candidate: FB only, no rate, workforce pitch; Google 4.4/11; phone 306-209-2253)
## 9223 Don Forsyth - DONE (village page: 8 elec + 18 non-elec, $40, booking call 306-631-6745; pin unconfirmed)
## 12817 Indian Head - DONE (2027 rates 62/65/55, GS 10%, RMS booking, Google 4.7/322, closes Oct 5)
- sk_sites.py background was crawling (~25 s/site on a stale cookie); sk_sites2.py uses per-run cookie + site-name filter (^S for Sandy Bay)

## 9166 Candle Lake Sandy Bay (done)
- SKPP parkId 290405 covers Minowukaw (M) + Sandy Bay (S). Sandy Bay: 143 sites + group; 123 electric (97 nightly, 26 seasonal), 20 non-elec (18 nightly). Max 50 ft.
- PIN 5.8 km off: stored 53.7561,-105.2852 is a marina/trailer park on the causeway. Target 53.7999,-105.3340.
- Lakeview kept close: S406-S409 (non-elec nightly) ~70-80 m across grass + beach road + day-use/boat-trailer lot. Stored evidence described the pin's place.
- sk_sites2.py background log missed 61 sites (names None); sk_ids.py (fresh cookie, detail per id) works. Douglas/Echo logs from sk_sites2 had NO details -> killed, re-run with sk_ids.py/sk_list.py (bpxwhn7cc).

## 9174 Douglas (done)
- 143 nightly electric (31 Homestead 15/30/50 -> electric 50), 4 hike-in, max 50, site 104 only <23. Oct camping (electric, pit toilets, by phone) -> closes 10-31 flagged. Not waterfront (349/350 ~150 m behind woods/dune). Pin fine. Phone matches.
## 9177 Good Spirit (done)
- Aspen 85 / Balsam 65 / Sandy Ridge 45 non-elec / 2 hike-in = 197; 29 seasonal (4 FS). 9 Aspen 50 A. Winter Aspen Nov 1 - Mar 14 -> wrap season 05-14..03-14. Sandy Ridge 660 m from Balsam: not a split. Not waterfront (B104/B121 ~150-170 m behind forest + marsh). Phone '' -> 1-306-792-4750.
- sk_ids.py is ~2 s/site.

## 9178 Great Blue Heron - Murray Point (done)
- sk_table.py (paging tables, div.td parser) -> sp/gbhT.json; details for 23 key sites -> sp/gbhW.log.
- Murray Point 134 nightly electric (M1-M29 50 A), Heron's Hideaway 18 + Coot's Corner 6 non-electric; North Murray Point 30 seasonal + 3 nightly (~0.9 km NW, not a split).
- M124-M136 ~60-70 m from beach behind conifer band: not waterfront kept. Pin fine. Phone '' -> 1-306-982-6250.

## 9176 Echo Valley (done)
- sp/echoT.json + sp/echoW.log. 381 sites: 250 nightly electric (Morningview 14 full service W/S/50 A), 71 non-electric, 60 seasonal (Valleyview).
- Lakeview B 401-415 behind road + private cottages: not waterfront. Chain of loops each <0.5 km apart: no split. Pin in Aspen fine. Phone '' -> 1-306-332-3215.

## Dry run: all 11 ready, no "!!" (2026-11-18). No headless browser used.
