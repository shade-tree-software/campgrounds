# Alberta notes from p3-377 (2026-11-10)

## Let's Camp (M.D. of Bonnyville parks)
- `curl -H "X-Tenant-Type: camp" https://letscamp.ca/api/camps/<slug>?locale=en` gives keys `camp` and `metaData`.
- `/api/camps/<campId>/sites?locale=en` returns a dict whose `sites` key holds the list, not a bare list. `lcsum.py` in p3-377 summarises it.
- Out of season there are no prices (null minimumPrice), and the price-model endpoints 404.
- Cold Lake M.D. Park posts no rates anywhere; its bylaw 1864 has penalties only.
- M.D. of Bonnyville parks line: 780-826-2245.

## PitchCamp (Coyote Creek, Sundre)
- `app.pitchcamp.me/campground_availability_search?campground_name=<code>` is an SPA.
- With bwnet2.py (it captures every XHR/fetch, not just `/api/`), the body text shows policies and minimums.
- `api.pitchcamp.me/api/api.php/auth/get_system_parameters` has no site types or rates while the park is closed for the season.

## Campspot
- `campspot.com/book/<slug>` returns 403 to curl but loads in the browser helpers (cs1/cs2).
- A cs2 type quote lists the site names of each type. Drayton Valley shows only 4 of its 42 RV sites, which is a nightly-share signal.
- Drayton Valley's booking moved from elevatedexperiencecamping.com (now dead) to Campspot (`drayton-valley-camp`, park 5987).

## TLS failures where http works
- Two operator sites fail https with a certificate-name mismatch but answer 200 over http: diamondgrove.ca and elbas.com.
- Store the http URL.

## Alberta Parks shop
- Year-round campgrounds show "Status: Open year round." or "Open through <date>" rather than "Closed through".
- Crimson Lake: "Open through Tue May 11 2027".

## Internet Archive
- The Wayback CDX/id_ endpoints were down mid-run ("Internet Archive services are temporarily offline"). Treat that as UNREAD.
