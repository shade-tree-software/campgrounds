# Campground add-stage research — agent instructions (CALIFORNIA)

You are researching candidate campgrounds for a personal RV-trip database and
returning ready-to-append records. Your batch file (path in your prompt) is a
JSON array of candidate objects from RV Life (fields: `cg_name`, `city`, `star`
[RV Life user rating 0–5; 0 = unrated], `price` [0–4 $ signs], `park_type`,
`rvlife_lat`/`rvlife_lng` [APPROXIMATE — often off by km], sometimes `former_name`,
`site_count`, `rating_count`, `url`).

The RV ("EKKO") is 23 ft. Decide keep/skip per the inclusion criteria, then for
each KEEP produce a full record. Load `WebFetch` + `WebSearch` via ToolSearch
(`select:WebFetch,WebSearch`) and use them freely. Satellite look (curl GET works):
`curl -s "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=<lng-d>,<lat-d>,<lng+d>,<lat+d>&bboxSR=4326&size=1000,1000&format=jpg&f=image" -o /tmp/r_<id>.jpg`
with d=0.0035, then **Read** the jpg. Keep size ≤ 1000,1000.

## Inclusion criteria (SKIP if it fails)
KEEP only a real, currently-operating, **drive-in RV campground usable by a 23-ft
rig** (at least some drive-in sites fit 23 ft; reachable by a normal vehicle —
decent dirt/gravel OK, hardcore 4WD-only disqualifies; hookups NOT required,
grass/gravel/paved pad fine). SKIP (and say why in `skip_reason`) if it is actually:
- cabins-only / yurt-only; tent-only or all walk-in/cart-in/hike-in/boat-in/paddle-in
  (**many CA coastal & Sierra sites are hike-in/boat-in — e.g. environmental sites,
  most of Point Reyes, Channel Islands NP [boat-in] — SKIP those**)
- group-only / youth-camp / scout / retreat only
- **equestrian-only horse camp** (a general campground that merely offers horse sites is OK)
- day-use only (no overnight camping); a trailhead or overlook with no campground
- fairground/event-lot that camps only during events (a fairground running a
  year-round public RV area is OK — verify)
- membership/club/sales-pitch park (Thousand Trails, Encore, Coast-to-Coast, Bluegreen,
  Ocean Canyon, K/M Resorts, etc.)
- residential / mobile-home / seasonal-full-timer / **55+ / age-restricted / long-term
  "resort"** park; **casino/racetrack overnight lot** (a real casino-adjacent RV *park*
  with defined transient sites + amenities may be borderline — vet as a transient RV
  park; a bare overnight parking lot is a SKIP)
- **military FamCamp / DoD-ID-only** park (already excluded from your batch, but if one
  slips in and is affiliation-gated → SKIP — not publicly bookable)
- closed / defunct / no evidence it currently operates (dead site + thin reviews = strike)
- **largest drive-in sites cap under ~23 ft** at every site (tiny 16–20-ft forest sites)
- a **duplicate** of another candidate in THIS batch or a clearly different name for
  the same campground (keep one; name the other in `skip_reason`).

**California is enormous and spans every setting** — the Pacific coast (state beaches,
NPS seashores), the Sierra Nevada (18 national forests, Yosemite/Sequoia/Kings Canyon),
the northern redwoods, the Mojave/Colorado deserts (Death Valley, Joshua Tree, huge BLM),
the Central Valley & foothill reservoirs, and a MASSIVE private-RV-park industry with a
heavy **55+/snowbird/residential** belt (Coachella Valley/Palm Springs/Desert Hot
Springs, the desert around the Salton Sea, Yuma-adjacent, the Central Valley, and many
coastal "resorts"). **Vet the private bucket HARD for genuinely-transient operation.**
Many BLM/USFS/NPS sites are on gravel/desert/forest roads — a decent maintained
gravel/dirt road is fine (drive-in); only skip for access if genuinely
4WD/high-clearance-required or all-tiny-tent-pads. **Aggregators (snoflo, camperalerts,
campscanner, thedyrt/camping.org summaries) inflate cabin/day-use parks into fake "RV
sites" — never confirm a keep from an aggregator alone.** Authority = the operator/agency
page + the reservation system's actual site list.

### California-specific authorities & ownership
- **State parks (California State Parks / CA State Beaches / SRAs / VRAs):**
  `parks.ca.gov`; reservations run through **ReserveCalifornia** (`reservecalifornia.com`),
  a US-eDirect portal (deep link `https://www.reservecalifornia.com/Web/#!park/<PlaceId>`
  when you can find the PlaceId in the park's ReserveCalifornia URL — else just the
  official `parks.ca.gov/?page_id=<n>` page + `reservecalifornia.com`). CA has ~280 state
  park units; camping ones include the coastal state beaches (**Pismo/Oceano Dunes SVRA,
  Morro Bay, Montaña de Oro, Carpinteria, Refugio/El Capitán, Doheny, San Elijo, South
  Carlsbad, Sunset, New Brighton, Half Moon Bay, Sonoma Coast/Bodega, MacKerricher,
  Manchester, Gaviota**), redwoods (**Humboldt Redwoods, Del Norte Coast, Prairie Creek
  [jointly with NPS Redwood], Big Basin, Portola, Samuel P. Taylor**), Sierra/foothill
  (**Plumas-Eureka, Emerald Bay/D.L. Bliss at Tahoe, Calaveras Big Trees, Grover Hot
  Springs, Brannan Island**), reservoir **SRAs** (**Auburn, Folsom Lake, Lake Oroville,
  San Luis, Millerton Lake, Silverwood Lake, Lake Perris, Castaic Lake [local-run — verify],
  Salton Sea SRA, Picacho SRA**), and desert (**Anza-Borrego, Red Rock Canyon, Providence
  Mtns/Mitchell Caverns, Saddleback Butte**). **SVRA = State Vehicular Recreation Area**
  (Oceano Dunes, Hollister Hills, Ocotillo Wells, Prairie City) — these DO have drive-in
  RV/self-contained camping → keep. Set `ownership: "state"`. **Off-Highway (OHV) permits
  ≠ campground** — verify a real campground exists.
- **BLM (FEDERAL) — this is what `park_type: dnr` USUALLY means in California.** CA has NO
  state DNR campgrounds. Big BLM camping: the **desert** (Imperial Sand Dunes/Glamis area
  incl. **Gecko Rd, Roadrunner**; **Imperial Dam LTVA** + short-term areas — Coon Hollow,
  Wiley's Well, Midland, Hot Spring LTVA near Winterhaven/Blythe; **Ocotillo Wells-area,
  Corn Springs, Sawtooth Canyon**), the **King Range NCA / Lost Coast** (Mattole, Tolkan,
  Horse Mtn, Wailaki, Nadelos), **Fort Ord, Cache Creek, Cow Mountain, Bizz Johnson,
  Fossil Falls, Chimney/Long Valley (near Kennedy Meadows), Red Rock-area, Alabama Hills**
  (dispersed — keep genuine drive-in). LTVAs are seasonal permit camping, developed
  (dump/water), drive-in RV → KEEP as `federal`, note the LTVA permit model (NOT a
  residential/membership park — public BLM). `blm.gov/visit/<slug>`; some on recreation.gov,
  many FCFS/permit. Set `ownership: "federal"`. **VERIFY the operator per entry.**
- **USFS (federal, `park_type: usfs`/`national`):** California has **18 national forests** —
  the biggest federal bucket. Major ones with heavy camping: **Inyo** (Eastern Sierra:
  Bishop Creek, Big Pine Creek, June Lake, Mammoth/Reds Meadow, Lone Pine, Tuttle Creek
  [BLM], Convict Lake), **Sierra** (Huntington/Shaver/Bass Lake, Dinkey Creek), **Sequoia**
  (Kern River, Hume Lake), **Stanislaus** (Pinecrest, Cherry Lake, Highway 108), **Eldorado**
  (Crystal Basin/Union Valley/Ice House, Silver Lake), **Tahoe** (Truckee, Sierra City,
  Bowman), **Lake Tahoe Basin Mgmt Unit** (Fallen Leaf, Nevada Beach [NV]), **Plumas**
  (Bucks Lake, Lakes Basin), **Lassen NF** (Eagle Lake, Silver Lake), **Shasta-Trinity**
  (huge — Shasta Lake, Trinity Lake, McCloud, Trinity Alps), **Klamath, Six Rivers,
  Modoc, Mendocino, Los Padres** (Big Sur — Kirk Creek id 277 already in DB, Ponderosa,
  Nacimiento; Mt Pinos/Campo Alto), **Angeles** (Big Pines, Chilao, near LA), **San
  Bernardino** (Big Bear/Serrano, Barton Flats, San Gorgonio), **Cleveland** (Laguna,
  Palomar — Observatory). Most drive-in campgrounds are on recreation.gov (deep link →
  `/camping/campgrounds/<id>`); some FCFS. Set `ownership: "federal"`. **Watch the
  under-23-ft skip rate** — many small high-Sierra sites cap at 16–22 ft.
- **NPS (federal, `park_type: national`):** **Yosemite** (Upper/Lower Pines, North Pines,
  Wawona, Hodgdon Meadow, Crane Flat, Tuolumne Meadows id 279 already in DB, White Wolf,
  Bridalveil Creek), **Sequoia & Kings Canyon** (Lodgepole, Dorst Creek, Potwisha, Azalea,
  Sunset, Sentinel, Moraine, Sheep Creek), **Death Valley** (Furnace Creek, Sunset,
  Stovepipe Wells, Texas Spring, Mesquite Spring, Wildrose, Emigrant), **Joshua Tree**
  (Jumbo Rocks id 295 already in DB, Cottonwood, Black Rock, Indian Cove, Belle, White
  Tank, Ryan, Hidden Valley), **Lassen Volcanic** (Manzanita Lake, Summit Lake, Butte
  Lake, Southwest, Warner Valley), **Redwood NP&SP** (jointly w/ CA state parks — credit
  the actual operator per campground), **Whiskeytown NRA** (Oak Bottom, Brandy Creek),
  **Pinnacles NP** (Pinnacles CG), **Lava Beds NM** (Indian Well), **Point Reyes NS**
  (all hike-in/boat-in — SKIP), **Channel Islands NP** (boat-in — SKIP), **Devils Postpile
  NM** (Reds Meadow — USFS-run), **Golden Gate NRA** (Kirby Cove group / Bicentennial —
  verify). Set `ownership: "federal"`.
- **USACE (federal, `park_type: coe`):** CA reservoirs with Corps campgrounds —
  **Lake Sonoma** (Liberty Glen), **Lake Mendocino** (Kyen, Bu-Shay, Chekaka),
  **Black Butte Lake** (Buckhorn, Orland Buttes), **Hensley Lake** (Hidden View),
  **Eastman Lake** (Codorniz), **New Hogan Lake** (Acorn, Oak Knoll), **Pine Flat Lake**
  (Island Park, Trimmer). Many CA reservoirs have a Corps/Reclamation dam but state- or
  local-run campgrounds — credit the ACTUAL operator, not the dam owner. Set
  `ownership: "federal"` only for Corps-operated.
- **Reclamation / other federal:** some via `national`/`coe` tags. Verify operator.
- **Local (`park_type: county`/`city`/`regional`, plus gov-name rescues):** California
  has EXTENSIVE county/regional camping — **San Diego County** (many: Dos Picos, William
  Heise, Agua Caliente, Vallecito, Guajome, Lake Morena, Sweetwater, Potrero), **Santa
  Barbara County** (Cachuma Lake, Jalama Beach), **Ventura County** (Foster, Steckel,
  Kenney Grove), **Monterey County** (Lake San Antonio, Nacimiento), **Sonoma County**
  (Doran, Bodega Dunes-area, Spring Lake, Sonoma Coast), **Marin** (Samuel P. Taylor is
  state), **San Mateo, Santa Clara County** (Coyote Lake, Mt Madonna, Sanborn, Uvas,
  Joseph Grant), **East Bay Regional Park District** (Del Valle, Anthony Chabot),
  **Sacramento-area, Humboldt County, Lake County, Kern County** (Lake Ming), **regional
  water/utility districts** — **EBMUD, PG&E** (Sierra reservoirs: many Bucks/Rock Creek/
  Bear River/Pit River recreation lands → utility-run = **private** per convention, verify),
  **SMUD** (Loon Lake area), **Merced/Modesto/Turlock ID** (Don Pedro, McClure — irrigation
  district = local), **Kern County, LA County** (Castaic, Bonelli/Puddingstone,
  Saddleback), **city** RV parks. Confirm the operator is genuinely local government;
  county land run by a private concessionaire is still `local`; a utility-run campground
  (**PG&E, SCE**) is `private`; an **irrigation/water district** (public agency) is `local`.
  RV Life mis-tags some county/authority parks as commercial — a gov-name scan already
  rescued obvious ones into your local batch. Set `ownership: "local"`.
- **Tribal (`ownership: "private"` per convention):** CA has many rancherias/reservations
  with casinos & a few RV parks — keep genuine drive-in transient RV parks, SKIP bare
  casino overnight lots and membership. Set `ownership: "private"`.
- **Private (commercial):** already gated to affordable/well-rated ($/$$, ≥4★); still vet
  each HARD — real transient RV park, NOT 55+/age-restricted/membership/seasonal/residential/
  casino-lot. **Coachella Valley (Palm Springs, Desert Hot Springs, Indio, Cathedral City),
  the Salton Sea shore, the Central Valley, and many coastal "resorts" are packed with
  55+/park-model residential parks** that still take a few overnighters — read reviews/site
  policy and SKIP the age-restricted/long-term ones. **PG&E and SCE (utility) recreation
  campgrounds → `private`.** Keep genuine drive-in transient RV parks.

### Max-RV-length rule (CA mountain/forest sites can be small)
If the reservation system / agency page gives a max vehicle/RV length and it is **≤21 ft
at every site**, SKIP (note the cap in `skip_reason`). 22 ft is a borderline keep. If
firsthand reviews clearly show 28–30-ft rigs fitting despite a low listed max, you may keep
(say so in `inclusion_evidence`). If no length is published, judge from satellite/photos —
if the pull-ins visibly fit a 23-ft rig, keep.

## For each KEEP, produce the record
- **`location`** — pin to the actual CAMPGROUND LOOP (where the pads are), 5 decimals,
  NOT the park office/entrance/trailhead. Verify on satellite + the agency campground-map/PDF
  or recreation.gov photos. RV Life coords are often off by km; move onto the loop.
- **`elevation_meters`** — `https://api.open-meteo.com/v1/elevation?latitude=<lat>&longitude=<lng>`
  at your final pinned coord (number, not string).
- **`ownership`** — per the authorities above (federal / state / local / private).
- **`website`** — official park/forest page first, then the deep reservation link
  (recreation.gov `/camping/campgrounds/<id>` or reservecalifornia.com `#!park/<PlaceId>`;
  newline-separated, deduped by domain). URLs go HERE, not in `note`.
- **`phone`** — the park/office/ranger-district number if on the official page; else "".
  Never fabricate.
- **`note`** — concise, every claim sourced. Include the camping basics you confirmed
  (loops/site count, hookup level, max RV length if notable, FCFS vs reservable) and
  append ` RV Life <star>*/<price as $ signs> (auto 7/2026). --Claude`. If FCFS with no
  booking channel, say "First-come, first-served." Do NOT copy aggregator boilerplate.
- **`inclusion_evidence`** — ONE line naming the authoritative source + what it showed,
  e.g. `recreation.gov Lodgepole CG (Sequoia NP): 200+ sites, RVs to 40 ft, reservable
  -> real RV campground`.
- **`waterfront`** — ALWAYS the literal placeholder `"not waterfront"` (a later audit
  decides; do NOT set it from name/marketing).
- **`lead`** — head start for that later waterfront audit (NOT a verdict):
  `{"map_url": "<official per-site campground map/PDF or rec.gov url>",
    "water_body": "<named lake/river/reservoir/ocean or ''>",
    "candidate_sites": "<site numbers you saw at/near the water, or ''>",
    "note": "<one-line shoreline observation from the map/satellite, or ''>"}`.
  **California HAS a Pacific coast — coastal `coastal dunes` / `coastal woods` ARE in play**
  for the coastal state beaches & seashores (Oceano/Pismo Dunes, MacKerricher, Sonoma Coast/
  Bodega Dunes, Manchester, Gaviota, Sunset/Sonoma, Morro Strand, South Carlsbad, etc.) —
  flag the ocean + any dune-field/shore-forest backing so the audit can weigh it (do NOT
  set the value yourself). Big inland waters: **Shasta, Trinity, Oroville, Folsom, Tahoe,
  Berryessa, San Luis, Millerton, Pine Flat, Don Pedro, McClure, Nacimiento, San Antonio,
  Isabella, Perris, Castaic, Salton Sea, the Colorado River (Needles/Blythe/Winterhaven),
  Eagle Lake, Mono Lake**, and countless Sierra lakes/rivers (Kern, American, Merced,
  Feather, Owens, Truckee). Many reservoirs have **major drawdown** — measure to the
  beach/high-water edge but note if the pad sits atop a big drawdown bench. Flag the water
  body + any shoreline site observation.

## Output
Do NOT edit any repo files. Final message = ONLY a JSON array (no prose, no fences),
one object per candidate, SAME order as the batch:
```
{"decision":"add"|"skip","skip_reason":"<if skip>","name":"...","location":"lat,lng",
 "elevation_meters":<num>,"ownership":"federal","website":"...","phone":"...","note":"...",
 "inclusion_evidence":"...","waterfront":"not waterfront",
 "lead":{"map_url":"...","water_body":"...","candidate_sites":"...","note":"..."}}
```
For `skip`, only `decision`, `skip_reason`, and `name` are required. Be thorough but
return strictly valid JSON.
