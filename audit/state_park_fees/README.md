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

Rules that differ by state: Maine charges its $5 reservation fee per NIGHT (recorded in `reservation_fee`, said in the
note); Delaware's non-resident price is the resident's x 1.25 rounded up (a `multiplier`); New York's State Parks add $4
on Friday, Saturday and holiday eves, DEC campgrounds don't; where every sampled RV site has electric (Sampson,
Letchworth, Selkirk Shores, Lakeside, Verona Beach, Delta Lake, every Delaware park but Seashore) the electric site is the
base and there is no electric surcharge, as in West Virginia. Illinois's base is the cheapest site an RV can use: $11
where a drive-in non-electric class exists, otherwise the electric price with the tent sites' $11 in the note.

Side fixes, recorded with their evidence: `link_fixes_2026-10-12.json` (nine Vermont booking links on a host that no longer
resolves, Green Falls' missing parkId), `corrections_2026-10-12.json` (Gilson Pond's five RV sites now have 30-amp
electric; Horseshoe Lake (Madison) is closed until May 2027). Not priced: Henderson County CA 1805 and Green River SWA
1806 (no camping information on their IDNR pages).

Helpers: `ra_sites.py` (save a state's listings), `ra_type_prices.py` (one price per site type), `ra_sample.py` /
`ra_quick.py` (sample sites across a park, with hookups; ra_quick skips the full listing), `ra_price.py` also reads the
newer "Price Breakdown / Residents Pay" layout (Delaware), `vendor_calendar.py` (the reserve.*parks calendar behind SC,
AL and TN, through the one-browser driver), `rdr_place.py` (Tyler/US eDirect place search: facilities and unit types).
