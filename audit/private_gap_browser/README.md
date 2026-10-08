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
  read booking-engine JSON straight from its XHR), `dialogs`, `quit`.
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

### Playbook: where a "no rate" campground's rate actually is

Of the first 72 Quebec no_rate parks, most turned out to post a rate; the static crawl just
couldn't see it. Look in this order:
1. **The tarifs/tarification/prix/liste de prix page**, read in the browser: JS tables,
   tabs and accordions (`textContent`, not `text`), and rates that are an IMAGE (Wix "tarifs
   2026.jpg" - download and Read it), lazy-loaded sections (scroll, then `shot full=1` and Read
   the chunks), a separate reservation/policy page, or a "à partir de X$" line in body text.
2. **The booking engine** (scan.py prints ENGINE links): quote one night, 2 adults, a 23-ft
   trailer, a July weeknight (2027 was mostly NOT open in Oct 2026 - use the current-season
   table or any open date). An engine quote overrules a lower posted price (Bellerive: list
   C$67.50, engine only sells the site at C$75.50).
3. **The Wayback Machine** when the page now says "prix à venir": CDX
   `web.archive.org/cdx/search/cdx?url=<page>&output=json&from=2025&fl=timestamp,statuscode`,
   then `web.archive.org/web/<ts>/<url>` (60-90 s timeouts). Last season's operator table.
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
