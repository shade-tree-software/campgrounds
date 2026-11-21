# u-12 AB retry: 9047 Village of Carbon Main Campground (2026-11-21)

## Routes
1. Headless Chrome with a desktop UA (pwc.py, under flock): villageofcarbon.com gave HTTP 418 with an empty body, the same as curl. SiteGround anti-bot. REFUSED.
2. Wayback: the campground page's latest real capture is 20230519023600; the 2024 captures are sgcaptcha 202/301. Stale for rates and season. The PDFs in wp-content/uploads ARE captured in Oct/Nov 2025 and are readable:
   - Newsletter April 2025 (20251109001847): bookings moved to Let's Camp.
   - Newsletter January 2025 (20251030121136): bookings on CRC opened Feb 3 2025; council approved +$5.
   - Council agenda 16 Dec 2024 (20251029032055), p.95: RFD rate table (2024 rates).
   - Council agenda 27 Oct 2025 (20251031004221): PW report, water off Oct 7, gates locked end of Oct, reopen spring 2026.
   - The minutes PDFs (Dec 2024, Jan 2025, Aug 2025) are image-only. pdftotext gives nothing.
   - The 2025-11-01 capture of /category/camp-in-carbon/ still links /attractions/campgrounds/, so the stored website stays.
3. Strong secondary: Let's Camp (curl with header X-Tenant-Type: camp)
   - slug carbon-main-campground, id 67928ddd3cb7f3aa32a6dac4
   - sites 1-22 + 16A, all back-in; 3 and 16A are 20 ft
   - maxNights 30, check-in 14:00, check-out 12:00
   - phone 403-572-3244
   - no prices off-season
   - East = carbon-east-campground
   - The site map is an SVG (cloudinary). Render it via playwright set_content. It is rotated: the top is the west street, and the bottom row (10-16A + washroom) is the east side by Kneehills Creek.
   Travel Alberta listing 5747 (modified 2026-09-25) is corroboration.
- Old campreservations.ca listing -> 301 to campspot.com home (dead).

## Calls
- Fees C$45-50 for 2025 = the 2024 RFD rates (40/43/45) + the approved $5. Written as reported, checked 2025.
- Waterfront: kept as not waterfront. The creek is 25-35 m behind a continuous treed strip east of the loop.
- Pin: OK (Let's Camp point ~90 m).
- Season: left as derived.
- Phone: '' -> 403-572-3244.

## Tool notes
- Esri export (sat.py) gave HTTP 500 at small half-widths. satz.py z18 works; z19 here is "Map data not yet available".
- The Overpass private.coffee query hung for 120 s+ and was killed (not needed).
- dry run: 0 "!!"
