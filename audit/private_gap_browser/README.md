# Private-gap browser helpers

Headless-Chrome helpers used to read booking engines the plain `curl` path can't
(ResNexus, Open Campground, Campspot availability, Newbook, Wix/script sites).
CampLife still 403s.

Setup (per machine; not a repo dependency):

    pip install --target ~/.cache/ekko-pw playwright
    python3 -m playwright install chromium   # or edit executable_path to a local Chrome
    export PYTHONPATH=~/.cache/ekko-pw

The scripts launch `/usr/bin/google-chrome` when it exists, else Playwright's
bundled Chromium as `channel='chromium'` (the full browser in new-headless mode).
The default headless *shell* loads Google Maps tiles but never fills the place
panel, so `gm.py` came back empty under it. On a container that ships Chromium
(e.g. `/opt/pw-browsers/chromium-1194`), pin the matching package instead of
downloading a browser: `pip install playwright==1.56.0`.

- `txt.py URL [--browser] [-l] [-nCHARS] [-wMS]` - page as text (+ links)
- `cs.py SLUG CHECKIN CHECKOUT` - Campspot park page with live per-site prices
- `newbook.py URL` - Newbook engine quote for a 23-ft trailer
- `sat.py LAT LNG HALF_WIDTH_M OUT.jpg` - Esri satellite crop with a crosshair
- `satz.py LAT LNG ZOOM OUT.jpg` - same from 3x3 stitched tiles (use when the export endpoint 500s; z17 ~ 600 m frame)
- `geo.py "ADDRESS"` - Census geocoder
- `gm.py "name town ST" ...` - Google Maps place: coords, phone, website, rating + review count
  (the quality signal for parks RV Life doesn't rate; a lodging-style panel hides the count)
- `gsr.py ST "name" ...` - Good Sam ratings by name (Algolia; the fetch cache has no ratings)
- `v.py <state>_private '<json>'` - append a verdict to audit/<state>_private/verdicts.jsonl
- `curlrates.py LIST` - plain-urllib rate crawl over a `name<TAB>url` list (no browser; reads ~2/3 of operator rates; run several splits in parallel)
- `bq.py LIST OUTDIR` - ONE rendered browser, sequential: each `name<TAB>url` page + up to 3 rate/booking links saved as text (~1 min/park; fixed 7 s / 5 s settle waits; reads `body` text only, so iframe widgets come back empty)
- `csl.py SLUG CHECKIN CHECKOUT` - Campspot park page sorted by price ascending (cheapest site type first; watch for tent/dry-camp rows)
- `rates.py URL` - crawl an operator site for rates: follows rate/booking links, prints every `$` line with context and the booking ENGINE / rate-PDF links (run in parallel over a "name url" list)
- `../private_gap_holds.py` - regenerate `audit/private_gap_holds.md`, the checklist of every candidate still on hold


## Interactive driver and booking-engine recipes (added 2026-10-08, Canada no_rate follow-up)

The one-shot helpers above relaunch a browser per call and can't work a date picker. These
drive ONE persistent Chromium step by step, so a booking engine can be worked like a person
would (open it, fill dates, click through, read the quote) across many shell calls. Still
one browser only ([[feedback-limit-headless-browsers]]).

    PYTHONPATH=~/.cache/ekko-pw nohup python3 -u audit/private_gap_browser/drv_server.py > ~/.cache/ekko-drv.log 2>&1 &
    python3 audit/private_gap_browser/drv.py goto url=https://example.com wait=6000
    python3 audit/private_gap_browser/drv.py quit          # when done

The socket is `~/.cache/ekko-drv.sock` (override with `DRV_SOCK`). Context: en-CA, America/Toronto,
1400x1000, `webdriver` flag hidden; dialogs auto-accepted and logged (`dialogs`).

- `drv.py <cmd> key=value ...` - the client. Commands: `goto url= [wait=ms]`, `url`,
  `text [sel=] [frame=] [grep=regex] [ctx=n] [max=] [off=]` (innerText - VISIBLE text only),
  `html sel=`, `links [grep=]`, `buttons [grep=] [sel=]` (inputs/selects/buttons with
  name/id/type - the fastest way to learn a form), `click text=|sel=|role=+name= [nth=] [exact=1]`,
  `xy x= y=` (pixel click, for canvas-like pickers seen in a screenshot), `fill sel= value=`,
  `type sel= value= [clear=1]`, `press key=`, `select sel= value=|label=`, `options sel=`,
  `shot path= [full=1] [sel=]` (then Read the PNG), `eval js=` (returns JSON/str),
  `frames`, `pages`, `switch idx=`, `back`, `scroll dy=`, `wait wait=ms`,
  `net [grep=] [xhr=1] [last=n]` (recent responses), `body i=` (a captured response body -
  read booking-engine JSON straight from its XHR), `reqbody i=` (the POST body that request sent - for
  replaying an engine's own search call), `dialogs`, `quit`.
  Hidden tab/accordion text is NOT in `text`; use
  `eval js="document.body.textContent.replace(/\s+/g,' ')..."`.
- `scan.py URL [n]` - open an operator site, list its rate/booking/plan links and any
  booking-ENGINE hosts, print every `$`/tarif/minimum/saisonnier line on the home page and on
  the top n rate pages. The first call for every park.
- `rpa.sh SLUG ARRIVE DEPART` - reservationpleinair.ca (Manisoft) list view, 2 adults: unit
  or site type, services, equipment-length range, "À PARTIR DE" price. "-" = not priced/open.
  Paged 10/page, so the row count is not a site count.
- `rc1night.sh CAMPING_ID DATE` - reservationcamping.ca (Pixum) one-night search for a 23-ft
  trailer, 2+3 services, then opens 3 result sites and prints each site's minimum line.
  **The per-site page is the only place the minimum shows** ("Ce site nécessite un minimum de
  2 nuitées"): the nights select starting at 1 proves nothing (Wigwam). Some installs
  generate the select from 2 (Péninsule: the default 1-28 list is commented out in the HTML).
- `rpro.py URL [DATE] [NIGHTS]` - RéservPro (reservationquebec.net, or embedded on the
  operator's own /reservation page with `a.rp-service-action` links): per service type, the
  nights offered and the `check-disponibilite_service` JSON - `Prix`, `Frais`, `NbrDispo`
  (sites free = traveller inventory), and `Erreur` (minimum nights, "pas encore activé pour
  2027"). Minimums are per type and date (Larochelle: 2-service 2 nights, 3-service 1).
  Prints one parsed line per type (`Prix | Frais | NbrDispo | status message`). Given a single
  service page it quotes only that type; given the camp listing it visits every type. Some
  parks put only part of their inventory online (2 Rivières sells only rustic field sites in
  the engine, even for July 2027; its serviced sites go by phone at the posted rates).
- `rms.sh CLIENT_ID ARRIVE DEPART [AGENT]` - RMS Cloud (Parkbridge resorts) Rates page opened
  directly for 2 adults + travel trailer: per site type the tax-INCLUDED "From CAD" and the
  PRE-tax daily grid (weekday/weekend). No picker needed.
- `wb.py LAT LNG` / `wb.py LAT LNG REL Z OUT` - Esri Wayback: list every distinct capture
  (date, source, release) at a point in ~1 min, then stitch 3x3 tiles from a chosen release.
  The off-season imagery test for seasonal parks (see the playbook below). Caches the release
  config at `~/.cache/ekko-waybackconfig.json`.
- `satpx.py LAT LNG ZOOM X Y [X Y ...]` - lat,lng (and metres from the point) of pixel X,Y in the
  frame `satz.py`/`wb.py` stitched for LAT LNG at ZOOM. The frame is 3x3 tiles starting one tile
  left of and above the point's tile, so the crosshair is NOT at the centre - pin from this, not
  from offsets measured from the middle. Esri z19 is often "Map data not yet available"; use 18.
- `camplife.py CAMPGROUND_ID ARRIVE DEPART [N]` - CampLife (camplife.com/<id>/reservation/step1,
  behind many Ontario "Book now" buttons; curl gets 403, the driver's browser loads it). Sets the
  Duet date pickers through the host element (`value` + a `duetChange` event - typing appends to
  the old value), opens Select Site, prints the notices ("2 night minimum...", "2027
  RESERVATIONS OPEN MID NOVEMBER") and the available count, and prices N sites from the
  `/api/invoice/estimate` XHR (resSubTotal = pre-tax). US parks list day-use pavilions among the
  sites: `CL_NOT='PAV|cabin'` (or `CL_GREP=`) filters the picks and `CL_LIST=1` prints every
  available option first. Some parks show campsite prices only after a login ("Login required to
  check availability ... for all sites except pavilions", Jetty Park FL): don't sign up, ask AWH.
  Since 2026 some parks have a combobox site picker (`button.combobox-trigger` +
  `[role=option]`) instead of vue-select; the script handles both (Artillery Ridge PA). A park's
  per-stay charge can sit inside `resSubTotal` with no label: Artillery Ridge's one night is the
  rate plus $17.50 and two nights twice the rate plus $17.50, untaxed and outside the one-night
  deposit (`amountDue`). Quote one and two nights on the same sites to separate the two. The
  page loads slowly at times; "no date pickers" means it hadn't rendered, so run again.
- `pwu.py URL ARRIVE DEPART` - Park With Us (`parkwith.us/camps/<slug>`, city and county
  parks): picks the dates on its react-day-picker, fills the prerequisites (23-ft rig, 2 adults)
  and tallies the site list's "$65.00 / night" prices by site row (Noccalula Falls AL, Carl
  Precht WA).
- `campspot.py SLUG ARRIVE DEPART` - Campspot. **Two traps, both met in Ontario:** (1) the
  `/book/<slug>/search/<in>/<out>/guests.../list` page can say "no sites available" while the
  park's availability API lists free sites, and (2) the guests segment follows the PARK's guest
  categories in order ([Children, Adults, Pets] at one park, [Children 0-5, Children 6-17,
  Adults, Pets] at the next), so `guests0,2,0` is 2 adults at one park and 2 children at
  another. The script reads the categories from the guests picker, builds the string for 2
  adults and prints the API answer per site type (price, free/total, longest rig, failure
  reasons such as RESERVATION_MIN_RULE or RESORT_CLOSED_RULE - a closed park still shows its
  prices). It falls back to the marketplace `/park/<slug>` page when the slug has no /book/
  engine (Summerhill white-label parks).
  The park record (`/api/gator-core/v2/parks/slug/<slug>`, in `net` after loading /book/<slug>)
  carries the operator's own `latitude`/`longitude` - a better pin source than a Google point
  that sits on the road (Cedar Falls BC).
- `campspot_site.py SLUG GUESTS CHECKIN CHECKOUT CATEGORY_ID [...]` - the price breakdown on a
  Campspot site-type page: "$52.92 x 1 night", each fee line and "Site Total". **The
  availability API's `averagePricePerNight` (what `campspot.py` prints) is the Site Total**, so
  it folds the park's own "Campground Fees" into the rate: Bear Run PA's $58.92 is a $52.92 site
  plus $6.00. Take GUESTS from `campspot.py`'s output and the category ids from the `id` of each
  type in its availability answer. Quote two nights before calling a fee per stay: Bear Run,
  Mountain Top, Wheelin, Palmetto Shores and Colonial Pines charge a flat fee once per stay,
  while Stow OH's is 3% of the site charge ($0.66 a night). Campspot's own "Booking Fee" (3%, at
  least $3) shows up only at the parks that pass it on, and is the platform's charge, not the
  park's. **Always give the full guests string, pets included (`guests0,2,0`):** a search URL
  that leaves pets out gets the pet count the browser last used, and a pet-free site then
  reports MAX_PET_RULE (2026-10-13).
- `koa.py SLUG CHECKIN CHECKOUT` (dates MM/DD/YYYY) - KOA's own booking form. Plain fetches of
  koa.com get a Cloudflare challenge; the driver's browser does not. Fills step 1 for RV, 2
  adults, no pets, a 23-ft motorhome and prints step 2's site types with their "avg/night"
  price (the site rate before tax; "KOA Select My Site" is +$20 on top). `KOA_DUMP=PATH` saves
  the page text: read the "buddy" descriptions, because some pairs need two reservations (Grove
  City PA's patio pair) and others are priced per site ("One RV per site", St. Augustine Beach
  FL).
- `nbq.py NEWBOOK_URL ARRIVE DEPART` - Newbook (`bookingsus.newbook.cloud/<park>/index.php`,
  Pinnacle Lifestyles parks) through the driver; `newbook.py` above launches its own browser.
  Newbook ignores URL dates, so it sets the form fields (dates as "Mon D YYYY", Feet, 23, Travel
  Trailer) with jQuery change triggers and prints each category's "From $X / night", its
  availability line and any "7 Night min" rule (White Lake BC: C$77.50).
- `bqread.py URL` - Bonjour Québec listing (curl-readable): "Prix maximum par nuitée pour
  emplacement de camping", unit count, address/phone/website, CITQ number. Find the URL with
  a web search "bonjourquebec <campground name>".

Engines worked by hand (no script yet):
- **campin.ca** (Camping Québec partner): `campin.ca/en/search/campings/search?utf8=%E2%9C%93&search_camping_availability[camping_id]=<id>&search_camping_availability[start_date]=YYYY-MM-DD&search_camping_availability[end_date]=YYYY-MM-DD&search_camping_availability[authorized_equipments]=3&search_camping_availability[max_length_equipment]=23&search_camping_availability[flexible_date]=0&search_options=C`
  - shows "Open from <season>"; "no result" when the season isn't open. Its name search needs region filters.
- **Reservit** (`secure.reservit.com/fo/booking/58/<hotelid>/dates`): 2-month calendar, `button.next`
  advances a month, pink cells = unavailable/not open.
- **Small WordPress engines** (`/reservation-en-ligne/?item=P<id>`): per type, the allowed
  equipment list (a 2-service type may exclude travel trailers - Lac Frontière), the site list
  (`select.cal-plan-select`), and a "Vérifier" form whose answer prints "Total : <price> (taxe en sus)".
- **RMS Cloud via the UI** (if the direct URL ever stops working): dismiss the cookie banner,
  click `#arriveDate`, step months with the arrow right of the month row, click the days,
  guests bubble `#show-bubble` (+ then Ok), radio "Overnight Site", hidden mobiscroll selects
  `#T` (Travel Trailer = 13) / `#L` set by value + change event, "Search Availability".
- **Camping Union network** (campingunion.com - Demi-Lieue, du Gouffre, Parc de la Chaudière,
  Lac Saint-Michel, Chutes-aux-Iroquois, Falaise-sur-Mer, Annie, Lac-du-Cerf, Baskatong): one
  2026 rate grid per park on `/tarifications/`; online reservations need 2 nights but the
  same-day "Nuitée Express" (bought after 16:00, out by 09:00, 20% off) and walk-ins sell one
  night - a late-booking waiver, not a standing minimum.
- **Camping au Soleil** chain (St-Côme, Wentworth-Nord, St-Paulin, St-Paul-de-Joliette,
  Mirabel): RéservPro, one page per park.
- **Parkbridge** (parkbridge.com/fr/resort/resort-detail/<slug>): traveller rates only in RMS
  (`bookings.rmscloud.com/Search/Index/<id>/137` on the resort page); the site map is a PDF
  ("Cliquez ici pour télécharger la carte"). Most Quebec Parkbridge resorts are ~7-8% traveller
  (skip), but Domaine des Érables is ~20% (add) - measure each, don't skip on the brand.
- **RezExpert** (`online.rezexpert.com/book?business_code=<code>`, Holiday Trails Resorts): tick
  the terms radio `input[name=radPreConditionAccept]`, click `Accept` (`exact=1`); in Check
  Availability, `Select Dates` opens a calendar of only the bookable months (Oct 2026: Oct-Nov
  only, 2027 not loaded) - `shot`, then `xy` the check-in and check-out days; `Select Occupants`
  opens a bubble (`xy` the Adults + twice, then OK); set the rig length on `input.DimensionValue`
  (`txtLength`, unit `cboMeasureUnit` = Feet) to 23 with input/change/blur events; `click
  text='Check Availability' nth=1`; the text after "Available" lists each site type and its
  "$49.00" from-price, pre-tax, plus a per-booking reservation fee (C$7 at Sunshine Valley).
- **WebRez** (`secure.webrez.com/hotel/<id>/?arrival_date=YYYY-MM-DD&num_nights=1&num_adults=2&num_children=0`):
  the room search loads in `frame=1` (`Bookings105/activity-edit.html?...roomsearch_version6_perl`)
  beside a Cloudflare Turnstile frame (`challenges.cloudflare.com/.../turnstile/...`); the booking
  frame says "Verifying you are human" or "No rooms found that match the selected filters" until
  a person passes it. **Do not try to get past it** - it is the one case the Canada no-holds rule
  keeps: record a hold (`kind_of_no` "engine behind a human check") with the exact URL so AWH can
  read one July weeknight, 2 adults, RV site in a normal browser (BC: Riverside 3538, Crazy Creek
  2021, Cedar Beach 1144). Read the operator's own pages for a posted rate first.
- **Wix Hotels** (Wix sites' "Book now" page), two generations: the older widget is an iframe
  (`hotels.wixapps.net/index.html?...`) - `text frame=1` lists every unit as "RV Lot 1 / Full Hook
  Up / From C$50" with no dates needed, and minimums sit in each unit's description ("MINIMUM 2
  NIGHTS" on cabins only at Barney's); the newer engine renders in the page at
  `/booking-engine#/search`, defaults to tonight + 2 adults and shows "from C$40.00" per type with
  "Show Rates" and stock notes ("Last 2 rooms available"); its date strip
  (`button.box.horizontal-strip` / `input.datepicker-desktop-input`) changes the dates.
- **Checkfront** (`<x>.checkfront.com/reserve/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`): the URL
  dates take, but the category list carries no prices - click a category (`#cf-grid<N>`, "See
  Listings") for per-site "$89.00 per night" + AVAILABLE/UNAVAILABLE. Category names can carry the
  stay rule ("1-Night RV Stays Welcome", MTN Fun Basecamp).
- **Cloudbeds** (`hotels.cloudbeds.com/reservation/<id>?checkin=YYYY-MM-DD&checkout=YYYY-MM-DD&adults=2`):
  the page text opens with a schema.org JSON block (which carries the property's own `geo`
  lat/lng); the rate list is the visible text after it, between "Search results"/"Available
  rooms" and "Property Information" (Lake Front: RV Half Service C$50, Full Service C$65). A
  motel-and-RV property may list only rooms (Christina Lake: RV sites by contact only).
- **SiteMinder / The Booking Button**
  (`app.thebookingbutton.com/properties/<x>?check_in_date=DD-MM-YYYY&check_out_date=DD-MM-YYYY&number_adults=2`)
  redirects to `direct-book.com/properties/<x>?checkInDate=YYYY-MM-DD&checkOutDate=YYYY-MM-DD&...`;
  each rate plan prints its name, then a "CAD 44.00" line (Kayanara: Standard RV Campsite Rate).
- **RoverPass** (`roverpass.com/c/<slug>/booking/search?accommodation=overnight&check_in=YYYY-MM-DD&check_out=YYYY-MM-DD&site_type=type_rv_site`):
  the URL dates take, no sign-in, and each RV rate prints as "$37.00 USD/ night" with its longest
  rig. **The listing page's "Starting Daily" column can be a placeholder** - $15 for every hookup
  site against $30 for a primitive one at Clear Creek Station ID - so quote the engine instead.
  Rig size is two react-select menus (open with `xy`, then click `[id^=react-select-N-option]`);
  the cart then shows the subtotal and RoverPass's non-refundable platform fee ($3.95); tax only
  appears at the checkout details step. A RoverPass-built site (`rover.domains/preview/<slug>`)
  uses the same slug (Marion MI).

Public engines worked 2026-10-11 (the public no-rate leads, `audit/price_research/public_engine_leads_2026-10-11.json`):
- **WebTrac** (`*.myvscloud.com/webtrac/web/search.html?display=detail&module=RN&keyword=<park>&search=yes`):
  the result rows print "$27.00/$30.00" (resident/non-resident) and "Item Details" names each fee
  ("Deer Haven Resident (Standard Fee): $27.00"). Some counties show only the default tier on every
  date ("Weekday Off-Season: $61.00" at Oceano CA) - say so rather than guessing the others.
- **FareHarbor** (`fareharbor.com/embeds/book/<company>/items/`): click a site's "Select date", then a
  time slot; the booking form lists night-count options with totals ("- 2 Nights US$55"). Read the
  nightly rate off the ladder (+$25 a night) - the gap is a per-booking charge (White Mound WI:
  2 nights $55 = 2 x $25 + $5). No 1-night option = online minimum of 2 nights.
- **The Flybook** (`go.theflybook.com/book/<id>/ListView/...`): the category tabs ("CAMPSITES & RV
  SLIPS") print "$25 per night" on each listing without dates.
- **reservationfriend / camping.com** (`properties.<host>/<Park-Name>/Reservations`, Leisure
  Interactive): choose Campsite, then unit type, length 23, slide-outs 0, width 8, tick an Amp
  Service box; `onSearch()` submits (the button click alone didn't). A 1-night search for a
  2-night-minimum park comes back blank - search 2 nights; the availability grid prints the
  nightly price in each date cell (Powers OR $23).
- **ActiveCommunities** (`anc.apm.activecommunities.com/<org>/reservation/search?keyword=<park>`):
  each facility's "View fee details" lists the per-day fee by customer type and the processing fee.
- **Camava** (Don Pedro Recreation Agency `reservations.donpedrolake.com/reservation/camping/`,
  the same family as PG&E's): pick the park, dates and nights; "Use Fee" is the STAY total, so
  halve a 2-night search. Nights start at 2 there.
- **MetroParks of Butler County OH** (`reservations.yourmetroparks.net`, plain CGI): the grid and
  the day view carry no fee; it appears only in the cart, and the reserve link didn't add a site
  when followed directly. Ask AWH.
- **Bonfire** (`book.letsbonfire.com/<park>`) carries a reCAPTCHA: don't automate the search
  (same rule as Firefly); ask AWH for a saved page. **bookmysites** links now open a login page.
- **A page a plain fetch was refused** (403, TLS, bad gzip) almost always renders in the browser;
  one that fails there too has usually MOVED - search for the agency's new domain (Town of
  Bainbridge NY .org -> .gov, Chenango County, Tulare County Parks, Shelby County KY, Silverton BC
  had all moved, leaving our links dead).
- **A PDF or rate image that answers curl with 403** comes through inside the page: `eval` a
  `fetch(url)`, return the bytes as base64, decode them locally, then `pdftotext` or Read the image
  (Clay County FL's fee schedule, Lake Shelby KY's rate sheet JPEG).
- **CampLinq** pages that say "Claim your listing" are unclaimed directory records, not a booking
  channel (Crossett Harbor AR).
- Before the engine, follow the operator's own "Rates" link even when the home page shows no `$`:
  Point Hudson's rate card is a PDF behind `rates-and-fees/`, Sunnyside's rates are a bylaw PDF,
  and Orchard Springs' rate page only points at the district's site (nidwater.com), which lists them.

Public entries with no website, worked 2026-10-11 (`no_website` in the same leads file):
- **Finding the operator's page:** the search tool mostly returns directories for a small town.
  `https://html.duckduckgo.com/html/?q=<words>` loaded in the one browser (read `a.result__a`,
  unwrap the `uddg` redirect parameter) turned up the town, village and county pages it missed:
  Earl Park IN, Blanchardville WI, Starke County Parks IN, Aberdeen MS and Marathon County's booking site.
- **State tourism listings link the operator:** the "Visit the website" link on alabama.travel led to
  the operator's own domains. Both had lapsed: one is for sale, one redirects to casino spam.
- **Council minutes carry fee votes:** Bloomfield IA's new site dropped its camping-fee page, but the
  agenda PDFs are indexed; the 2025-03-06 minutes record the vote raising Lake Fisher to $20 a night.
  Minutes also surfaced the closures and seasonal turnovers that no directory shows: Aberdeen MS
  closed Morgan's Landing to RVs in 2022, and Hancock WI's 2026 minutes count 11 seasonal sites and
  2 nightly tent rentals. Many small-town minutes are scanned images with no text layer, so a grep
  that finds nothing has not ruled anything out.
- **County fee schedules** often sit in the county's document centre rather than on the park page.
  Marathon County WI's "Proposed 2026 Facility and Program Fees" PDF prices each campground. It
  needed the in-page fetch above; curl got an HTML wall.
- **Unclaimed listings, not booking channels:** a Hipcamp land page reading "Coming soon to Hipcamp /
  Contact this campground for pricing" (Twin Forks AL, Earl Park IN); CampLinq "Claim your listing";
  RoverPass "Claim my Campground" (Multipurpose Complex, Canton MS).
- **RV Life listing ids can be re-pointed:** RV Life listing `multipurpose-complex-rv-park-7946` now
  redirects to a different park, The Landing at MovieTown. Check the name and address on the page
  before trusting its reviews.
- **Let's Camp** (`letscamp.ca/camps/<slug>`) is the booking channel for Daajing Giids' municipal
  campground; its "starting at" figure is the cheapest site (the walk-in tent rate).

The 57 local entries whose links showed no booking engine, worked 2026-10-11 (`audit/price_research/public_57_2026-10-11.json`):
- **Checkfront** (`<org>.checkfront.com/reserve/?category_id=N&start_date=YYYY-MM-DD&end_date=...`):
  the city's Squarespace page only frames it; the `frames` command shows the Checkfront URL,
  and loading it with dates prints every site with "$28.00 USD From" or "per night".
- **Hidden tabs keep their text:** Santa Barbara County's fee schedule keeps Jalama's fees in a
  tab that `innerText` skips; read `document.body.textContent` from the tab title onward.
- **Rate cards as images:** Nickerson Beach's rates are only a PNG on its rates page. Download
  it and Read it, checking the pixels rendered before writing anything down.
- **WordPress booking plugins** (MotoPress at Glasgow MO) print "FROM $35" on each site page.
- **Stale official sites:** a town camping site whose rate pages carry 2016-17 seasonal terms
  (Fallsburg NY), or a former operator's rate page from a 2017-19 site (Dauphin Island's Park &
  Beach Board), is too old to land even though it is official. The current operator page saying
  "call for rates" wins.
- **WebFetch is fine for plain municipal pages and PDFs**, and it runs alongside a long browser
  pass, so the two can work in parallel. Revize-hosted county PDFs redirect to `cms8.revize.com`.

The 106 rates that came only from our own sweep notes, re-checked 2026-10-11 (`audit/price_research/note_priced_2026-10-11.json`):
- **Background the browser pass and research beside it.** One visit per website (`$` lines,
  status words, booking links, saved after every entry) took about an hour for 106 sites, and
  WebSearch/WebFetch ran alongside it. A waiting loop written as `pgrep -f quick106.py` matches
  its own command line and never exits; use `pgrep -f 'quick10[6]'`.
- **Operator documents in other formats:** a .docx price list (Jack's Landing: unzip it and read
  `word/document.xml`), a rate-card JPEG named in the page HTML (Big Bear), a scanned town rate
  sheet (Lisbon NY: `pdftoppm` it and Read the image), a village RV reservation agreement whose
  fee table is the only rate (Ilion NY).
- **Engines that show a price without dates:** SteadyStays prints "STARTING AT $50" per site
  type; Gibbs posts next season's table once the season ends. On RJourney, the park page's
  "Starting at $4/night" is the storage product, not a campsite.
- **Campspot quotes include its fees.** Provo River names its site types with the base price
  ("Back In Site ($30)") and the quote reads $38.90, so it adds about $8 plus 3% a night. Say in
  the note which figure was recorded.
- **Moved agency pages:** the Nemaha NRD's pages are now `nemahanrd.org/recreation-areas/<name>`
  and carry the camping fee; `nrdnet.org` is the statewide association and 404s for them. Lehi
  relaunched its site and the Willow Park page is gone; reservations sit on its facility-rentals
  page.
- **Bot checks are a stop sign, not a puzzle.** Five private sites now answer "Confirm you are
  human" (one hosting provider's check) and two pages show a Cloudflare check. None was worked
  around. Burrell Park's rate came from the city page's text in the search index, and its
  source says so.
- **A directory link can hide who the operator is.** Maka-Oicu Park was filed under Murray
  County, but its phone (Worthington) and the 211 directory make it a Nobles County park. First
  Responders Park's pin is in Alexander, not Watford City, and a 2022 review quotes City Hall
  saying it closed.

### Playbook: where a "no rate" campground's rate actually is

Of the first 72 Quebec no_rate parks, most turned out to post a rate; the static crawl just
couldn't see it. Look in this order:
1. **The tarifs/tarification/prix/liste de prix page**, read in the browser: JS tables,
   tabs and accordions (`textContent`, not `text`), and rates that are an IMAGE (Wix "tarifs
   2026.jpg" - download and Read it), lazy-loaded sections (scroll, then `shot full=1` and Read
   the chunks), a separate reservation/policy page, or a "à partir de X$" line in body text.
   **Rate tables in a widget iframe** (Wix sites: POWR price-table `powr.io/plugins/price-table`,
   Wix data tables `wix-visual-data.appspot.com`) render empty in `text` and in a full-page
   `shot`: list them with `frames`, then `eval js` an `iframe.scrollIntoView()` on the widget,
   wait ~5 s, and read `text frame=N` or a viewport `shot` (Fort Steele BC, Scott's ON).
   **Read the home page's text, not only its `$` lines**: a closure notice carries no figure,
   so a `$`-line crawl passes straight over "SOLD and closing our doors" (Westview AB, 2026-10-11).
2. **The booking engine** (scan.py prints ENGINE links): quote one night, 2 adults, a 23-ft
   trailer, a July weeknight (2027 was mostly NOT open in Oct 2026 - use the current-season
   table or any open date). An engine quote overrules a lower posted price (Bellerive: list
   C$67.50, engine only sells the site at C$75.50).
3. **The Wayback Machine** when the page now says "prix à venir": CDX
   `web.archive.org/cdx/search/cdx?url=<page>&output=json&from=2025&fl=timestamp,statuscode`,
   then `web.archive.org/web/<ts>/<url>` (60-90 s timeouts). Last season's operator table.
   The same route recovers an ENGINE LINK when the live site now sits behind a bot check: fetch
   the raw capture `web.archive.org/web/<ts>id_/<url>` and grep it for the engine host - Killam's
   Paradise Valley shows "Confirm you are human" today, but its 2021 copy names RMS client 11545,
   and `rms.sh 11545 ...` still quotes (C$79, a price skip). archive.org rate-limits too (429):
   one request at a time.
4. **Bonjour Québec** (official provincial listing, operator-supplied): its "Prix maximum"
   BOUNDS every site - a maximum <= C$69 passes the price gate outright (Chez Moose C$52,
   Ensoleillé C$54.95); it confirms a stale operator table (Baie du Diable max C$60 = its top
   rate) and whether operator prices include tax (du Rivage max C$52.19 = C$60 / 1.14975); and
   it shows the park is operating this season when the operator site is stale.
- **Tax**: Quebec GST 5% + QST 9.975% = 14.975%. Campsites are EXEMPT from the 3.5% lodging
  tax (ready-to-camp/chalets are not), so tax-included / 1.14975 = pre-tax (Leroux C$80 ->
  C$69.58, a skip by C$0.58).
- **wordpress.com sites** answer a browser with an "I am human" page but serve the real page to
  `curl` with a browser UA (Frelighsburg, du Rivage) - that is not a captcha to get past, just
  read with curl. **campingquebec.com** is a Cloudflare managed challenge: do not bypass; it is
  not a source.
- Phone-only booking with NO posted rate = skip (AWH 2026-10-08). A posted rate with phone
  booking is judged normally.
- Renamed parks: read the operator site's own name and address (Belle-Montagne -> Camping au
  Soleil St-Paulin; Ste-Émélie -> Aventure Rivière-Noire; Domaine Madalie -> Plage Ô 4 Îles,
  whose old domain now redirects to a gambling site - Google's website field had the new one).
  Settle the RV Life row and its Good Sam twin together.

### Playbook: is it mostly seasonal?

Quebec private parks are nearly all part seasonal. Measure the traveller share, in order:
1. **The operator's map legend** often colours Saisonnier vs Voyageur/Passant sites - download
   the full-res map, crop with PIL, count. Some state it in text ("25 emplacements voyageurs ...
   120 saisonniers", "276 sites dont 68 destinés aux campeurs voyageurs").
2. **Engine availability for a future weeknight**: RéservPro `NbrDispo` per type,
   reservationcamping "N sites disponibles trouvés" (St-Paulin 40, Ste-Émélie 61, Larochelle 75
   free; Pin d'Érable only 8 -> seasonal).
3. **Off-season imagery** (`wb.py`): a pre-opening/post-closing frame with a stored trailer on
   nearly every pad = seasonal (Domaine Florent, Ô 4 Îles); mostly empty pads = traveller
   (Camping du Parc, Frelighsburg, du Gouffre, Beau-Soleil). Canopy-blind frames can't
   overrule a posted traveller rate (add with a caveat - Baie du Diable).
- Working line used (2026-10-08, from AWH's Sutter's precedent of ~9%): **traveller sites under
  ~10% of the park = mostly seasonal, skip** (Royal Papineau 7%, Panoramique 8%, 15/30 5%,
  Au Pied du Mont 4%, Pin d'Érable 5%); 12%+ with a real traveller block = add (Oasis 12%,
  Vallée Bleue 19%, St-Édouard 22%).
