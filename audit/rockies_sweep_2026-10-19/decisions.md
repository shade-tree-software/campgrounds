# Rockies mini sweep, 2026-10-19

Scope: Glacier NP, Waterton, Banff/Lake Louise, Jasper, 40 km around each town and entrance (`area.py`).
Sources: RV Life (every park_type) + Good Sam directory (`candidates.py`), OSM camp/caravan sites + RIDB (`osm_ridb.py`),
NPS API (`nps_glac.json`), Parks Canada / Alberta Parks pages, operator sites.

## Added (ids 15368-15393)
- MT private, Glacier gateway (price gate lifted), 15368-15388: Leaning Tree (Google listing + camper rate), Columbia Falls RV,
  Glacier Peaks, Mountain View, Whispering Pines, Beargrass, Timber Wolf, Mountain Meadow, Rocky Mountain Hi, Spruce Park
  (riverfront), Heart of Glacier, Red Eagle (Blackfeet Nation), Aspenwood (Google listing + camper rate), Casey's, West Glacier RV,
  Glacier View Golf, Glacier Campground, Moose Creek, Lake Five, North American, Whitefish RV.
- AB 15389-15393: Wilcox (Parks Canada), Wabasso (temporarily closed 2026), Crandell Mountain (temporarily closed since 2017),
  Switzer Halfway (4 sites), Exshaw Community Campground (local).

## Not added
- Already in the DB under another name: Pocahontas = Miette 8795; every other Banff/Jasper/Waterton/Glacier frontcountry campground present.
- NPS Glacier: Bowman Lake, Kintla Lake, Quartz Creek, Logging Creek, Cut Bank (RVs/trailers not permitted); Sprague Creek (21 ft max, no towed units).
- Parks Canada: Marble Canyon (15 ft max), Icefield (tents only), Lake Louise soft-sided, Lake Louise overflow (no longer run), Monarch (AWH drop 2026-10-16).
- Alberta: Pine Bay (group only), Rock Lake walk-in/equestrian loops (main campground already 8963), Dawson (equestrian), Preacher's Point (random camping),
  Waterfall Creek (could not confirm a campground), Celestine Lake (walk-in).
- Flathead NF / DNRC: Handkerchief Lake (3 hike-in tent sites), Riverside (one group site), Upper Stillwater Lake (tent sites, ~12 ft), Moose Lake
  (3 sites, 35 mi rough road, fit unconfirmed), Upper Whitefish Lake (DNRC, rough road, trailer fit unconfirmed), Elk/Fire Island (boat-in).
- Private, star gate: Johnson's of St. Mary (RV Life 3.5), Chewing Black Bones, Glacier Haven, Y Lazy R, Sears, Sleeping Wolf, Glacier Grizzly,
  Sundance (Coram), Stanton Creek, Glacier Pines, Three Bears, Greenwood, Lake Ashley Hideaway, Buffalo Calf, Canmore's Spring Creek / Rundle Mountain /
  Wapiti / Stoney Park, David Thompson Resort, Fort Heritage, Gateway RV Hinton; Spring Glen Park AB (unrated, 3 Google reviews).
- Private, other: Eastside Glacier (RV Life closed, Google 2.4); Glacier Elkhorn (domain parked for sale, unclaimed RoverPass, primitive tent/small-RV);
  Trappers Hill (20 ft trailer max); Sundance by Basecamp (fit unstated, access closed); Glacier Meadow RV Park (47 km, outside the gateway; hookup
  sites $65+ even at the Good Sam 10% off); Montana Basecamp, Bigfork Motor Coach, Edgewater (44-56 km, over the gate).
- Previously dropped by AWH, not re-added: Waterton Springs (closed 2017), Great Canadian Barn Dance (seasonal leases).

## For AWH
- Rising Sun 6235: NPS API says 21 ft max; RIDB 10363618 shows every site 17-21 ft. The entry's "10 sites to 25 ft" is wrong. Propose drop (no trip refs).
- KOAs in the gateway: West Glacier KOA (5*, 3.4 km), St. Mary / East Glacier KOA (4*, ~1 km), Whitefish/Kalispell North KOA (4*, 31 km).
  Brand skip vs gateway rule (Hinton/Jasper KOA 12804 is in).
- Crandell Mountain has been closed since 2017 with no date; added greyed-out per the add-with-caveat rule. Drop if you'd rather not carry it.
- Lake Five Resort advertises waterfront "Lake Sites"; satellite couldn't tie RV pads to the shore through the tree band, so it's recorded not waterfront.
