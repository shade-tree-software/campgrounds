# Alberta notes, p3-385

- nightly_low AND nightly_high are both the BASE rate (cheapest plain site a 23-ft motorhome fits; schema doc ~line 427). Other tiers go in surcharges / fees.note. Fixed 8875, 9086, 9141 after first writing the top tier.
- Alberta Parks pages: plain curl (ab.sh) gives advisories, Information phone, the Season line, the rate table, amenities, `destination=lat,lng` and the tear-sheet PDF. Advisories can carry odd "Updated" dates (Miquelon showed "Updated: May 23, 2027").
- shop.albertaparks.ca: ralist.py SLUG PARKID OUT.json then rasum.py OUT.json '.'; the first page shows "Status: Open year round" / "Open through".
- Pinehurst Lake (8999): the Seibert Lake road warning on the Lakeland PRA pages is NOT for Pinehurst. New dump station under construction Sep 8 2026 - Apr 30 2027.
- Kakwa River PRA (8961): stored pin was off by exactly 1 deg latitude.
- Magrath Jubilee (9086): bookings via the town's ActivityReg page; both stored URLs 404.
- Let's Camp API: https://letscamp.ca/api/camps/<slug>?locale=en with header `X-Tenant-Type: camp` (siteTypes, minimumPrice, settings, metaData.maxRVLength).
- Good Sam engine: GraphQL at https://api.campgroundreservations.com/graphql (gsq.py).
- Lost Lemon (9075): rate tables are escaped HTML inside the page; html.unescape twice. Campspot answered "Park is closed" for Nov-Apr nights though the operator says year-round; its C$63 power/water type is a 22-ft van-only site.
- Louie Lake (9097): Campspot park 3747 uses age categories ['Children','Adults'] (guests0,2); the availability call returned an empty list, then CORE-0 errors. Operator rates page is plain HTML.
- Parks Canada Jasper: camping page /pn-np/ab/jasper/activ/passez-stay/camping has the 2026 season table; fees at /visit/tarifs-fees ("with fire pit" rate = no-fire-pit rate + C$13.75 fire permit).
- Nominatim/Overpass did not answer on 2026-11-11 (empty bodies).
