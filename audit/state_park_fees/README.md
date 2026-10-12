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
is the state:OH registry row's.

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
sites are all 'Horse Site' on Reserve Florida ('We are known for our equestrian camping'), a question for AWH. Ohio: Caesar Creek and Paint
Creek linked their marinas' place ids (771, 773: boat slips) and now link 344 and 368; Strouds Run's campground is not
on ReserveOhio at all (first come, run by the concession Strouds Run Rentals), so its link, booking group and note say so.
Malabar Farm is priced although ReserveOhio types its sites as equestrian: ODNR says its non-electric sites 'can
accommodate equestrian campers', a general campground that also takes horses.

Helpers: `ra_sites.py` (save a state's listings), `ra_type_prices.py` (one price per site type), `ra_sample.py` /
`ra_quick.py` (sample sites across a park, with hookups; ra_quick skips the full listing), `ra_price.py` also reads the
newer "Price Breakdown / Residents Pay" layout (Delaware), `vendor_calendar.py` (the reserve.*parks calendar behind SC,
AL and TN, through the one-browser driver) and `vendor_parse.py` (its text, summed up per park, window and site kind), `rdr_place.py` (Tyler/US eDirect place search: facilities, unit types and each facility's 'Starting at' rate line),
`rdr_rates.py` (a US eDirect site's nightly rate per site type, from its search/details call).
