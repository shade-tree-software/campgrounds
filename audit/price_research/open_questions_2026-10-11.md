# Price pass - open questions for AWH (2026-10-11)

What the 685 -> 405 pass could not settle on its own. Each line names the entry ids.

**AWH answered 2026-10-11:** Colorado SWAs $40, with the details spelled out (`co_swa.json`);
GW and Monongahela dispersed sites free (`gw_mon_dispersed.json`); every "probably drop" entry
dropped (`dropped_2026-10-11.jsonl`); accept the note prices (`note_prices.json`, 108 of the 110 -
1459 gives only a surcharge and 14683 only a weekly rate), kept re-checkable via
`unpriced.py --from-note`. Montana fishing access sites $20 for two (`mt_fas_license.json`). AWH's ResNexus reads:
Birch Coulee $27, Pecan Grove $50 (saved page; then dropped as mostly annual), Big Kandiyohi East no availability (`awh_reads_2026-10-11.json`).
Nakusp C$42.86. River Forks GA $30 from the county's own Itinio page (saved by AWH): its ResNexus link was the
Timberline glamping engine, and 736 was a duplicate of 4638 pinned in SC - merged into 736 per AWH.

## Decisions (one call settles a group)

- **Montana fishing access sites, 31 entries** (`mt_fas_license_only.txt`): no camping fee; each
  site's FWP page lists only the Conservation License ($8 MT resident, $4 senior/youth, $10
  non-resident; annual). Record nightly $0, or a Virginia-style two-person figure ($20 non-resident)?
- **Colorado State Wildlife Areas** - 2268 San Luis Lakes (Mosca), 14478 North Cove (South
  Republican): no camping fee published; everyone 16+ needs an SWA pass ($10/day, $43.87/yr) or a
  hunting/fishing licence. Virginia-style two people, one night = 2 x 2 days x $10 = $40?
- **13 national-forest dispersed sites** (George Washington and Monongahela NFs: 45, 55, 121,
  397-403, 406, 515, 517): no agency page says "free", but FLREA (16 USC 6802(d)(1)(E)) bars a fee
  for camping at undeveloped sites. Record $0 on that basis?

## Probably drop (criteria failures found while pricing)

- 3267 Tower Hill SP (WI): all 10 GoingToCamp campsites allow Tent(s) only.
- 13591 Sky View (Carter Lake, Larimer Co.): priced only as "Group Electric Pods" ($175-275/night) -
  a group campground.
- 14472 Rocky Top River Ranch (CO): rockytopriverranch.com now serves a slot-gambling spam page; no
  rates anywhere (The Dyrt slug now "banderas-bunkhouse").
- 4943 Gulf Breeze RV Resort (AL): Newbook "RV Sites From $53.00 / night" - over the $50 gate.
- Day-use only now?: 1043 South Shore (rec.gov 234689 = 3 group shelters), 4578 Van Pugh South
  (rec.gov 234670 = 54 picnic sites, renamed "Day Use Facility"), 1708 Andalusia Slough (USACE:
  "roadside style day use area"), 3741 Udell Rollways (FS lists only the day-use area), 5221 Lena
  Landing (USACE lists only an AG&F boat ramp).
- No current agency page: 2353 Byers Creek ("closed, slated for decommission"), 2393 Supply Basin,
  2467 Slumgullion (decommissioned; camping still allowed?), 2494 Ferris Canyon, 3334 Windsor Dam,
  3753 Hungerford Lake family campground (FS lists only the horse camps).
- 14805 Hollywood Bottom (LCRA): LCRA lists 6 free campsites (sleeps 8), no RV mention; the entry's
  note claims $45 RV sites.

## Need a human (blocked to scripts)

- ResNexus engines answer with a human captcha and a "scraping violates our Terms" notice: 13326,
  13329, 14562, 14565, 14707, 14812, 14814, 14867, 14890, 14909, 15070, 15087, 736.
- Firefly captcha: 13388 Escatawpa, 4669 Barrington; 13318 Burlington Bay waits for 2027 rates (by
  2027-01-01).
- 1432 Poke-O-Moonshine (DEC site behind Cloudflare), 4577 Upper Stamp Creek (Bartow rec1 catalog
  did not render), 14683 Clear Creek Station (RoverPass table inconsistent).

## Held / known

- Kansas 6 (revisit after 2026-11-01), TN 9 closed for renovation, WV DNR WMAs (AWH), MO Long
  Branch closed, CA Turlock closed, Leesville South Fork (do not chase).
- 112 of the 308 remaining local/private entries carry a price in our own sweep note (often dated
  2026, read from the operator then) that the operator page no longer shows. Accept those as the
  source, marked as such, or leave them unpriced?
