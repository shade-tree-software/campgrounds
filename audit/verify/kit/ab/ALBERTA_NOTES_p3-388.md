# Alberta notes, p3-388 (2026-11-11)

## Sources and access
- albertaparks.ca camping pages: plain curl works. pg.py (this folder) summarises body, ADV, DEST (directions point), PDFs and TEL.
- shop.albertaparks.ca: ralist.py SLUG PARKID OUT.json; dl/shop_<pid>.html holds "Closed through ..." / "Open year round".
- stettler.net and tofieldalberta.ca: 403 to curl, open in bw.py (under flock).
- villageofcarbon.com: 418 to curl, ERR_HTTP_RESPONSE_CODE_FAILURE in the browser, Wayback refused this client ("suspected abusive bot traffic"). UNREAD again (p3-375 too).
- Let's Camp API needs header `X-Tenant-Type: camp`; without it: {"error":"Invalid tenant type"}. ../p3-377/lcsum.py summarises /sites.
- Checkfront (hoodooresort.com): `https://<sub>.checkfront.com/api/3.0/item?start_date=...&end_date=...` answers plain curl with items + rates.
- Pincher Creek books through PerfectMind (townofpinchercreek.perfectmind.com), member sign-in; rates on the town page.
- gmt.py (this folder): Google Maps place + reviews dump; one call per lock.
- Esri export answers 500 intermittently; sat2.sh retries, a sleep helps.

## Findings worth keeping
- St. Mary Reservoir shop park 330314 also holds "Wally's" campground (32 reservable + 20 FCFS unserviced, 52-65 ft): NOT in the DB.
- St. Mary Upper pin was in the reservoir; agency point 49.361528,-113.122797.
- Sulphur Gates Hikers Canyon: agency says "11 unserviced campsites suitable for tents" (spurs round a gravel lot); fee now $25.
- Wabamun Lake: tear sheet maps Main Campground (Aspen, Deer) and West End Campground (Birch, Dogwood, Pine, Spruce, Willow) ~1.5 km apart, same entrance; agency directions point is the West End. Shop: Closed through May 13 2027.
- Tillebrook shop max 85 ft, 44 pull-throughs; Closed through Apr 30 2027.
- Taber RV Park: taberrv.com NXDOMAIN; Google 2.8 / 5 reviews at 50 Barton Dr; RV Life record last updated 2018.
- Hoodoo: ~45% of RV sites nightly (site map legend); Checkfront base C$30 no-hookup RV.
- Three Hills: winter power-only camping (Let's Camp open Oct 13 - Apr 30); Let's Camp phone 403-443-1123.
