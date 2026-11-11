# p3-412 Minnesota notes (2026-11-11)

## Method
- MN DNR park pages are JS; the data is JSONP at https://maps.dnr.state.mn.us/cgi-bin/compass/feature_detail.cgi?callback=foo&id=spkNNNNN (tools/dnr.py + dnrshow.py): overnight_facilities, seasonal_update (electric sites, rvs, campgrounds open/close), alert, contact.
- ReserveMN (mnrdr.usedirect.com) search/details/<UnitId>/startdate/<d>/nights/1/0/0 gives per-site description, pad length, amps, 'Water Front' tag, rate (tools/units.py). Season from grid SeasonDates (tools/season.py, ~3-week windows).
- Overpass mirrors all down this session (private.coffee, kumi timeouts).

## 5377 Franz Jevne
- 18 units (15 back-in drive-in, 2 electric 30A; 3 walk-in); DNR 30-ft limit; 'Steep grades located after the picnic area limit RV and large 5th Wheel travel.' -> caveat.
- Site 2 only site tagged Water Front (.01 mi, up steep bank) -> riverview kept.
- Pin at entrance/1E; main loop ~48.6438,-94.0668 (imagery est.). Phone 218-888-7310 (Big Bog).

## 5632 Freeborn County Fairgrounds - done
County Non-Fair page: $40/day, $240/wk, $900/mo; W/E/S; dump; mid-Apr to mid-Oct; phone reservations 507-383-5192. Websites old->new flagged.

## 5380 Gooseberry Falls SP - done
69 drive-in (68 ReserveMN), no electric, 3 pull-through, 40 ft limit, $25. Year-round. Coastal walk upgrade flagged (loop 50-150 m from Lake Superior shore under canopy, Hwy 61 on far side of river). Pin north of Hwy 61 -> ~47.1394,-91.4608. Phone 218-595-7100.

## 5647 Green Lake County Park (Kandiyohi) - done
2026 policy PDF: 7+ night reservations Memorial-Labor Day, online only; $42+tax. DROP CANDIDATE (Nickerson pattern). Not waterfront kept. Same rule covers 5612/5646/5648/13329.
(booking.platform must be 'operator' for ResNexus - 'resnexus' failed apply.py schema; fixed.)

## 5475 Gull Lake USACE - done
rec.gov 233648: 39 public sites (3 HOST excluded), 50A, no W/S at sites, $32, 05-01..10-14. USACE mvp page 403 (unread). Phone stored 218-829-3334 unconfirmed; rec.gov (651) 290-5772. North entrance closed. Not waterfront.

## 5535 Gun Lake Family Campground (private) - done
22 pull-through full hookups, $35/$45, May 1-Oct 31, parkwith.us engine. Google 4.8/27. Five tests pass. Not waterfront (marsh).

## 5635 Harmony City Campground - done
FCFS payment box, $30 campers, dump. Phone add 507-886-8122. Hookups/season unstated.

## 5637 Hill City - done
City: $45 FHU / $35 W/E / $20 tent, monthly + May15-Sep15 seasonal. Dump OFF SITE at Sunny's ($10) -> dump false. Lakeview kept (east-end pads ~40-50 m from boat landing over the landing lot; site numbers unreadable: city Campsite Map.JPG = Cloudflare page; campspot_map.py IndexError). Sites 14 (city text) vs 19 RV on Campspot - not written.
Tool note: DRV_SOCK under this scratch path exceeds the AF_UNIX 108-char limit; run from the scratch dir with DRV_SOCK=./drv.sock.

## 5640 Holiday Campground Warren - done
Rates doc unchanged (2026-04-24). CampLife 1422: same description, 32 back-in online sites with 20/30/50A + water -> electric 50. City page body is now empty. Not waterfront.

## 14623 Hungry Jack Lodge (private) - done
$40/2 + $8 per extra person/pet, tax extra, prepaid non-refundable; phone-only. Memorial Day - mid-Oct. Google 4.7/376. No gateway (not needed). Not waterfront (wooded sites behind lodge/cabins).

## 5435 Hungryman Lake (Two Inlets SF) - done
DNR cmp00048: 14 sites 'on a pine covered rise above Hungry Man Lake'. Canopy hides every pad; stored lakeview evidence not reproducible -> DOWNGRADE to not waterfront flagged. Phone: DNR manager Itasca SP 218-699-7251 vs stored 218-266-2100. Pin ~150 m from DNR point.

## 5643 Island View, Mountain Lake - done
$35/$600 mo/$2,000 season, FCFS, May 1-Oct 1, full hookups, showers/flush/dump. 17 vs 18 sites on same page. Canonical URL cityofmountainlakemn.gov. Not waterfront.

## apply.py dry run: 12 results ready, 0 "!!" after the 5647 platform fix.
