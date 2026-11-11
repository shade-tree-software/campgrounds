# Alberta notes (p3-379)

- Let's Camp availability: POST https://letscamp.ca/api/camps/<campId>/sites/available/search?locale=en,
  headers X-Tenant-Type: camp + Content-Type: application/json; body {guestCount{adult:2..}, unitTypes[{unitType:rv,
  measurementUnit:ft,length:23}], startDate, endDate, ...}; response has `sites`. Lamont + Kneehill County (Keiver's Lake) book here.
- ResNexus (Jasper Gates): curl gets Incapsula; bw.py with ?StartDate=M/D/YYYY&EndDate=...&Adults=2 lists units + prices.
- Campspot prices include the park booking fee (Lee Creek 49.25 = 44 + 5.25). Campspot calendars for next year may be empty in November.
- mountkiddrv.com: Cloudflare challenge to curl AND headless browser; read via Wayback (cdx API). No Alberta Parks camping page exists for Mount Kidd.
- cardston.ca: 403 to curl, opens in bw.py.
- oldslionsclub.com: 406 to curl, opens in bw.py.
- McLean Creek: loops C & D (sites 71-170) are OHV loops with trail access to the PLUZ staging area -> OHV drop candidate.
- Little Elbow: tear sheet shows loops A/B are the equestrian campground; the RV campground pin belongs ~800 m SW.
- Outwest (Clearwater County): "idling your quad from your site right to the trails" -> OHV drop candidate.
- Lamont phone in DB (780-895-2220) is wrong; 780-826-0078 everywhere.
- Kneehill County also runs Braconnier Dam, Swalwell Dam, Torrington campgrounds (not in DB).
