# Alberta notes, p3-380 (learned this batch)

## Parks Canada reservation catalogue (reservation.pc.gc.ca)
- Plain curl answers 403 (Azure WAF). In the headless browser (bwnet.py, under the flock), open the
  RESULTS url, not the home page:
  `https://reservation.pc.gc.ca/create-booking/results?mapId=<map>&searchTabGroupId=0&bookingCategoryId=0&startDate=...&endDate=...&nights=1&isReserving=true&equipmentId=-32768&subEquipmentId=-32768&partySize=1&resourceLocationId=<id>`
  It fires /api/resourcelocation/resources (per-site equipment + attributes, ~2-4 MB - raise bwnet's
  body cap), /api/dateschedule (go-live dates) and /api/resourceLocation (gpsCoordinates).
- p3-380/pcsum.py PREFIX summarises the capture: per-site max length, service type, tent-only/walk-in.
- Ids: Protection Mountain resourceLocationId -2147483512, mapId -2147483065;
  Rampart Creek resourceLocationId -2147483639, mapId -2147483648.
- Every Banff Icefields/Lake Louise site's service type reads "Unserviced with on-site Fire Pit
  (Fire Permit Added)", and the camping page says "Reservations include fire permits where
  applicable" - contradicts the federal:parks-canada row's "fire permits are extra where sold"
  (bundled at booking, not optional). Cart total not quoted.
- Banff phones: no campground lines. Lake Louise VC 403-522-3833, Banff VC 403-762-1550,
  reservations 1-877-737-3783.

## Alberta Parks
- Red Lodge: the 2026 wastewater-repair advisory is gone from every page; the seasonal-closure
  advisory (Sep 21, 2026) is up. Shop: "Closed through Tue May 18 2027".
- Sir Winston Churchill: the shop shows NO "Closed through" for the campground - the park has
  year-round comfort cabins, so park and site pages read "Status: Open through Fri Apr 30 2027".
  Look for that line when grep finds no "Closed through". The shop's map point is the island's
  middle; Loops A-F are on Big Island's south shore (~54.8288,-111.9848). Phones: Information
  780-623-7189, Campground Booth 780-623-4144. Seniors line absent on both pages.
- The shop's "Near Water" tag is not the waterfront gate: SWC's four tagged sites are behind a
  dense tree belt.

## Private / local
- Campspot slugs and park ids: Penhold penholdrvpark 4792 (no 2027 types yet); Owl's Nest
  owlsnestcampground 1194; Rainbow Valley rainbow-valley-campground-edmonton-ab 5781;
  River's Edge RiversEdge 6037.
- min_stay entries take only nights/applies/waived_if (applies: always|weekend|holiday|summer);
  a "note" key fails apply.py - detail goes in booking.note.
- Poplar Escape: the stored pin and Google's both sit on the access lane/acreage; widen the
  imagery (~1 km) to find the loop before calling a pin OK.
- Spirit Creek (reddeergolf.com/rv-park): Google's phone is the golf tee-time line; the camp
  line is 403-314-9577. The 2026 season closed Oct 4 (not year-round).
- Esri export 500s at small extents (~120-140 m half-width) - retry at 200 m+.
