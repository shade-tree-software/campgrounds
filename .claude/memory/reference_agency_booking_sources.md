---
name: reference_agency_booking_sources
description: Where an agency's booking rules can be read without a browser - eDirect grid API (AllowWebBooking), Camis resourceLocation, ReserveAmerica park-page policy blocks, state admin codes on LII/SOS sites; which sites wall bots
metadata:
  type: reference
---

Sources that answered for the 2026-10-20 registry pass ([[project-campground-schema]], method in [[reference_agency_policy_research]]):

- **US eDirect** (ReserveNevada, ReserveOhio, ReserveND, WY…): `<host>/rdr/fd/citypark`, `rdr/search/place`, `rdr/search/grid` — the grid's per-unit `AllowWebBooking` says whether a park is really reservable online. NV's catalog overturned five "not reservable" notes.
- **Camis / goingtocamp** (NS, NB, NL, WI, MB…): `/api/resourceLocation` lists the parks; policies are on the agency's own site, not the engine.
- **ReserveAmerica / Aspira** (`*.reserveamerica.com`, peiprovincialparks.ca): each `campgroundDetails.do` page carries "Booking Window" and "Fees and Cancellation Policies" / "Alerts" blocks in plain HTML; one park's page is usually the whole agency's policy. Needs a cookie jar (`curl -c/-b`) or it 302s.
- **Admin codes beat the website** for stay limits: IDAPA, NAC (NV), N.J.A.C. via Cornell LII, RICR via rules.sos.ri.gov, NH Ncr.
- **Bot walls (don't bypass):** sepaq.com (403 + robots clause), NJ DEP (Incapsula), riparks.ri.gov (Cloudflare), lastateparks.com (403). Use the reservation site or the regulation, or ask AWH.
