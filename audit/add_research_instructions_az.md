# Campground add-stage research — agent instructions (ARIZONA)

You are researching candidate campgrounds for a personal RV-trip database and
returning ready-to-append records. Your batch file (path in your prompt) is a
JSON array of candidate objects from RV Life (fields: `cg_name`, `city`, `star`
[RV Life user rating 0–5; 0 = unrated], `price` [0–4 $ signs], `park_type`,
`rvlife_lat`/`rvlife_lng` [APPROXIMATE — often off by km], sometimes `former_name`,
`site_count`, `rating_count`).

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
  (**Havasupai / Havasu Falls is hike-in — SKIP**)
- group-only / youth-camp / scout / retreat only
- **equestrian-only horse camp** (a general campground that merely offers horse sites is OK)
- day-use only (no overnight camping); a trailhead or overlook with no campground
- fairground/event-lot that camps only during events
- membership/club/sales-pitch park (Thousand Trails, Encore, Coast-to-Coast, Bluegreen, etc.)
- residential / mobile-home / seasonal-full-timer / **55+ / age-restricted / long-term
  "resort"** park; **casino/racetrack overnight lot** (a real casino-adjacent RV *park*
  with defined transient sites + amenities may be borderline — vet as a transient RV
  park; a bare overnight parking lot is a SKIP)
- closed / defunct / no evidence it currently operates (dead site + thin reviews = strike)
- **largest drive-in sites cap under ~23 ft** at every site (tiny 16–20-ft forest sites)
- a **duplicate** of another candidate in THIS batch or a clearly different name for
  the same campground (keep one; name the other in `skip_reason`).

**Arizona is a huge, arid, federal-land state** — vast BLM desert (LTVAs + 14-day
areas around Quartzsite/Yuma), six National Forests, big NPS units (Grand Canyon,
Lake Powell/Glen Canyon, Lake Mead/Mohave), many tribal reservations, and an enormous
**snowbird / 55+ / long-term-residential RV-resort** belt (Phoenix metro—Mesa/Apache
Junction/Casa Grande, Tucson, **Yuma** [massive winter], **Quartzsite** [winter],
Lake Havasu City, Cottonwood/Verde Valley, Benson). **Vet the private bucket HARD for
genuinely-transient operation** — Yuma/Mesa/Apache-Junction/Casa-Grande are packed with
55+ and park-model residential "resorts" that still take a few overnighters; SKIP those.
Many BLM/USFS/NPS sites are on gravel/desert/forest roads — a decent maintained
gravel/dirt road is fine (drive-in); only skip for access if genuinely
4WD/high-clearance-required or all-tiny-tent-pads. **Aggregators (snoflo, camperalerts,
campscanner, thedyrt/camping.org summaries) inflate cabin/day-use parks into fake "RV
sites" — never confirm a keep from an aggregator alone.** Authority = the operator/agency
page + the reservation system's actual site list.

### Arizona-specific authorities & ownership
- **State parks (Arizona State Parks & Trails):** `azstateparks.com`; reservations run
  through their own portal (`azstateparks.com/reserve` / the park's page — NOT rec.gov).
  Big camping state parks: Lost Dutchman, Catalina, Picacho Peak, Kartchner Caverns,
  Patagonia Lake, Roper Lake, **Lyman Lake**, Dead Horse Ranch, Fool Hollow Lake,
  Homolovi, **Lake Havasu SP / Windsor Beach**, **Cattail Cove SP**, **Buckskin Mountain
  SP / River Island** (Colorado River), **Alamo Lake SP**, Tonto Natural Bridge (day-use —
  verify overnight), Oracle, Jerome/Red Rock (day-use). Set `ownership: "state"`.
- **BLM (FEDERAL) — this is what `park_type: dnr` USUALLY means in Arizona.** AZ has NO
  state DNR campgrounds (AZ State Land Dept = trust land, permits, not developed
  campgrounds). Big BLM camping: **Long-Term Visitor Areas (LTVAs)** — **La Posa** (4 units,
  Quartzsite), **Imperial Dam LTVA** (Yuma; incl. Coyote/Kripple Creek/Skunk Hollow/South
  Mesa) — seasonal (mid-Sep–mid-Apr) permit camping, developed with dump/water, drive-in RV
  → KEEP as `federal`, note the LTVA permit model (long-term-visitor permit is NOT the same
  as a residential/membership park — these are public BLM). BLM 14-day short-term areas
  around Quartzsite (Hi Jolly, Scaddan Wash, Dome Rock, Road Runner, La Posa short-term) and
  the Yuma area (Senator Wash, Squaw Lake [rec.gov-reservable], Mittry Lake) — keep the
  named/developed ones. Other BLM: Lake Havasu-area, Agua Fria, Gila Box RCA (Owl Creek/
  Riverview), Burro Creek, Virgin River. `blm.gov/visit/<slug>`; a few on recreation.gov,
  many FCFS/permit. Set `ownership: "federal"`. **VERIFY the operator per entry** — a
  `dnr`-tagged site that's actually AZ State Parks → `state`; county-run → `local`.
- **USFS (federal, `park_type: usfs`/`national`):** six forests —
  - **Coconino NF** (Flagstaff/Sedona: Oak Creek Canyon — Cave Springs, Pine Flat,
    Manzanita, Bootlegger; Lake Mary/Mormon Lake — Dairy Springs, Double Springs, Ashurst;
    Lakeview),
  - **Kaibab NF** (North: DeMotte, Jacob Lake; South: Ten X),
  - **Tonto NF** (huge — the Salt River lakes below Phoenix: Roosevelt [Cholla, Windy Hill],
    Apache Lake, Canyon Lake, Saguaro Lake; Payson/Mogollon Rim — Houston Mesa, Ponderosa,
    Christopher Creek, Sharp Creek; Pine),
  - **Apache-Sitgreaves NF** (White Mountains — Big Lake, Woods Canyon Lake, Willow Springs,
    Rim-area, Sunrise, Luna Lake near Alpine),
  - **Prescott NF** (Lynx Lake, Granite Basin, Yavapai, Mingus Mountain, Playground),
  - **Coronado NF** (Mt Lemmon — Rose Canyon, General Hitchcock; Madera Canyon — Bog
    Springs; Chiricahua — Rustler Park, Pinery/Idlewilde; Huachuca — Reef Townsite;
    Parker Canyon Lake — Lakeview).
  Most drive-in campgrounds are on recreation.gov (deep link → `/camping/campgrounds/<id>`);
  some FCFS. Set `ownership: "federal"`. **Watch the under-23-ft skip rate** — many small
  high-elevation Rim/White-Mountain/Sky-Island sites cap at 16–22 ft.
- **NPS (federal, `park_type: national`):** **Grand Canyon NP** (Mather, Desert View,
  Trailer Village [concessioner-run on NPS land → still `federal`]; North Rim id 275 already
  in DB — skip as dup); **Glen Canyon NRA / Lake Powell** (Wahweap, Lees Ferry;
  Bullfrog/Halls are UT); **Lake Mead NRA** (AZ side: **Temple Bar**, **Katherine Landing**
  on Lake Mohave); **Organ Pipe Cactus NM** (Twin Peaks); **Chiricahua NM** (Bonita Canyon);
  **Canyon de Chelly NM** (Cottonwood — jointly NPS/Navajo). Set `ownership: "federal"`.
  Saguaro NP & Petrified Forest have NO drive-in campground (wilderness/none) — SKIP.
- **Tribal (`ownership: "private"` per convention):** AZ is heavy with reservations —
  **Navajo Nation** (Monument Valley: Mitten View/The View; Antelope Point & Navajo-side
  Lake Powell; Cottonwood at Canyon de Chelly; Little Colorado), **White Mountain Apache /
  Fort Apache** (Hon-Dah, Sunrise, Hawley Lake, Horseshoe Cienega, many reservation lakes —
  tribal permit; keep genuine drive-in RV), **San Carlos Apache** (San Carlos Lake, Soda
  Canyon), **Hualapai** (Grand Canyon West), **Havasupai** (Havasu Falls — HIKE-IN, SKIP),
  **Salt River Pima-Maricopa** (We-Ko-Pa/casino), Ak-Chin, Gila River, Cocopah, Quechan
  (Yuma). Tribal camping is often permit-based dispersed/beach — keep only genuine drive-in
  RV camping; SKIP hike-in/boat-in. Set `ownership: "private"`.
- **Local:** **Maricopa County Regional Parks** are excellent and county-run → `local`:
  **Lake Pleasant, Usery Mountain, McDowell Mountain, Cave Creek, White Tank, Estrella**.
  **Pima County** (Gilbert Ray, Tucson Mtn). **Mohave County** (**Davis Camp** on the
  Colorado near Bullhead City/Laughlin; Windsor Beach). **La Paz County** (La Paz County Park
  & many Parker-strip Colorado-River county sites). **Yavapai, Cochise, Pinal, Yuma** county
  parks; **city** RV parks (Cottonwood, Show Low, Winslow, Benson, Wickenburg, etc.);
  fairgrounds that run a year-round public RV area (skip event-only lots). Confirm the
  operator is genuinely local government; county land run by a private concessionaire is
  still `local`. Set `ownership: "local"`.
- **Private (commercial):** already gated to affordable/well-rated ($/$$, ≥4★); still vet
  each HARD — real transient RV park, NOT 55+/age-restricted/membership/seasonal/residential/
  casino-lot. Yuma, Mesa/Apache Junction, Casa Grande, Tucson, Quartzsite, Lake Havasu City,
  Benson, Cottonwood have MANY 55+/park-model residential "resorts" — read reviews/site
  policy and SKIP the age-restricted/long-term ones. Keep genuine drive-in transient RV parks.

### Max-RV-length rule (AZ mountain/forest sites can be small)
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
  (newline-separated, deduped by domain). URLs go HERE, not in `note`.
- **`phone`** — the park/office/ranger-district number if on the official page; else "".
  Never fabricate.
- **`note`** — concise, every claim sourced. Include the camping basics you confirmed
  (loops/site count, hookup level, max RV length if notable, FCFS vs reservable) and
  append ` RV Life <star>*/<price as $ signs> (auto 7/2026). --Claude`. If FCFS with no
  booking channel, say "First-come, first-served." Do NOT copy aggregator boilerplate.
- **`inclusion_evidence`** — ONE line naming the authoritative source + what it showed,
  e.g. `recreation.gov Cholla CG (Tonto NF, Roosevelt Lake): 206 sites, RVs to 40 ft,
  reservable -> real RV campground`.
- **`waterfront`** — ALWAYS the literal placeholder `"not waterfront"` (a later audit
  decides; do NOT set it from name/marketing).
- **`lead`** — head start for that later waterfront audit (NOT a verdict):
  `{"map_url": "<official per-site campground map/PDF or rec.gov url>",
    "water_body": "<named lake/river/reservoir or ''>",
    "candidate_sites": "<site numbers you saw at/near the water, or ''>",
    "note": "<one-line shoreline observation from the map/satellite, or ''>"}`.
  ARIZONA is LANDLOCKED — no ocean, NO coastal dunes/woods (its lakes lack genuine
  shore-dune fields). The big waters: **Lake Powell** (Wahweap, Antelope Point, Lees Ferry),
  **Lake Mead & Lake Mohave** (Temple Bar, Katherine Landing — note DRAWDOWN: Mead/Mohave
  have receded far, so verify the site still sits on water), **Lake Havasu** (Windsor Beach,
  Cattail Cove, London Bridge), the **Colorado River** (Parker strip, Buckskin Mtn/River
  Island, Davis Camp, Imperial Dam/Squaw Lake — `riverfront`/`riverview`), **Lake Pleasant**,
  the **Salt River chain** (Roosevelt, Apache, Canyon, Saguaro lakes), **Lyman/Roper/
  Patagonia/Alamo/San Carlos** lakes, and the **White Mountain lakes** (Big Lake, Woods
  Canyon, Hawley, Sunrise). Flag the water body + any shoreline site observation so the audit
  can weigh it. Do NOT assign a coastal value.

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
