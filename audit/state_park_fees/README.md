# State park nightly rates: PA, MD, WV (2026-10-12)

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
