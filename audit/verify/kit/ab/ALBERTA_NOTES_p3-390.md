# p3-390 Alberta notes (2026-11-11)

Results written: 8816 8822 9044 8948 8996 8973 8836 8833 8985 8963 9032 9065. The apply.py dry run is clean (12 ready, 12 note rewrites, no "!!").

## Method reminders that worked
- Alberta Parks pages: ap.sh (it exits 1 when the seniors count is 0, which is harmless). For shop sites, ralist.py/rasum.py; pull-through is the "NN Pull-Through" in the length cell.
- Shop site photos: sph.sh SLUG PARKID SITEID TAG produces ph/TAG_u.jpg. Use these for the waterfront views (B-40 Cottonwood, A-30/A-36 Park Lake, E-098 Pembina).
- Let's Camp (Taber, Vegreville):
  - Camp record: `curl -H "X-Tenant-Type: camp" https://letscamp.ca/api/camps/<slug>?locale=en`. This gives lat/lng, phone, bio, settings (min/maxNights, check-in), siteTypes and the map image.
  - Site list: /api/camps/<_id>/sites?locale=en. Each site has a maxRvLength {amount}, electrical, siteTypes as a list of dicts (use the name), and allowedUnitTypes.
  - The map is an SVG on Cloudinary. Insert `f_jpg,` into the upload path to get a JPG.
- Imagery: sat2.sh LAT LNG HALF OUT gives 900 px at HALF/450 m/px.

## Pins to move (recommended)
- 8996 Garner: 54.18166,-111.73814 (~480 m)
- 8963 Rock Lake: 53.46425,-118.24057 (~870 m)
- 8973 Nojack: 53.60995,-115.60170 (~200 m; on the Hwy 16 carriageway)
- 9032 Taber: 49.81238,-112.17003 (~280 m; the stored point is west of Hwy 864)
- 9065 Vegreville: 53.49156,-112.03966 (~180 m; the stored point is on Hwy 16A)
- 8948 Dillberry: optional, 52.584093,-110.009919 (~265 m)

## Waterfront recommendations
- 8836 Cottonwood: pond -> riverfront with a caveat (north-arc A/B sites).
- 8963 Rock Lake: lakeview -> not waterfront.
- 8833 Park Lake: lakeview kept; AWH may upgrade for Loop A unserviced A-24..A-41.
- The rest are confirmed as stored.
