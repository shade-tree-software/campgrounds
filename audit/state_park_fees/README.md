# State park nightly rates (2026-10-12): PA, MD, WV, then the other eastern states

AWH 2026-10-12: popups for Rocky Gap, Gifford Pinchot and Blackwater Falls showed no price. 60% of
the database had only RV Life's `$` tier, and the price research had counted that tier as priced.
This pass prices each state's parks from the agency's own figures, checked against its booking site.
Findings land through `audit/price_research/apply.py`.

| state | source | checked against the booking site | entries |
|---|---|---|---|
| PA | DCNR's statewide table ([camping prices](https://www.pa.gov/agencies/dcnr/recreation/where-to-go/state-parks/state-park-prices/camping.html)) + each park's site types on pennsylvaniastateparks.reserveamerica.com (`pa_types.py` → `pa_site_types_*.json`) | Gifford Pinchot, Cherry Springs, Poe Paddy, Cook Forest (`pa_booking_checks_*.log`) | 50 |
| MD | each park's line on [dnr.maryland.gov oc.aspx](https://dnr.maryland.gov/publiclands/Pages/oc.aspx) | all 21 parks, one site per type (`md_booking_checks_*.log`) | 24 |
| WV | no published table: book.wvstateparks.com prices per site (`wv_tiles.py` → `wv_booking_*.json`) | it is the source | 25 + Briar Point |

How each schedule maps onto `fees` (docs/campground-schema.md §4.2: the base is a resident's plain site):

- **PA**: base $16 rustic / $20 modern (showers); surcharges electric +$7, full hookup +$21 (electric $7 +
  water and sewer $14), Friday/Saturday/holiday +$4; non-resident +$5/night; $6.50 transaction fee.
  "Modern-Rustic" loops are priced as modern (Cook Forest). Two full-hookup sites at Gifford
  Pinchot cost $43, $2 over the table (most likely designated pet sites).
- **MD**: base is the park's "Campsite" line; electric and electric/water/sewer as the difference;
  Friday/Saturday +$1; $6.25 transaction fee; no out-of-state camping rate (the booking site shows
  none). Wolf Den Run's page says $15, the booking site charges $10-11, and the entry says both.
- **WV**: each site category has its own price, so the base is the non-electric price and the
  electric surcharge is the difference to the cheapest electric site. Where every reservable RV
  site has electric, the range is the electric sites' and there is no surcharge. Weekend and
  April prices are the same except where the note says otherwise.

Not priced, no published rate found: Salt Springs PA 308 (Friends of Salt Springs, by phone),
Denton Hill PA 1061 (Denton Go, Firefly captcha), Bluestone WV 232 and Panther WV 877 (only their
shelters are on the booking site), Canaan Valley WV 526 (CampLife now picks sites on a map the
helper can't drive). The WV WMAs stay empty (AWH 2026-10-11).

Rebuild the findings from the committed evidence: `python3 -I pa_build.py pa_site_types_2026-10-12.json OUT`,
`python3 -I md_build.py OUT`, `python3 -I wv_build.py wv_booking_prices_2026-10-12.json wv_booking_weekend_2026-10-12.json OUT`.

## The other eastern states (2026-10-12, AWH: "Start working on the rest of the state park. Do Eastern states first.")

| state | source | checked against the booking site | entries |
|---|---|---|---|
| ME | Bureau of Parks and Lands fee schedule ([campground fees](https://www.maine.gov/dacf/parks/camping/reservations/campground_fees.shtml)), unchanged in Wayback since 2024-04 (`me_build.py`) | not possible: the engine only takes dates in its 2026 online season | 11 |
| NH | NH State Parks' [rate table by site type](https://www.nhstateparks.org/fees-reservations/camping-rates-reservations) + each park's site types | every park, 2027 nights (`ne_booking_checks_*.log`) | 17 |
| VT | [Camping fees](https://vtstateparks.com/camping) in effect since 2025-07-01 ($20 resident / $38 non-resident, prime +$2) | every park, sampled sites (`vt_booking_sample_*.jsonl`) | 27 |
| RI | the fee regulation's three tiers ([250-RICR-100-00-8](https://rules.sos.ri.gov/regulations/Part/250-100-00-8)) | every park, October 2026 nights (2027 bookings are on hold while RI picks a new vendor) | 4 |
| CT | DEEP's [parking and camping fee table](https://portal.ct.gov/DEEP/State-Parks/Parking-and-Camping-Fees---CT-State-Parks-and-Forests) | every park, 2027 nights | 14 |
| NJ | NJ Outdoors lists every site's resident / non-resident cost (`nj_sites.py` → `nj_sites_*.json`) | it is the source | 13 |
| NY | State Parks: the [statewide schedule](https://parks.ny.gov/camping/fees-policies) + sampled sites per park (`ra_quick.py` → `ny_booking_sample_*.jsonl`); DEC: its [2026 campground summary](https://dec.ny.gov/sites/default/files/2025-04/summerreccampgroundsummary.pdf) | State Parks: it is the source; DEC: 5 of 20 matched | 52 |
| DE | the booking site (Delaware's 2026 rate PDF refuses every fetch): winter, spring, summer weekday and a summer Saturday (`de_booking_sample_*.jsonl`) | it is the source | 5 |
| IL | IDNR's [2027 schedule](https://dnr.illinois.gov/content/dam/soi/en/web/dnr/parks/2027-camping-changes/fee.pdf) applied to each park's site classes (booking API `rdr_place.py` + IDNR camping pages `il_classes.py`); State Fairgrounds from its own rate table | site classes only | 56 |
| SC | no published table: every bookable night on reserve.southcarolinaparks.com's calendar for two weeks from 2026-10-13 and from 2027-06-15 (`vendor_calendar.py` → `vendor_parse.py` → `sc_calendar_summary_*.json`, `sc_build.py`) | it is the source | 18 |
| AL | the same, on reserve.alapark.com with an Alabama zip; Cheaha re-read with a Pennsylvania zip gave the same prices (`al_calendar_summary_*.json`, `al_build.py`) | it is the source | 7 |
| WI | wisconsin.goingtocamp.com's site fee panel, Tuesday nights 2027-05-11 and 2027-06-15 (`audit/price_research/gtc_prices.py`) | it is the source | 5 |
| MS | parks: reserve.mdwfp.com's fee panel (a GoingToCamp site, `gtc_prices.py --max-fee 200`); state fishing lakes: the permit rule, [Title 40 Part 3 Rule 2.1](https://www.mdwfp.com/sites/default/files/2024-04/40-miss-admin-code-part-3-rule-21-state-fishing-lakes-rules-and-regulations-rev-04-2023-final.pdf) ($22 a day, $25 at Calling Panther, primitive $17; `ms_lakes_build.py`) | parks: it is the source; the lakes take no reservations | 19 + 13 |
| FL forests | floridastateforests.reserveamerica.com, a Tuesday and a Saturday in January 2027 (`fl_forest_booking_sample_*.jsonl`, `fl_forests_build.py`); Cypress Glen and Mutual Mine found later in its park directory | it is the source | 17 + 2 |
| IN | parks: indianastateparks.reserveamerica.com, sampled sites for Tue 2027-06-15 and Sat 2027-06-19 (`in_booking_sample_*.jsonl`, `in_build.py`); the DNR's [rate page](https://www.in.gov/dnr/state-parks/rates-and-fees/camping-fees) gives only statewide ranges. State forests: that page's first-come rate, $12 non-electric / $12.15 primitive (`in_forests_build.py`) | parks: it is the source; the forests take no reservations | 31 + 9 |
| TN | no published table: every bookable night on reserve.tnstateparks.com's calendar for two weeks from 2026-10-13 and from 2027-06-15 (`vendor_calendar.py` → `tn_parse.py` → `tn_calendar_summary_*.json`, `tn_build.py`); which calendar sites are tent or primitive comes from each park's campground page (`tn_parse.py` SITE_KIND) | it is the source | 31 + Notchy Creek |
| FL parks | each park's Hours & Fees page (`fl_park_fee_text_*.json`, read through the one-browser driver: floridastateparks.org refuses plain fetches) + Reserve Florida's 'Starting at $N' line per campground loop (`rdr_place.py` → `fl_rdr_rates_*.json`) + the statewide [fee page](https://www.floridastateparks.org/fees) (`fl_parks_build.py`) | every page fee matched its park's rate line; six parks whose page gives no camping fee are priced from the rate line | 52 |
| OH | no published table: ReserveOhio's rate for sampled sites of each type, from the call its page makes when a site is clicked (`rdr_rates.py` → `oh_booking_rates_*.jsonl`), Tue 2027-06-15 and Sat 2027-06-19 (`oh_build.py`); Strouds Run from its concession's page, Camp Perry from the Guard RV park's page | it is the source | 56 |
| VA | DCR's [camping fee table](https://www.dcr.virginia.gov/state-parks/camping-fees) (resident and non-resident price per site type and park, effective 2025-05-12; `va_fee_table_*.json`) + reservevaparks.com's site types per campground (`rdr_place.py` → `va_place_types_*.json`) (`va_build.py`); Breaks Interstate Park from its own page | 20 parks' sampled prices (`va_booking_rates_*.jsonl`) all on the table, Saturday = Tuesday; the host answered 403 after that | 24 + Breaks |
| NC | northcarolinastateparks.reserveamerica.com, sampled sites for Tue 2027-06-15 and Sat 2027-06-19 (`ra_quick.py` → `nc_booking_sample_*.jsonl`) + every Kerr Lake site's campground and type (`ra_list.py` → `nc_kerr_sites_*.json`) (`nc_build.py`) | it is the source; matches NC's statewide rate page except Umstead (+$3) | 26 |
| GA | state parks: gastateparks.reserveamerica.com, sampled sites for Tue 2027-06-15 and Sat 2027-06-19 (`ra_quick.py` → `ga_booking_sample_*.jsonl`; entry → park id from the booking directory, `ga_park_ids_*.json`); lodge parks: their concessions' iqwebbook engines, January 2027 (`ga_lodges/`); Wildlife Resources: Go Outdoors Georgia's site lists; Stone Mountain: Campspot (`ga_build.py`) | it is the source | 45 + 7 |

Rules that differ by state: Maine charges its $5 reservation fee per NIGHT (recorded in `reservation_fee`, said in the
note); Delaware's non-resident price is the resident's x 1.25 rounded up (a `multiplier`); New York's State Parks add $4
on Friday, Saturday and holiday eves, DEC campgrounds don't; where every sampled RV site has electric (Sampson,
Letchworth, Selkirk Shores, Lakeside, Verona Beach, Delta Lake, every Delaware park but Seashore) the electric site is the
base and there is no electric surcharge, as in West Virginia. Illinois's base is the cheapest site an RV can use: $11
where a drive-in non-electric class exists, otherwise the electric price with the tent sites' $11 in the note.
South Carolina, Alabama and Tennessee price each site and night by demand and publish no table, so an entry carries the
range of its RV sites over every bookable night in the two windows; Tennessee's quoted rate also leaves out tax and a
$5 reservation fee per site, which goes on each entry (no registry row covers Tennessee). `gtc_prices.py --max-fee 200` drops the monthly rate a
"Campsite/Monthly Campsite" site answers with on reserve.mdwfp.com. Florida's state forests price in odd cents, the
same on a weekday as on a Saturday, plus a $5.79 reservation fee. Indiana has no out-of-state camping rate (its
entrance fee differs by plates, the registry row's). Florida State Parks charge 'all new reservations for RV ... units at all parks' a $7
nightly utility fee on top of the park's campsite fee (tents pay the campsite fee alone), so an entry's nightly price is the
sum; the $6.70 reservation fee is per reservation, Monroe County stays add $2.50 a night, and Reserve Florida's rate line is the
campsite fee without the utility fee. `rdr_place.py` sends the page's own search body for an ISO date, which is what fills in the
rate lines. Ohio's prices are flat by site type (a Saturday costs the same as a Tuesday); as in Indiana the base is the
non-electric site where a park has one, with electric and full hookups as surcharges, and the $6.50 reservation fee
is the state:OH registry row's. Virginia: DCR's 'Standard' row is a tent-only site at several parks
(the booking site's 'Tent Only-No Hookups'), so the RV base there is the electric site; a no-hookup type whose longest
site is under 23 ft (Claytor Lake, Staunton River, Bear Creek Lake's waterview sites) is in the note, not the base.
Entries with no add-ons of their own carry `surcharges: {"weekend": 0}` (true: one price every night) so the state:VA
row's electric +$10 / full hookup +$16 do not show as typical over a price that already includes them; the same
$0 weekend went on 43 NY DEC campgrounds and 3 free NY sites (`set_surcharges.py`, `surcharge_zeros_*.json`), and the
popup prints no chip for $0. Breaks Interstate Park (the VA-KY commission's, Firefly booking) has `policy_ref: none`. New York's 43 DEC campgrounds have their own registry row, `state:new-york-dec-campgrounds`, instead of NY State Parks' (`ny_dec_row_2026-10-12.py`: DEC's reservation, rules and campground-summary pages), and DEC's free state-forest camping areas have `policy_ref: none`; the 17 whose summary line asks a 2- or 3-night reservation minimum (it lapses once DEC's season opens) carry it as `booking.min_stay` with a MINIMUM STAY note line (`ny_dec_min_stay_2026-10-12.py`). North Carolina's booking site
shows each site's rate before a $3-a-night reservation fee and its rate page quotes the sum ($30 / $35 / $40 / $45), so
the entries carry the sum; Jordan Lake's electric loop is walk-up only, priced from that statewide table. Georgia prices site by site (a park's sites differ by a few dollars) and publishes no table,
so its entries carry the range of the sampled RV sites; the $10 ParkPass is the state:GA row's. The Wildlife Resources
campgrounds (Charlie Elliott, Rocky Mountain, Evans County) and Stone Mountain Park are outside the state-park system
and have `policy_ref: none`.

Side fixes, recorded with their evidence: `link_fixes_2026-10-12.json` (nine Vermont booking links on a host that no longer
resolves, Green Falls' missing parkId), `corrections_2026-10-12.json` (Gilson Pond's five RV sites now have 30-amp
electric; Horseshoe Lake (Madison) is closed until May 2027; MS Lake Monroe's campground is closed until further
notice; TN Hiwassee/Gee Creek's closure now runs from early spring 2027 to summer 2028). Not priced: Henderson County CA 1805 and Green River SWA 1806 (no camping information on their IDNR pages);
MS Grand Gulf 5003 (its own commission's page lists 42 full-hookup sites, no price), Golden Memorial 5002 and Holmes
County 5004 (not on reserve.mdwfp.com; both pages carry renovation notices), John W. Starr 13445 (Mississippi State's
page for it is gone); TN Big Hill Pond, Cove Lake, Montgomery Bell, Norris Dam (both), Standing Stone and Pickwick Landing's Main Campground had no campsites on either calendar (all marked closed). Notchy Creek TN 4447 (the Tellico Reservoir Development
Agency's) is priced from Campspot (`notchy_campspot_*.jsonl` → `tn_notchy_fees_*.json`); its page link was dead and
is fixed in `link_fixes_2026-10-12.json`. Florida links fixed there too: Shangri-La and Ross Prairie pointed at their
CityParkIds (#!park/3315, 3311 open nothing; the PlaceIds are 62 and 58), Gilchrist Blue Springs and Santos at the dead
ReserveAmerica host, and Cypress Glen and Mutual Mine had no booking link. Not priced: FL Shangri-La 155, whose 22
sites are all 'Horse Site' on Reserve Florida ('We are known for our equestrian camping'), a question for AWH. Georgia: Fort Mountain and General Coffee linked other parks' ids (now 530158 and
530160); 14 entries had no booking link; Georgia Veterans' and Little Ocmulgee's ReserveAmerica links were dead (their
lodges take the bookings). Not priced: Little Ocmulgee 4536 (its lodge's engine lists every campsite as 'please call
hotel').

## AWH's calls and the fee display (2026-10-12, after the deploy)

`awh_calls_2026-10-12.py`: Shangri-La FL 155 dropped (every bookable site a 'Horse Site'); the seven Georgia parks
entered twice merged into AWH's originals (2/4530, 3/4537, 695/4538, 173/4521, 195/4520, 693/4545, 731/4542; the
original keeps its id, name, pin, rating and waterfront call and takes the sweep entry's links, phone, groups,
evidence and description); Stephen C. Foster 4543 renamed Okefenokee State Park. All logged in `dropped.jsonl`.

AWH, on Hither Hills' popup ('$33–37/night · non-resident rate ×2 · electric +$7/night* · …'): is an add-on inside the
range or extra, and does ×2 double the base or the total? Fixed four ways:
- a campground with its own price no longer inherits the agency's add-ons (`campground_schema._moot_agency_keys`);
  the 54 South Dakota parks whose price is the non-electric figure now carry the statewide `{"electric": 7}`
  themselves (`sd_electric_2026-10-12.json` via `set_surcharges.py`);
- the 25 NY State Parks campgrounds priced 2026-10-09 from each park's posted range (which spanned site types and
  weekends) were re-priced from the booking site like the other 52: base, own add-ons, weekend +$4
  (`ny25_booking_sample_*.jsonl` → `ny25_build.py` → `ny25_fees_*.json`, landed with `replace_fees.py`, which keeps
  the old figures under `replaced`);
- Hither Hills itself: $33 base, +$4 on weekends, non-residents double the whole price, no hookups (park page and
  23 sampled sites, `ny_hither_hills_sample_*.jsonl`);
- `fees.nonresident.applies_to` says what a multiplier multiplies: `total` for Delaware, Hither Hills and Bucks
  County, `base` for Suffolk County (its add-ons cost everyone the same); Massachusetts unknown
  (`nonresident_scope_2026-10-12.py`). The popup chips now read as a sum: '$33/night base · +$4/night on weekends ·
  non-residents pay double, add-ons included · +$7.25 booking fee'. Ohio: Caesar Creek and Paint
Creek linked their marinas' place ids (771, 773: boat slips) and now link 344 and 368; Strouds Run's campground is not
on ReserveOhio at all (first come, run by the concession Strouds Run Rentals), so its link, booking group and note say so.
Malabar Farm is priced although ReserveOhio types its sites as equestrian: ODNR says its non-electric sites 'can
accommodate equestrian campers', a general campground that also takes horses.

Helpers: `ra_sites.py` (save a state's listings), `ra_type_prices.py` (one price per site type), `ra_sample.py` /
`ra_quick.py` (sample sites across a park, with hookups; ra_quick skips the full listing), `ra_price.py` also reads the
newer "Price Breakdown / Residents Pay" layout (Delaware), `vendor_calendar.py` (the reserve.*parks calendar behind SC,
AL and TN, through the one-browser driver) and `vendor_parse.py` (its text, summed up per park, window and site kind), `rdr_place.py` (Tyler/US eDirect place search: facilities, unit types and each facility's 'Starting at' rate line),
`rdr_rates.py` (a US eDirect site's nightly rate per site type, from its search/details call).

## Atlantic Canada (2026-10-12, AWH: "continue pricing the states, eastern states first, then moving westward")

Every eastern US state agency was done, so the pass moved west from the Atlantic provinces. Prices are in CAD.

| province | source | checked against the booking site | entries |
|---|---|---|---|
| NL | ParksNL's [reservations page](https://www.parksnl.ca/reservations/): $20.15 unserviced / $30.90 serviced, $7 nightly vehicle pass, $7.00 reservation fee (incl. tax) | www.nlcamping.ca (GoingToCamp), every park's short-stay schedules, July 2027 (`gtc_probe.py` → `nl_booking_fees_*.json`, `nl_build.py`) | 13 |
| PE | PEI Provincial Parks' [2026 rates](https://www.peiprovincialparks.ca/articles/camping/pei-provincial-parks-fees-and-operating-dates) for every provincial campground: $38 / $45 two-way / $50 three-way, plus 15% HST, $6 + HST reservation fee (`pe_fee_page_*.txt`) | the ReserveAmerica site prices nothing between seasons; each park's sites, service type and length (`ra_list.py` → `pe_sites_*.json`, `pe_build.py`) | 8 |
| NS | Nova Scotia Parks' [2026 prices](https://parks.novascotia.ca/camping-fees), taxes included: $26.50 unserviced / $35.30 serviced, $8.95 reservation fee (`ns_fee_page_*.txt`) | novascotia.goingtocamp.com, every park, Tue and Sat in July 2027 (`ns_booking_fees_*.json`, `ns_build.py`) | 19 |
| NB | each park's 'Dates & Rates' tab, 2026 high and low season, before tax (`nb_park_rates_*.json`); $10 reservation fee (about-us policies) | reservations.parcsnbparks.ca (GoingToCamp) still prices 2026 nights, so both seasons were read there with each site type's hookups (`nb_booking_fees_*.json`, `nb_build.py`) | 9 |

Notes. GoingToCamp's feeDetails can answer with several fees for one site: Newfoundland returns the nightly and the
weekly rate, New Brunswick the nightly and the monthly rate plus, at République and Sugarloaf, a further 4% / 3.5% the
pages don't name (stated in those notes). `gtc_probe.py` keeps every fee as returned and the build scripts take the
nightly one; `audit/price_research/gtc_prices.py` sums them and is only right where a site has one fee. A park whose
unserviced sites are tent, van or 18-ft-trailer sites has the cheapest hookup site as its base (PEI's Cedar Dunes;
NB's Sugarloaf, New River Beach, The Anchorage and République). NB's surcharges are the high-season differences and
nightly_low/high the low- and high-season base; the notes give both seasons. Nova Scotia's Laurie and Thomas Raddall
list one serviced site each ('H1' at Thomas Raddall) and no serviced sites on their park pages, so no electric
surcharge. New Brunswick's day-use vehicle entry fees are not recorded: no page says whether campers pay them.
Not priced: Green Park PE 14939 (a leaseholder's campground; its own page lists 2-way $42 / 3-way $46 / 50-amp $50 but
is undated, Campspot has no 2027 nights yet and Wayback was down).

## Ontario and Louisiana's Sabine River Authority (2026-10-12)

| agency | source | checked against the booking site | entries |
|---|---|---|---|
| Ontario Parks | the [2026 camping fees](https://www.ontarioparks.ca/fees/camping/2026) (levels AA / A / B / C, electrical and non-electrical, before 13% HST) and the [reservation fee](https://www.ontarioparks.ca/fees/reservation/2026) ($11.00 online) | reservations.ontarioparks.ca (GoingToCamp): every park's campsite fee schedules with service type and allowed equipment, July 2026 and July 2027 (`gtc_probe.py` → `on_booking_fees_*.json`, `on_build.py`) | 91 |
| St. Lawrence Parks Commission | its [2026 fees](https://www.stlawrenceparks.com/fees/) (plus HST) and [reservation fee](https://www.stlawrenceparks.com/reservations/) ($13.25) (`slpc_fee_page_*.txt`) | reservations.parks.on.ca (GoingToCamp): every campground's schedules, July and September 2026 (`slpc_booking_fees_*.json`, `slpc_build.py`) | 8 |
| Fort William Historical Park | its [campground page](https://fwhp.ca/campground/): $25 non-serviced, $40 serviced, plus HST (`fwhp_fees_*.json`) | - | 1 |
| Sabine River Authority (LA) | its parks fee schedule, effective May 1, 2025 (`la_sra_fee_page_*.txt`, `la_sra_2026-10-12.py`) | - | 4 |

Ontario Parks prices by site: a park's loops sit at different fee levels, so an entry's nightly_low / nightly_high are its
cheapest and dearest non-electrical sites that take a 23-ft rig ('Trailer or RV up to 25ft' or longer), and the electric
surcharge is the cheapest such electrical site less the cheapest non-electrical one (none where the electrical site is no
dearer, as at Restoule). Where every RV-length site has electricity, those sites are the base (Bronte Creek, Oastler Lake,
Murphys Point, Sharbot Lake, Silver Lake). Algonquin's loops now carry Anishinaabe names (Pog Lake's Pàgwà, Rock Lake's
Somogneche and Tanakiwin; Raccoon Lake is kept out of Rock Lake). The 2027 nights still answer with the 2026 fees. Not
priced: Tea Lake 8205, whose 39 campsites take trailers up to 18 ft; dropped on AWH's call (`awh_calls_2026-10-12b.py`). The
provincial:ON registry row now carries the $11 reservation fee.

The St. Lawrence Parks Commission's eight campgrounds and Fort William Historical Park's RV park are provincial agencies
apart from Ontario Parks: they get `policy_ref: none` (`on_other_agencies_2026-10-12.py`), and the commission's its own
booking channel. Base = the cheapest unserviced site that takes a 23-ft trailer (Ivy Lea's $47.32 basic sites take 20 ft,
so its base is the $55.30 waterfront site); waterfront, premium waterfront, electric and full hookups are the table's
categories less the base. Upper Canada Campground 8343 turned out to be a private Campspot park at 13390 County Road 41,
Morrisburg (pools, camp store), not the commission's as its note said: on AWH's call it is now `private`, priced from
its own 2026 rates (C$48-65 before HST), with its July-August weekend minimum and seasonal share marked.

The Sabine River Authority's four Toledo Bend parks (Cypress Bend, Oak Ridge, San Miguel, Pleasure Point) carry the
standard RV spur as the base and the waterfront / pull-through spur as a premium site; the schedule's standing minimum
(2 nights on weekend reservations March - September, 3 on holiday and major-event weekends) is marked on each.
Not priced in Louisiana yet: Indian Creek 6870 (LDAF; rates only on ResNexus).

## Quebec (2026-10-12)

| agency | source | entries |
|---|---|---|
| SEPAQ (parcs nationaux, réserves fauniques, Lac-Simon, Voltigeurs) | sepaq.com's booking search, every campsite of each entry's loops on four 2027 nights: Tue June 8 and Tue September 7 (low season), Tue July 13 and Sat July 17 (high season #2) (`qc_sepaq_jobs.py` → `qc_sepaq_search.js` → `qc_sites_*.json`), plus site detail pages for eligible equipment, up to four per loop, type and price (`qc_sepaq_more_reads.py` → `qc_sepaq_details.js` → `qc_site_details_*.json`); `qc_build.py` | 42 |
| Corporation Nibiischii (Lacs-Albanel-Mistassini-et-Waconichi) | its Lac Albanel and Baie Pénicouane pages: $40 without services, $50 electric / $55 electric and water, plus taxes (`qc_nibiischii_fees_*.json`) | 2 |

SEPAQ prices a site by its type, its campground's rate level and the night (low season, high seasons #1 and #2,
Sunday-Thursday or Friday-Saturday; the network table on its tent-camping page gives only 'From ... to ...' ranges), so
each campground was read site by site. 2027 bookings open 2026-11-08, but the search already prices every site. The
search is a form POST that pages by the Referer (see `qc_sepaq_search.js`); sepaq.com refuses plain fetches, so it
runs inside the one-browser driver. The base is the cheapest site with no hookups that takes a 23-ft trailer or
motorhome, else the cheapest hookup site that does; nightly_low / nightly_high are its low-season and high-season
weeknight prices, the weekend surcharge the Saturday difference, electric and full hookups the high-season differences.
Equipment limits differ site by site inside a loop (Arthabaska's rustic sites take trailers from 15 to 40 ft), so a loop,
type and price counts when any site read in it fits. National parks add the daily entry fee, $10.30 an adult (children
free, taxes included; 'For a stay, the entry fee is in addition to the accommodation fee'); wildlife reserves and the
two tourist centres charge none. Lac Dunbar 12495 (its sites take trailers under 20 ft) and Baie aux Rats Musqués 12501
(tent trailers to 15 ft, the rest list no trailer) were dropped on AWH's call as too short. Not priced: Lac Arthur 12523
(its site pages list no equipment at all, so the 23-ft fit is unknown).

## Louisiana State Parks (2026-10-12)

21 parks from each park's camping rates on lastateparks.com (`la_park_rates_*.json`; the site refuses plain fetches, so
read through the one-browser driver) and the booking site's unit records (`la_booking_sites_*.json`: the
`var sites = [...]` array on each reservations.gooutdoorslouisiana.com FacilityDetails page, with type, max equipment
length and base price) (`la_build.py`). Every park prices by demand, each type from its base to 1.5 times it (Premium
$33-49.50, Improved $28-42, Unimproved $18-27, plus tax; 'subject to change depending on availability'), and the booking
site's base prices are the low ends. So an entry's nightly_low / nightly_high are its base type's range, with no fixed
weekend add-on, and the add-ons are differences between low ends. Improved is water and electric everywhere; Premium is
full hookups at some parks and water-and-electric 'prime location' or pull-through sites at others, as each page says.
Unimproved sites are the base only at Fontainebleau and Tickfaw, where the booking site shows them long enough for a
23-ft rig. $4.50 reservation fee per booking. The $3 entrance fee is not recorded: the pages don't say campers pay it
(Lake D'Arbonne's tennis courts are 'available for overnight guests and for day-use visitors with payment of entrance
fee').

## Arkansas State Parks (2026-10-12)

30 entries from every RV site's nightly rate on reserve.arkansasstateparks.com's parkwide calendar (the vendor behind
the SC/AL/TN sites), two weeks from 2026-10-13 and from 2027-06-15 (`ar_calendar.py` → `ar_calendar_*.json`,
`ar_build.py`). Arkansas publishes no rate table: 'rates are subject to change based on availability and season', and
'The quoted rate for each night does not include taxes or the reservation fee' (the fee's amount is not shown before
checkout). So, as for SC/AL/TN, an entry carries the range of its cheapest kind of RV site over every bookable night in
the two windows, and the note gives each kind's range. Each calendar row carries its site's attributes (rv-tent or
tent-only, max RV length, water, sewer, amps); RV sites are rv-tent rows of 23 ft or more, or with no length at all
where the park records none for that kind (Queen Wilhelmina, Moro Bay). A primitive site's amps field reads 'None'.
Mississippi River State Park's calendar lists Beech Point's and Storm Creek Lake's sites together, so both entries carry
the park's range. Davidsonville's booking link pointed at a slug that now redirects to the park finder; fixed
(`ar_link_fixes_*.json`). Senior discounts from the parks' camping policy are in the notes.

## Iowa State Parks and Forests (2026-10-12)

54 entries from the DNR's 'Camping Rates' sheet, updated February 15, 2026 (`ia_rate_sheet_2026-10-12.txt`, fetched in
the browser because iowadnr.gov answers plain requests with 504s): a peak (May 1 - October 15) and an off-season price
per park and site type, 'Rates are per night and include sales tax'. Checked on iowastateparks.reserveamerica.com:
sampled sites priced for Wed 2026-10-14 and Tue 2026-10-20 (`ra_quick.py` → `ia_booking_sample_*.jsonl`; 597 quotes
match the sheet) and every site of all 53 parks with its type and length (`ra_list.py` → `ia_sites_2026-10-12.json`).
`ia_build.py`: an entry's base is the non-electric site where the park has one a 23-ft rig fits, else its electric
site; nightly_low / nightly_high are the base's off-season and peak prices, electric and full hookups the peak
differences, `weekend: 0`. Off-season, every hookup site is priced as electric (the water is off). The $4.50 reservation
fee is on every quote; the $4-5 a night holiday-weekend fee (Memorial Day, July 4th, Labor Day) is in the notes. A
non-electric site with no length posted counts as fitting: the ones read are typed 'RV Site, Tent Site, Trailer Site'
with 26-100 ft sites (`ia_ne_site_details_2026-10-12.jsonl`); 'Tent Only' and walk-to sites never do. Where the booking
site charges something else the entry carries it and the note quotes the sheet: Brushy Creek's Beach Campground still
charges $25 electric / $35 full hookups (sheet $26 / $38), and Beeds Lake, Bellevue and Dolliver sell full-hookup sites
at electric + $12 that the sheet has no column for (Backbone's two are its camp hosts'). Host and two-family Buddy sites
are left out, and so is Lake Macbride's primitive south loop.

Not priced: Honey Creek Resort 2905 (not on the sheet; the resort's own site no longer lists RV sites, so it may have
closed) and Sharon Bluffs 3129 (Appanoose County Conservation, first come, no published fee). Dropped on AWH's call
(`awh_calls_2026-10-12c.py`): Shimek State Forest's White Oak 2930, whose 11 sites are all typed 'Tent Only' ('Looking
For Category: Tent Site', one 'can accommodate a pop up camper', 35-45 ft gravel pads).

## Manitoba (2026-10-12)

41 entries from every campsite fee schedule on manitoba.goingtocamp.com for Tue 2027-07-13 and Sat 2027-07-17
(`gtc_probe.py` → `mb_booking_fees_2026-10-12.json`, `mb_build.py`), with each schedule's service type and the longest
unit its sites allow. The prices are the province's 2026 fees ('Basic Services $11.55 to $23.65, Electrical Services
$17.85 to $29.95, Electrical/Water Services $21.00 to $31.00, Full Service $25.20 to $27.30', GST included), the same
every night of the week. Base = the cheapest Basic site whose units go to 25 ft or longer, else electric; electric,
water (electric/water over electric alone) and full service as add-ons; the $10.00 reservation fee and the $9.50 daily
vehicle permit ('2026 Park Vehicle Permit Fees Includes GST') on each entry. Seasonal, group, backcountry and $0 host
schedules are left out.

Not priced: Beaver Creek, Bell Lake, Singush Lake, Grass River's Iskwasum / Reed Lake / Gyles, Lake St. George,
Whitefish Lake and Falcon Creek have no campsites on the booking site (first come, self-registration; the page gives no
per-park fee), and Norris Lake and Max Lake are on it with no campsites. St. Ambroise Beach, run by Surfside Beach, a
commercial operator ('may have their own fees'), whose site now offers seasonal lots and day camping and whose Campspot
listing shows no sites, was dropped on AWH's call (`awh_calls_2026-10-12c.py`).

## Minnesota (2026-10-12)

90 entries. State parks and recreation areas (64) from ReserveMN (the US eDirect/Tyler engine; API
`mnrdr.usedirect.com/minnesotardr/rdr/`): `rdr_place.py` → `mn_places_2026-10-12.json` gives each campground's site
types and their longest vehicle length; `rdr_rates.py` found sampled sites of each type for late-October nights
(`mn_booking_rates_2026-10-12.jsonl`), and `rdr_reprice.py` priced those same sites for Tue 2027-06-15 / Sat 2027-06-19
(`mn_booking_rates_june_2026-10-12.jsonl`) - the per-site call answers beyond the 120-day window although the site list
does not, and October understates a full-hookup site once the water is off (Lake Shetek $42 on Oct 20, $34 on Oct 24).
`mn_build.py`: base = the cheapest drive-in site without electric that a 23-ft rig fits (else electric), low/high across
the entry's campgrounds, electric and full hookups as add-ons measured within one campground - everywhere the DNR fee
page's 'Electric hookup ... add $10/night' and 'Water and sewer hookup ... add $8/night' - and `weekend: 0` (Saturday
the same). Tax is additional. The state:MN registry row was a `reported` row: re-read from the fee page, it keeps the
$7 vehicle permit and gains the $8 online reservation fee ('No fee for same-day reservations')
(`mn_registry_2026-10-12.py`).

State forest campgrounds (26 priced, 31 in all) are a separate system: 'In state forests (taxes are included):
Drive-in campsites $17/night', paid online or at a state park on the day you arrive ('Beginning in 2026 ... DNR does not
accept self-payment envelopes'). They had inherited the state parks' row (vehicle permit, reservation-only rule, 120-day
window), which the row itself says does not cover them, so they now carry `policy_ref: none`. Older notes quoting $14
or envelope payment are superseded by the fees group.

Dropped on AWH's call (`awh_calls_2026-10-12c.py`): Minnesota Valley SRA 5402 - ReserveMN lists only its equestrian
campground; the Lawrence Unit's 25 drive-in sites the note described are not on it. Left alone: Grand Portage State Forest's Devilfish, Esther and McFarland lakes
carry $0 from their notes, and a commented-out notice on the DNR's forest fee page lists them among campgrounds that
'will' start charging - a question for AWH.

## Oklahoma (2026-10-12)

45 entries from okstateparks.reserveamerica.com: every site of the 31 parks (`ra_list.py` → `ok_sites_2026-10-12.json`)
and, for each loop and RV site type, up to two sites priced for Tue 2027-06-15 and one for Sat 2027-06-19 with the site
page's hookups and length (`ra_loop_types.py` → `ok_booking_rates_2026-10-12.jsonl`). Oklahoma publishes no rate table.
`ok_build.py`: every Oklahoma RV site has electricity ('Semi Modern' = water and electric, 'Modern' adds sewer), so the
base is the cheapest non-premium RV site a 23-ft rig fits; full hookups and premium sites are add-ons; the weekend
add-on is the base site's Saturday difference (+$2 at most parks, +$4 to +$8 at Lake Murray's and McGee Creek's loops,
where premium sites rise more - the note gives each). Multi-entry parks are split by loop (Lake Murray's seven
campgrounds, Fort Cobb's west-shore coves, Lake Wister, McGee Creek, Sequoyah Bay inside Sequoyah's listing, Lake
Eufaula's Dogwood). TravelOK's reservation guidelines: a 3% card service fee, no reservation fee, one vehicle's parking
pass included with a reservation, seniors 62+ and military 10% off the base rate.

Not priced: Raymond Gary 6611, Little Blue / Disney 6617, Snowdale 6619 (its TravelOK page is gone) and Beaver Dunes'
Pioneer 6621 and Hackberry Bend 6626 are not on the booking site.

## Texas (2026-10-12)

71 entries from each park's own fee pages on tpwd.texas.gov (`tx_pages.py` → `tx_park_pages_2026-10-12.json`): every
campsite type with its nightly fee and description, and the park's daily entrance fee per person 13 and older.
`tx_build.py`: a type counts for an RV unless its name makes it a tent, walk-in, hike-in, equestrian, group, overflow or
cabin site, its description bars RVs, or it caps them under 23 ft (Garner's water-only loops: '20 feet or less'); a
water-only or primitive type counts only where its page says RVs, trailers or motor homes may use it (Galveston's 'Dry
camping for tents, trailers, or motor homes', Seminole Canyon's 'Self-contained pull-through campsites'). Base = the
cheapest such type with the fewest hookups, low/high across that kind's loops; water, electric and full hookups as
add-ons; the entrance fee on each entry as `{per: person_day}` (the registry row has the shape with no amount). Cooper
Lake, Lake Somerville and Ray Roberts are split by unit. Atlanta's entrance-fee page 404s.

The 18 entries run by other state agencies come from their own pages (`tx_other_build.py`, page text in
`tx_other_pages_2026-10-12.json`): LCRA's park pages ('Starting at $25' for the six primitive drive-up parks, $35-58 for
its RV parks; entrance $5 an adult a day, $2 seniors / military / disabled), Campspot for the two Lake Fayette parks Vista
Recreation runs for LCRA (June 2027 nights; Park Prairie +$3 on a Saturday), the Historical Commission's Fort Griffin
($15 water and electric, $22 full hookups, plus its entrance fee) and Mission Dolores ($24, first come), the
Lavaca-Navidad River Authority's Brackenridge and Texana ($40 / $45, $3.50 reservation fee), the Trinity River
Authority's Wolf Creek ($25, waterfront $35, $5 a person entrance) and the Guadalupe-Blanco River Authority's Lake Wood
($35, $40 for 50 amp). Those 21 non-TPWD entries (with Hubbard Creek, Rough Creek and Coleto Creek, already priced) had
inherited TPWD's row - booking site, 150-day window, weekend minimum, per-person entry - so they now carry
`policy_ref: none` (`tx_other_agencies_2026-10-12.py`).

## Nebraska (2026-10-12)

72 entries from Game and Parks' statewide camping rates grid (`ne_camping_rates_grid_2025.pdf`, the file
outdoornebraska.gov/parks/park-pricing/ links; 'These rates are consistent across all parks throughout the state, with
the exception of Lake McConaughy'): Full Hookup $35, Electric Plus $30, Electric $25, Basic $15, Primitive $10 a night,
$5 less mid-October through April (primitive $10 all year), equestrian +$5. The grid marks each area's site levels with
dots that are graphics, so its rows are transcribed into `ne_build.py`'s GRID from the rendered page. Lake McConaughy and
Lake Ogallala price by season and day (May 21 - September 12: $40 / $35 / $20 / beach $25 Thursday-Saturday, $5 less
Sunday-Wednesday; $30 / $25 / $10 / $15 the rest of the year), and each McConaughy campground's site levels come from
the booking site's site list. The booking site matched the grid at Branched Oak, McConaughy and Ogallala for June 2027
nights (`ne_booking_check_2026-10-12.jsonl`). Base = an area's Basic site, else Primitive, else its cheapest hookup
site; low/high = off-season / in-season; electric and full hookups as in-season add-ons. The state:NE row, a
`reported` row with no amounts, now carries the park entry permit ($7 a day Nebraska plates, $14 otherwise) and the
$8.50 reservation fee (`ne_registry_2026-10-12.py`).

Not priced: Bowman Lake, Champion Lake, Crystal Lake, DLD Wayside, Lake Wanahoo and Long Lake are not on the grid, and
their pages give no fee.

## North Dakota (2026-10-12)

14 entries from North Dakota Parks and Recreation's booking site, ReserveND (the US eDirect/Tyler engine,
ndparksrdr.usedirect.com/rdr/rdr/): `rdr_place.py` listed each park's campgrounds and site types with their longest
vehicle length (`nd_places_2026-10-12.json`), `rdr_rates.py` found sample sites of each type in October
(`nd_booking_rates_2026-10-12.jsonl`), and `rdr_reprice.py` priced them for Tue 2027-06-15 and Sat 2027-06-19
(`nd_booking_rates_june_2026-10-12.jsonl`); `nd_build.py` builds `nd_fees_2026-10-12.json`. The prices are the same in
every park: primitive $15 every night, standard (electric) and modern (electric and water) $25 ($30 on a Saturday),
premium (full hookups) $30 ($35), which is what the 2026 State Parks Guide's '$25-30' and '$30-35' mean. Base = an
entry's cheapest primitive site a 23-ft rig fits (a blank length is unknown, not short), else its cheapest hookup site;
electric and full hookups are add-ons on it, and weekend is the base site's Saturday difference, with the other types'
Saturday prices in the note. North Dakota has no registry row, so each entry carries the $7 daily vehicle permit ('All
vehicles entering a state park must have a valid daily or annual vehicle entrance permit. This includes overnight
stays', the FAQ) and the reservation fee. The fee is the booking engine's: every sampled site carries a $6.00 'Fee',
the field where Ohio's engine puts its $6.50 reservation fee, while the FAQ still says '$5.80' online and '$9.00' by
phone, 'charged per campsite'. Cross Ranch's primitive campground note said $17; corrected to $15 and re-scanned.

Not repriced: Pembina Gorge 13958 keeps the guide's $25-30 from 2026-10-10 (the new campground had no sites to sample
in October). Not priced: Strawberry Lake 5900 (ND Forest Service) has no dated fee.

## Saskatchewan (2026-10-12)

41 Sask Parks entries from the 2026-27 Provincial Parks Rates and Fees table (`sk_rates_and_fees_2026-27.txt`, the PDF
the fees page links; 'Rates are set as of April 1, 2026', 'Fees include all applicable taxes'): Fully Serviced $49,
Electrical $35, Non-Electrical $20, Economy $18 a night in every park, $4 less from October 1 on electric and
non-electric sites; reservation fee $12 online or in park, $14 through the call centre, per reservation; vehicle entry
permit $11 a day ($42 a week, $82 a year), free for Saskatchewan residents 65 and older. The booking site
(parks.saskatchewan.ca, classic ReserveAmerica, contract SKPP) gives each campground's site types: `ra_list.py` listed
all 2,574 sites of the 23 parks (`sk_sites_2026-10-12.json`), and the new `ra_rate_card.py` read the posted 'Price
Rate' of two sites per loop and type (`sk_rate_card_2026-10-12.jsonl`). Classic RA pages print no 'Camping Fees (1
night)' outside the booking window, but given a date they print that rate line. Every posted rate is the table's except
Bronson Forest's electric sites, $31 (the $35 less the $4 reduced-services discount; no potable water at Little Fishing
Lake). Loops named '- NR' are first come, first served: they post no rate (the page points to the fees page), so they
take the table's price for their type, and an entry with only such sites gets no reservation fee. Base = cheapest type
a 23-ft rig fits (maximum equipment length; blank = unknown); electric and full service are add-ons; weekend 0.
`sk_build.py`. Three leased or private campgrounds on provincial land, from their own rates pages (`sk_other_build.py`,
text in `sk_operator_pages_2026-10-12.json`): Borden Bridge $25 / electric $35 (2026), Michel Point $35 / full hookups
$45, Nesslin Lake $28 / powered $38 + tax.

Notes corrected from the booking site and re-scanned: Coldwell 9167 has non-electric sites, not electric (10 on the
booking site's Coldwell - NR loop; Tourism Saskatchewan: 18 first-come sites for small units and tents, non-potable
water); Matheson Lake 9189 has electric 15/30-amp sites, a few reservable and the rest first come, first served (the
note's '46 non-electric' was Wikipedia's; Tourism Saskatchewan agrees with the booking site).

AWH's calls the same night (`awh_calls_2026-10-12d.py`): Amisk Lake Sawmill Bay 9157, Beatty Lake 9160, Cowan River
9168, Devil Lake 9180, Lac la Plonge 9185 and Tyrrell Lake 9206, self-registration campgrounds not on the booking site,
are priced $18-20 (the table's economy or non-electrical rate; which applies isn't published, and 'it's not worth
trying to narrow it down for a $2 difference'; `sk_self_registration_fees_2026-10-12.json`). Besant 9290 (Facebook and
a phone number only) is dropped. Reindeer Lake's Norvil Olson 9202 keeps its note's $0. Makwa Lake's note calls Jumbo Beach tent-only, but the booking site lists its 10 sites as
non-electric for rigs to 18-40 ft (not changed; the park's price comes from Mewasin's non-electric sites either way).

## Wyoming (2026-10-12)

12 entries (`wy_build.py`). Wyoming's '2026 Wyo Parks Fee Schedule' is statewide: 'The base rate for camping is $10 for
residents and $18 for non-residents', 'base camping fee + day use fee + sales & lodging tax', 'Electric Site Fee: $10
per night', day use $7 / $12 a vehicle at parks ($4 / $8 an adult at historic sites). Reservations moved to US eDirect
(reserve.wyoming.gov, API wyordr.usedirect.com/wyomingrdr/rdr/): `rdr_place.py` gives each park's campgrounds with their
electric and non-electric sites (`wy_places_2026-10-12.json`), and every sampled site is priced at the $10 base, Tuesday
and Saturday alike (electric fee, day use and tax are added in the cart). Each entry: $10 resident base, non-residents
+$8, electric +$10 where the campground has electric sites, day use as entrance (not at Connor Battlefield, whose page
says 'Daily use is free!' and posts the taxed $11.30 / $20.34, and not at Medicine Lodge, whose day-use fee isn't
stated). The Wyoming State Fair's RV park (state-owned, not State Parks) from its own page: $30 a night, $40 at fair
time. The old wyomingstateparks.reserveamerica.com no longer resolves: `wy_links_2026-10-12.py` points the 12 entries
that linked it (and Medicine Lodge) at their park's reserve.wyoming.gov page; Seminoe's note now names the new site and
Hawk Springs' note lost its '~$18/night' (both re-scanned).

## Colorado (2026-10-12)

54 Colorado Parks and Wildlife entries from its booking site, cpwshop.com (ReserveAmerica's 'CUI' .page platform, not
the classic .do one). `cui_sites.py` lists every site of a campground from the map its page draws:
`/ajax/CUIGISMap?event=getGISMap` (GeoJSON: loop, site type, maximum vehicle length, the site page's link), or, for the
five parks drawn on an SVG map, `/ajax/CUISVGMap?event=getMapIcons` (site and type only) (`co_sites_2026-10-12.jsonl`).
`cui_rates.py` reads a site page given `&arvdate=MM/DD/YYYY&lengthOfStay=1`, which prints 'Camping Fees (1 Night)' even
beyond the six-month window: two sites of each loop and type on Tue 2027-06-15 and one on Sat 2027-06-19, every site of
the SVG parks (`co_booking_rates_2026-10-12.jsonl`). `co_build.py` maps each entry to its park and loops and builds
`co_fees_2026-10-12.json`. June prices are nearly uniform, the top of the ranges on CPW's camping page: basic $28,
electric $36, full hookups $41, the same on a Saturday. Exceptions: John Martin Reservoir's Lake Hasty, electric $29
($31 on a Saturday) and full hookups $36 ($38); Mancos, basic $20-22; Stagecoach's McKindley loop, primitive $18. Base =
cheapest site type a 23-ft rig fits (maximum vehicle length; blank = unknown, but CPW's 0 is a site with no room for a
vehicle); electric and full hookups are add-ons, weekend the base site's Saturday difference. The daily vehicle pass is
the state:CO row's. CPW's reservation fee is not recorded: no current CPW page states it (the old reservation FAQ said
$10). Lake Pueblo's Northern Plains entry takes the Yucca Flats, Prairie Ridge, Kettle Creek and Eagle View loops and
Steamboat Lake's Dutch Hill takes Wheeler and Bridge Island, assigned by distance from the pins. The other 18 Colorado
state entries were priced from CPW's park pages and booking site on 2026-10-10 and are not repriced.

## New Mexico (2026-10-12)

38 entries (`nm_build.py`). New Mexico State Parks' fee schedule (in force since 2025-01-01; the fees page, flier and
FAQ are in `nm_fee_pages_2026-10-12.txt`) is statewide: camping per vehicle a night, residents $10 primitive / $15
developed, non-residents $15 / $20; water $5, electric $10, sewer $5 'only at sites with' them ('Sites that share
utilities would not be charged'); ReserveAmerica's reservation fee '$3.50 per night, $10.00 max. per reservation'. The
booking site (newmexicostateparks.reserveamerica.com, classic RA, contract NM) lists every site of the 30 parks
(`nm_sites_2026-10-12.json`, `ra_sites.py`; Manzano Mountains, whose entry linked a recreation.gov info page, by
`ra_list.py`), and `ra_sample.py` read every one for Tue 2027-06-15 (`nm_booking_rates_2026-10-12.jsonl`) and one per
loop for Sat 2027-06-19 (`nm_booking_rates_saturday_2026-10-12.jsonl`, all the same as Tuesday). A reservable site
quotes the resident and non-resident price, the schedule's sums ($15, $20 with water, $25 with electric, $30 with both,
$35 full hookups); a first-come one prints 'No pricing information available ... Not available online' and pays the
same schedule. Each entry: base = the cheapest kind of site in its loops a 23-ft rig fits, priced from the quotes (the
schedule for unquoted sites); water, electric and sewer add-ons where its sites have them; non-residents +$5 a night on
the base; reservation fee 3.5 (said per night in the note, as for Maine) unless no site is reservable. A kind of site
counts when it is reservable or there are 3 or more of it (Juniper's 2 first-come hookup sites include the park's one
accessible site). Sugarite Canyon's Lake Alice hookup sites share water and pay no water fee ($25 electric, $30 full
hookups). The park-wide 'Primitive Camping' listing ($10, shore camping) is mentioned, not priced. No entrance fee is
recorded: camping is charged per vehicle and nothing says a camper also pays day use.

Conflicts written into the notes (re-scanned): Eagle Nest Lake's 19 Lakeview sites are listed with 20/30/50-amp
electric and quoted $25, while the park's page still says 'No hook-ups' (note now gives both; hookups.electric
removed as unknown); Terrero's note claimed electric, water and sewer, but the booking site lists none and quotes $15,
and the park's page counts its sites as primitive. Lower Ridge Road's '~$14/night' is gone. Mora's 10 sites are listed
but 'Not available online' for June, while the park's page says reservations only: priced at the schedule's $15, no
reservation fee recorded. Links: Crusher Hole's bare ReserveAmerica link and Manzano's recreation.gov page now point at
their parks' booking pages.

## Montana (2026-10-12)

23 Montana State Parks entries and Ennis fishing access site (`mt_build.py`; texts in `mt_fee_pages_2026-10-12.txt`).
The booking site (montanastateparks.reserveamerica.com, classic RA, contract MT) quotes nothing in October: reservations
run from the third Friday in May to the third Sunday in September within a three-month window, and every date tried
(Oct 2026 to Jun 2027) prints 'Not available online' with no rate. So the prices are FWP's fee schedule: the '2020
Montana State Parks Schedule', the scanned PDF its fees page links (pages 3-4 transcribed), whose figures are exactly the
'CURRENT' column of FWP's 2026-06-24 fee-change justifications (the proposal, no earlier than 2027, would make them $24 /
$38 and $32 / $46). Peak season: standard site $18 for residents, $28 for non-residents 'includes daily entrance fee'
(the resident rate with the Nonresident Entrance Pass), electric +$6, backcountry/rustic $12 / $20; off season $4 less
(rustic the same); accommodation tax included; reservation fee $10. The booking site's listing gives each park's site
types and lengths (`mt_sites_2026-10-12.json`, `ra_sites.py`) and `ra_rate_card.py` read two sites' details per loop and
type (`mt_site_details_2026-10-12.jsonl`; 'Looking For Category: Tent Site' marks tent sites). Base = cheapest type a
23-ft rig fits (a loop of tent sites with no lengths is left out; Finley Point's standard sites are tent sites, so its
base is electric, as at Beavertail Hill, Black Sandy and Brush Lake); electric +$6 where 3 or more electric sites fit (a
lone electric site at Big Arm, Thompson Falls, Wayfarers and Whitefish Lake isn't one); non-residents +$10 a night, which
includes their entrance fee, so no entrance is recorded (residents pay theirs with vehicle registration); off-season
rates in the note; weekend 0. FWP's pages put campsite fees at '$4-$34', which leaves no room for the schedule's +$5
premium campsite, and list rustic campsites only at Thompson Chain of Lakes and Makoshika (Makoshika's 2 rustic sites
are too few to set its base). Ackley Lake, Lost Creek and Medicine Rocks (first come, first served, not on the booking
site) take the standard rate, as FWP's 2024 notice did for Ackley Lake ('$18/night', non-residents '$28/night'). Ennis
FAS: the 2026 FAS fee table's $12 with a Montana fishing license, $18 without, which its FishMT page lists.

## Arizona (2026-10-12)

15 Arizona State Parks entries (`az_build.py`; texts in `az_fee_pages_2026-10-12.txt`). The fee schedule page
(azstateparks.com/fee-schedule) lists each park's camping fees, $25-50 a night, plus 'a $3.60 non-refundable reservation
fee per site' and $15 a night for a second vehicle; there is no resident rate and no weekend rate for camping (Lake
Havasu's and Patagonia Lake's weekend prices are day-use entrance). Camping includes the park's day use, so no entrance
is recorded. The booking engine (azstateparks.com/reserve) is behind reCAPTCHA and a bot checker and was not read; each
park's camping page says which sites take RVs. Base = the cheapest fee for a site a 23-ft rig can use: Dead Horse
Ranch's and Fool Hollow's $25 non-electric sites are tent-only and Patagonia Lake's two are 22 ft, so those parks start at
their $50 hookup sites; Lost Dutchman's non-hookup sites ($35, 'for tents or RVs'), Lyman Lake's, Roper Lake's and Alamo
Lake's ($25) are the base with hookups as add-ons. Homolovi is seasonal: June is non-electric $30 / electric $35 (winter
$25 / $40). Lake Havasu is $40-50 (an RV site in the cabin loop $40). Weekend two- and three-night minimums at Cattail
Cove, Lake Havasu and River Island are in the notes.

Dropped on AWH's call (`awh_calls_2026-10-12e.py`): Ben Avery Shooting Facility 11547 (Arizona Game and Fish), whose
campgrounds AZGFD says are 'available exclusively for competition and recreational shooters'.

## Nevada (2026-10-12)

21 Nevada State Parks entries (`nv_build.py`; texts in `nv_fee_pages_2026-10-12.txt`). The fees page (parks.nv.gov/fees,
the same lines on each park's page) gives each park's camping fee 'per vehicle, per night': $15 (non-Nevada vehicles
$20) at most parks, $20 ($25) at Big Bend of the Colorado and Valley of Fire, '+ $10.00 for sites with utility hook ups'
where a park has them. Reservations (ReserveNevada, US eDirect, API nevadardr.usedirect.com/NevadaRDR/rdr/, 3 days to 11
months ahead) carry 'a non-refundable $5.00 transaction fee per reservation'. The booking site's place search
(`nv_places_2026-10-12.json`, `rdr_place.py`) says which campgrounds have hookup sites; its per-site rate is a flat $10
at every campsite of every park, hookups or not (group areas $25; `nv_booking_rates_2026-11_2026-10-12.jsonl`,
`rdr_rates.py` for 2026-11-03 and 2026-11-07), the site part of the per-vehicle fee, so the fee table is the price.
Each entry: base = the park's fee for a site without hookups where its campground has one a rig can use, else the hookup
site's (Kershaw-Ryan, Cathedral Gorge and Echo Canyon's RV Campground: $25); +$10 (as `electric`) where it has hookup
sites; non-Nevada vehicles +$5 a night; reservation fee 5; weekend 0. No entrance recorded (the camping fee is per
vehicle). Wild Horse's note said 'no hookups', but its Loop 2 is water and electric on the booking site and the fee page
charges for hookups there: note corrected and re-scanned (hookups.electric removed as unknown amperage).

## Idaho (2026-10-12)

24 Idaho State Parks entries (`id_build.py`; texts in `id_fee_pages_2026-10-12.txt`). Idaho prices campsites by demand
('Dynamic pricing means that campsite, cabin, and day-use fees may vary based on demand', the reservations page), and
its booking site (getoutside.idaho.gov) is Itinio behind DataDome, not read. The camping page gives the statewide
ranges, tax included: basic $14-24, electric $26-32, full hookups $28-40 a night; 'Campsite fees ... do not include
MVEF', $7 a vehicle a day ($14 for non-residents at Bear Lake, Farragut, Hells Gate, Priest Lake and Round Lake);
non-residents pay $3 a night more, or double at the 'Tier A' parks (Farragut, Henrys Lake, Ponderosa, Priest Lake,
Round Lake); $10 transaction fee per reservation, 3% by card. IDAPA 26.01.20 holds only maxima ($34 / $42 / $46; 'The
board has the authority to set actual fees by board policy'). Each entry carries the ranges of the site types its note
lists (nightly_low = the cheapest type's bottom, nightly_high = the dearest type's top), the entrance, the
non-resident rule and the reservation fee; no weekend figure. Eagle Island's note had an unsourced 'premium pricing
(~$80-160/night)'; removed and re-scanned (the statewide full-hookup range applies until a dated figure says otherwise).

## Utah (2026-10-12)

43 Utah State Parks entries (`ut_build.py`; fee pages in `ut_fee_pages_2026-10-12.txt`). Each park's fee page
(stateparks.utah.gov/parks/<park>/park-fees/) lists its camping fees by campground and site type, each covering one
vehicle, so no entrance is recorded; the reservation fee is $8 a reservation (the pages and every booking-site quote).
The booking site (utahstateparks.reserveamerica.com, classic ReserveAmerica, contract UT; a four-month window) quoted
every site for Tue 2027-06-15 (`ut_booking_rates_2026-10-12.jsonl`), and one site of each loop, type and price costs the
same on Sat 2027-06-19; `ut_site_details_2026-10-12.jsonl` marks the tent-only loops (Wasatch Mountain's Oak Hollow,
whose fee-page row is 'Water/Electricity', is all 'Tent Site' on the booking site). The quotes match the fee pages
except at three parks, where the page is used and the note gives the quote (`ut_booking_months_2026-10-12.txt`): Bear
Lake (the page's summer resident rates, non-residents $5 more, the only residency split in the state; the booking site
quotes one lower price for June-August 2027), East Canyon ($5-10 less on the booking site for its whole 2027 season)
and Green River ($45 on the page; the booking site quotes $45 for November 2026 and $50 from January 2027). Red Fleet's
page lists no camping and Utahraptor's only Fossil Flats, so their prices are the booking site's. Otter Creek's
no-hookup pull-throughs are listed on the booking site with no quote; the page's $40 is the base. Seasonal rates
(Dead Horse Point peak / off-peak, Steinaker and Starvation summer / winter, Bear Lake summer / regular) are in the
notes. Goosenecks ($10) and Bear Lake's Cisco Beach are first come, first served. Palisade's note had an unsourced
'fees from ~$20'; removed and re-scanned.

## Washington (2026-10-12)

68 Washington State Parks entries (`wa_build.py`; the fees page in `wa_fee_pages_2026-10-12.txt`), every park's campsite
fee schedules on washington.goingtocamp.com for Tue 2027-06-15 and Sat 2027-06-19 (`gtc_probe.py` ->
`wa_booking_fees_2026-10-12.json`). Each site is priced in one of three tiers: $31 / $37 / $43 standard, $41 / $46 / $51
with water and electric, $46 / $51 / $56 full hookups (the fees page's peak-season ranges, tax included), the same on a
Saturday. Base = the cheapest standard site whose units go to 25 ft or longer (primitive drive-in at Joemma Beach, $12),
else the cheapest hookup site; nightly_high the dearest of that kind; hookups as add-ons over the base. Tent-only
standard sites (Maryhill, Millersylvania, Lake Chelan) and sites taking nothing over 20 ft (Potholes, Lake Easton,
Larrabee) leave a hookup site as the base. Entries named for one campground take its map only (Beacon Rock's Woodard
Creek, Fort Worden's Beach and Upper Forest); Steamboat Rock's Banks Lake primitive sites are the separate Osborn Bay and
Jones Bay entries. The state:WA registry row now carries the fees page's rules (`wa_registry_2026-10-12.py`): camping
includes the vehicle's Discover Pass parking, $8 reservation fee online, and a $15 fee per reservation for people who
do not live in Washington. The 32 DNR campgrounds inherit their own row (free with a Discover Pass) and are not repriced.

## Oregon (2026-10-12)

55 entries (`or_build.py`; page texts in `or_fee_pages_2026-10-12.txt`). Oregon State Parks' booking site
(oregonstateparks.reserveamerica.com, classic ReserveAmerica, contract OR) quotes each site's 'Residents Pay' and
'Non-Residents Pay' (25% more, rounded) plus 'Reservation Fees $10.00'; one price per park and site type, so up to four
sites of each loop and type were quoted for Tue 2027-06-15 (`or_booking_rates_2026-10-12.jsonl`) and one per park and
type for Sat 2027-06-19 (the same). June 2027 resident prices: water and electric ('STANDARD') $53-61, full hookups
$57-65, tent $31-35, primitive $15-18. Tent and primitive sites are 'Looking For Category: Tent Site', so the base is
the cheapest water-and-electric or full-hookup site a 23-ft rig fits (Cottonwood Canyon, with only drive-in primitive
sites, is $15); non-residents ×1.25 on the whole price; the rates page's 'from October 1 to April 30, weekday rates at
a lower price than weekends' is in each note. Cove Palisades' Crooked River (A and C loops) and Deschutes River (B and E)
campgrounds are priced separately. Nine first-come parks are not on the booking site and their pages list site types
only, so they carry the rates page's resident range for their type ('Rates Effective May 1, 2026'): primitive $15-17
(OPRD's 2025-08-01 notice: 'at least $15' from May 2026) at Bates, Jackson F. Kimball, Minam, Cascara and Succor Creek;
tent $20-33 at Hilgard Junction, Red Bridge, Ukiah-Dale and Catherine Creek; water and electric $29-55 at Prineville's
Jasper Point. The four Department of Forestry campgrounds (Gales Creek, Nehalem Falls, Henry Rierson Spruce Run, Jones
Creek) are ODF's flat $20 drive-in rate, first come, first served. Links fixed: Hilgard Junction and Farewell Bend
pointed at other parks' pages (`or_links_2026-10-12.json`). Minam's note had a stale '$10/night'; removed and re-scanned.

## Alberta (2026-10-12)

199 Alberta Parks entries (`ab_build.py`; `ab_campground_pages_2026-10-12.json`; the fee guidelines in
`ab_fee_guidelines_2026-10-12.txt`). Every campground page on albertaparks.ca has a 'Camping' table (site type,
campsites, amps, '$/Night', reservable dates, '-' where first come, first served) and an 'Updated' date; 73 entries
linked a park page, followed to the campground page (by link, or by the campground's slug). Base = the cheapest of
unserviced, power, power/water and full-service sites (walk-in tenting, equestrian and seasonal left out), hookups as
add-ons; GST included; one price a night. The provincial:AB registry row now carries the guidelines' $12 reservation
fee (`ab_registry_2026-10-12.py`); first-come-only campgrounds record 0. Kananaskis and Bow Valley campgrounds carry the
Kananaskis Conservation Pass ($15 a vehicle a day) as their entrance. Five campgrounds run by the Friends of the Eastern
Slopes Association list 'FOESA Membership' as the rate: 'A nightly fee is not charged; however, campers are encouraged to
purchase an annual membership' - recorded as free. Mount Kidd RV Park (a concessionaire in Kananaskis Country) is
priced from its own rates page ('Rates last verified 2026-08-05'; $40.29-59.52 before tax, $14 reservation fee). Not
priced: Fort Vermilion PRA 9018 (its Alberta Parks page is gone; Mackenzie County leases it, booking through LetsCamp,
whose page would not load). Four notes quoted prices that differ from the campground pages (Maycroft, North Dyke,
Sulphur Gates, Machesis Lake); removed and re-scanned.
