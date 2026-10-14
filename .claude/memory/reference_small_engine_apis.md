---
name: reference_small_engine_apis
description: Set Your Sites and Let's Camp answer plain public JSON with no browser - per-site price, length, hookups and walk-up flags (SYS), open dates, max RV length and a "from" price (Let's Camp); recipes from batch 20 of the Campspot pass
metadata:
  type: reference
---

Found 2026-10-14 pricing parks that had left Campspot ([[reference_campspot_api]], [[project_price_research]]). Both answered urllib with no login and no browser.

**Set Your Sites** (booking links read `portal.setyoursites.com/explore/campground/<slug>` or `/reservations/<slug>`):
- `https://api.setyoursites.com/api/campgrounds/<slug>` gives the campground record (its `id` uuid, `campsites`, announcement).
- `https://api.setyoursites.com/api/campgrounds/<uuid>/availability?targetStart=YYYY-MM-DD&requestedNights=1` gives one row per campsite: `campsite.price` (nightly), `siteLength`, `water`, `sewer`, `has20Amp`/`has30Amp`/`has50Amp`, `wifi`, `minNights`/`maxNights`, and `walkupEnabled`/`reservationEnabled`.
- `https://api.setyoursites.com/api/campgrounds/<uuid>/calendar?startDate=YYYY-MM-DD&days=365&requestedNights=1` gives per-day `availableSiteCount`/`reservableSiteCount`, which shows the season.
- Traps: one `siteLength` on every site, horse stalls included, is a default rather than a measurement (Adams County Fairgrounds 2765: all 60 ft). The calendar's last open day can differ from the page's stated closing (2765: empty from October 17, the page says October 19).

**Let's Camp** (Canadian; park pages at `letscamp.ca/camps/<slug>`; 57 tier-only entries link it as of 2026-10-14):
- `https://letscamp.ca/api/camps/<slug>?locale=en` gives `camp.minimumPrice` (the page's "Price starting at"), `camp.info.includeTax`, `camp.settings.minNights`/`maxNights`, the refund policies, `camp.siteTypes` (empty for McNab), and `metaData.futureAvailableDates` (the season's open dates) and `metaData.maxRVLength`.
- `https://letscamp.ca/api/camps/<camp._id>/status?locale=en` gives `status` and `earliestBookingDate` (when bookings reopen).
- The "from" price matched none of McNab 9254's posted rates (C$20 against C$25-42), so price from the operator's own rate page where there is one.

Old campreservations.ca links now redirect to Campspot's home page: the link is dead, not a Campspot listing.
