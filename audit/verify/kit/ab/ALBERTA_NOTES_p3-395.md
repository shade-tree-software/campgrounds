# Alberta notes, p3-395 (2026-11-11)

Ids: 8856 15009 8903 8904 9069 8857 15393 9053 8905 8939 8906 8991. All twelve pass the apply.py dry run.

## Sources and tools
- **Shadowed or old Esri imagery:** use Esri Wayback. Release 2017-06-14 showed Dutch Creek, which is hidden by shadow on the current WV02 2016 layer. `wb1.py RELEASE LAT LNG Z OUT [R]` builds the mosaic, and release 43291 is the current one. Older releases (14765, 26751, 16245) can 404 at z18; drop to z17 or use 43291.
- **edson.ca:** sits behind Cloudflare and returns 403 to curl and to the headless browser. curl to web.archive.org is bot-blocked too. A Wayback capture rendered in the browser (bw.py, under flock) did work.
- **Edson Lions Park:** books through the Premier campground engine, at online.premiercampground.com/<hash>. No prices are quoted out of season.
- **Let's Camp (M.D. of Bonnyville parks, e.g. Ethel Lake):**
  - Send the header `X-Tenant-Type: camp`.
  - Out of season, minimumPrice and startingNightlyRate come back null, so the rate is UNREAD.
  - Site length and width are on /api/camps/<id>/sites.
- **West Fraser FRMA pages (Fairfax Lake):**
  - They carry this Highway 40 line: "a four-wheel drive or a vehicle with high clearance is recommended" in wet spring. It is a drop candidate for the reviewer.
  - Bookings go by phone to Fox Creek Development, 780-865-2154, with a C$10 fee, so policy_ref stays null.
  - The same office runs Elk River, and West Fraser has no Elk River page.
- **Red Rock Sawmill (Fallen Timber North and South):**
  - Its operator pages answer 200.
  - Single sites book by phone or email from March 1, with a C$12 fee. The shop handles only group sites.
  - Fallen Timber South's page names the OHV staging area and trail access, which makes it a drop candidate. North is FCFS and says "keep OHVs on trailers".
- **FOESA (Elk Creek):** the campground page is https://www.foesa.org/page-1075217.
- **Exshaw Community Association:** the rate sheet is an image, a file named "Rental Rates 01022024LL Revised".

## Alberta Parks pages
- **Two season dates on one page:** the camping table's "Reservable Dates" can differ from the "Season:" heading. On Fallen Timber South they read Apr 30 against May 1. An earlier manual read stored 04-30, so the season group was left out to avoid the manual-overwrite "!!".
- **Fawcett Lake:**
  - The page says "two camping sections ~2 km apart". The January 2026 tear sheet shows one contiguous string of sites, 1-28.
  - The shop lists all 28 sites as FCFS; only the group site is reservable.
  - "Close to the lakeshore" on the page does not meet the gate. On imagery, forest lies 70-130 m from the shore.
- **Seniors line:**
  - Present: 8856, 8857, 8904, 8905, 8906, 8991.
  - Absent: 8903 (free) and 8939.
