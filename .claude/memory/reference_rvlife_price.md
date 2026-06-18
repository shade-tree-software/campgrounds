---
name: reference-rvlife-price
description: How to pull RV Life campground price ratings (0-4 dollar signs) programmatically
metadata: 
  node_type: memory
  type: reference
  originSessionId: c8ea6a71-08f2-45a1-8ff8-4a363d1ac421
---

`campgrounds.rvlife.com` shows a price rating of 0–4 dollar signs. It's NOT in the rendered text (JS app), but the value is in the page's embedded JSON as `"pricing":"priceN"` (N = dollar-sign count), and far more usefully in their **Algolia** index.

- Algolia: APP_ID `H0LPZK92QJ`, search key `88da91e06e8ee5ec4aba26675ac26b99` (found inline in any park page's HTML: `algoliasearch('H0LPZK92QJ', '<key>')`). Indexes: `park`, `city`, `region`.
- `park` records carry `price_level` (int 0–4 = dollar signs), `star_rating`/`star` (0–5 user-facing star rating, half-steps; 0 = unrated), `avg_rate` (= average nightly price in $, NOT a rating — 0–125 range), `cg_name`, `city_name`, `region_abbvr` (e.g. "VA"), `region_name`, `_geoloc {lat,lng}`, `url` (`/regions/<state>/<city>/<slug>-<id>`), `closed`.
- `region_abbvr` is NOT facetable (filter returns 0). To pull a whole state, use a geo bounding box: `insideBoundingBox=[[minLat,minLng,maxLat,maxLng]]&hitsPerPage=1000`, then keep `region_abbvr==<ST>`. VA box `36.5,-83.7,39.5,-75.2` → 317 VA parks. Free-text `query=<name>` also works for one-offs (keep it short; multi-word all-terms queries can return 0).
- POSTs: use Python `urllib.request` (sandbox blocks `curl` POST). Endpoint `https://{APP}-dsn.algolia.net/1/indexes/park/query`, headers `X-Algolia-API-Key` + `X-Algolia-Application-Id`, body `{"params":"..."}`.

Use case: cross-check [[reference-good-sam-ratings]] parks (Good Sam triple ratings, but pricey/hard to price) against RV Life. **Inclusion rule the user set (June 2026): add a Good Sam park only if ALL hold — RV Life `price_level` <= 2 ($ or $$), RV Life `star` >= 4, AND the Good Sam asset `campground.type` is NOT `MEMBERSHIP_PARK`** (user excludes Good Sam-flagged membership campgrounds, e.g. Thousand Trails / Bluegreen sites that GS tags membership). GS `MEMBERSHIP_PARK` means the park doesn't generally rent nightly sites to non-members. The GS `type` flag is UNRELIABLE — some membership-chain parks get tagged `RV_RESORT` instead (one Thousand Trails was). So ALSO exclude membership chains by name regardless of GS flag: Thousand Trails, Encore, Bluegreen, Coast to Coast (Thousand Trails is membership-first — only a few nightly non-member sites at premium rates, so it meets the exclusion intent). Match GS→RV Life by normalized name + city (GS coords were empty in the asset index). Did this for VA: of 83 GS-rated parks, 21 were $/$$, 9 of those were also >=4 stars, and after excluding membership (4 by GS flag + 1 Thousand Trails by name) **4 survived** — kept in [[#campgrounds-json]] as ids 1123 (Chesapeake Campground) / 1124 (Cool Breeze) / 1127 (Meadows of Dan) / 1131 (Parkview RV Park). The ratings are crowd/algorithm-derived and only exist for parks listed on RV Life — WMAs/dispersed sites have none.
