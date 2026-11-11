# Alberta notes from p3-382 (2026-11-10), adding to kit/ab/ALBERTA_NOTES.md

- Alberta Parks booking: use platform "operator" + the shop URL (the provincial:AB row's label), not "reserveamerica".
  The page's "Reservations can be made 90 days in advance" -> booking.window_opens_days 90.
- Seniors-discount line: absent on Bow River 8818, Bow Valley 8817 and Castle Falls 8847.
- Kananaskis (Bow Valley PP) "Information:" phone is 1-866-686-0339; facility operator Cedar & Spruce Campgrounds.
- Castle PP shop parkId 330291: Castle Falls = 45 unserviced sites, 25-70 ft, 5 pull-through, none tagged Near Water.
- Wayback responses can arrive zstd-compressed: `zstd -d -c file`.
- Let's Camp (letscamp.ca) and Park With Us (parkwith.us) booking pages: the site map is an SVG; render it with
  playwright (svg2png.py with an HTML wrapper). Both are booking channels -> platform "operator" with the URL.
- Wix sites keep rate tables in "Table Master" iframes: bwf.py OUT URL dumps every frame's innerText.
- Canyon Creek 9109: canyoncreekgolf.ca is dead (BunnyCDN placeholder); new site canyoncreekgolfandcamping.com.
- Centennial RV Park 12796 (Fort McMurray): its domain 301s to Facebook; no rate anywhere (Travel Alberta/FMWB
  listings only). Country Roads 9124: rates.html posts the year's rates; booking parkwith.us/camps/country-roads-rv-park.
- gm.py lands on the wrong place for common names; add the street address or postcode to the query.
- Esri export (sat2.sh) fails at small half-widths; use 200 m or more and crop.
- curl -k is refused by the classifier; never weaken TLS (try plain http or Wayback instead).
