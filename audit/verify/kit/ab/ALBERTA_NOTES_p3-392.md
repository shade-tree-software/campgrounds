# Alberta notes from p3-392 (2026-11-11)

- West Fraser / Fox Creek Development Association campgrounds (Big Berland, Brazeau River, and others
  listed at westfraser.com/responsibility/recreation/frma/campgrounds/<slug>) are NOT on shop.albertaparks.ca.
  Their Alberta Parks page says "managed by West Fraser Mills. Visit their website". The West Fraser page
  posts sites, fees, a seniors rate ($15) and, where reservable, "Reserve contact ... 780-865-2154" with a
  C$10 reservation fee, so the provincial:AB row's shop/window/C$12 fee do not fit. The page text needs
  `<script>`/`<style>` stripped before h2t (the Drupal page is mostly inline JS).
- Alberta Parks directions points (`destination=`) can be well off for small PRAs: Beaverdam (log yard,
  760 m), Big Berland (forest, 950 m). Beaver Lake's stored pin was in the Group Use Area, 1.6 km away.
  Google's place point is a better hint at Big Berland but sat on the river.
- Beaver Lake PRA (shop parkId 330126): most sites are posted at 21 ft; list the ones that fit.
- Parks Canada Waterton: the per-campground page is /pn-np/ab/waterton/activ/camping/camping-belly
  (posts max RV length, FCFS, season). Fees page /visit/tarifs-fees. Plain curl works on both.
- Let's Camp camp bios can carry a prior year's dates (Braconnier Dam: "Tuesday February 25th" = 2025).
- Overpass returned 406 to curl with UA 'Mozilla/5.0' this session; I did not use OSM.
- Advisory index: grep the page for `label: "...(<PARK>)... | Advisory ", category: "Advisory"`.
