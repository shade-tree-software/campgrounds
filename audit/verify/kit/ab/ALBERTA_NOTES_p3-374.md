# p3-374 notes (2026-11-10)

- provincial:AB policy row already holds window_opens_days 90, max_stay 10, reservation_fee 12, GST included: never write those per entry (p3-374 first wrote 90 on 8929/9008, then removed it).
- Alberta Parks pages name a "Facility Operator:" line (Sandy McNabb = Kananaskis Campground Services Inc.; Sibbald Lake = Cedar & Spruce Campgrounds; Queen Elizabeth and Zeiner have none). The seniors line reads "This campground qualifies for the camping fee discount for Alberta seniors." (present on Zeiner, QE, Sibbald; absent on Sandy McNabb).
- AB shop: parkId pages cover a whole park (330125 = all of Sheep River incl. Bluerock equestrian), so filter ralist output with rasum's regex. Needs a cookie jar (-c/-b) to answer 200. "Status: Closed through <date>" gives next opening. The shop html carries itemprop latitude/longitude for the campground (Sibbald 51.04688,-114.86058).
- AB shop site types can disagree with the page table: Sibbald page "Unserviced 128" but the shop has 91 RV sites + 39 tent-only (all of Loop E).
- Tear-sheet PDFs (/media/<id>/<name>-tear-sheet.pdf) have campground maps with a 50 m scale bar - good for water distance and loop identification.
- Let's Camp API: GET https://letscamp.ca/api/camps/<slug>?locale=en with header "X-Tenant-Type: camp" works with plain curl; sites at /api/camps/<campId>/sites?locale=en.
- Zeiner (Pigeon Lake PP) phone is 780-389-2394; 780-586-2644 is the Pigeon Lake campground.
- rimbey.com answers 403 to curl (do not spoof the UA - the classifier refuses); the Wayback id_ copy works. Wayback/CDX was offline later the same day.
- campridgepark.ca now redirects to a payday-loan site (cupe2111.ca) - never cite.
- Parks Canada: per-site fees /visite-visit/tarifs-fees and hours /visite-visit/heures-hours for NHS sites; Banff contact numbers at /pn-np/ab/banff/info/contact. reservation.pc.gc.ca API answers 403 to curl; in the browser the resourceLocation body is truncated at 200k chars (Banff only), so per-campground site lists stay unread.
- Firefly Reservations (Sherk's) shows unit classes on a plain GET but prices only after a reCAPTCHA search - rate stays UNREAD.
- Overpass answered 406 to UA Mozilla/5.0 and kumi mirror timed out; use agency maps/shop coordinates instead.
- Eastern Irrigation District calls its Rolling Hills campground "privately owned and operated by the Eastern Irrigation District"; season 2026 May 14 - Sep 10 (not Oct).
- Rocky Mountain House NHS: the stored pin is the visitor centre; the trailer campground is ~1.4 km SSW (Google 52.35175,-114.97879).
