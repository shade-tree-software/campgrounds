---
name: reference_usedirect_deep_reservation_links
description: How to build deep
metadata: 
  node_type: memory
  type: reference
  originSessionId: f0f241c6-6ec0-4e4c-a2e2-5487197fe8e7
---

US eDirect reservation portals (ReserveOhio, ReserveFlorida, ReserveCalifornia, etc.) deep-link to a specific park with `<frontend>/#!park/<PlaceId>`. Get the PlaceId from the portal's `citypark` JSON API and match to a campground by name + geo.

- **ReserveOhio** — API `https://ohiordr.usedirect.com/Ohiordr/rdr/fd/citypark`; frontend deep link `https://reserveohio.com/OhioCampWeb/#!park/<PlaceId>`
- **ReserveFlorida** — API `https://floridardr.usedirect.com/FloridaRDR/rdr/fd/citypark`; frontend deep link `https://reserve.floridastateparks.org/Web/#!park/<PlaceId>`

The citypark response is a dict; each value has `Name`, `Latitude`, `Longitude`, `EntityType`, and `PlaceId`. Keep records with `PlaceId > 0` (those are bookable parks; `PlaceId 0` = city/place entries). Match our entry by name-token overlap + haversine distance (geo disambiguates name variants like "Mt"/"Mount", apostrophes). Anchors that confirm the map: Mt Gilead OH = 366, Findley OH = 349, Mike Roess FL = 46, St. Andrews FL = 64.

Find a portal's API host by fetching the frontend and grepping for `usedirect` / `apiUrl` (ReserveOhio embeds it inline; ReserveFlorida's is on a separate host `floridardr.usedirect.com`). The `#!park` route is a client-side hash, so HTTP-fetching the deep URL only returns the SPA shell — trust the API PlaceId, don't try to validate the deep URL by fetching it. floridastateparks.org and reserve.floridastateparks.org 403 to bots (WAF) regardless of validity.

NOT US eDirect: `camp.in.gov` (IN) redirects to ReserveAmerica `indianastateparks.reserveamerica.com` (Aspira) — use ReserveAmerica `campgroundDetails.do?contractCode=IN&parkId=<id>` deep links instead (no clean park-list API; look up parkId per park). `goingtocamp` (WI) is also Aspira.

Used to add deep reservation links to OH (57) and FL (38) state-park entries alongside their official park pages. See [[feedback_urls_in_website_not_notes]].
