# p3-403 Alberta notes (2026-11-11), the last AB batch: 8885 8886 8965 8966 15392 8852 8870

## Sources and recipes that worked
- West Fraser FRMA pages: https://www.westfraser.com/responsibility/recreation/frma/campgrounds/<slug>
  (kinky-lake-campground, wildhorse-lake-campground). Plain curl works. h2t.py output, around lines 912-935, carries
  the reservable/first-come split, "Reservations recommended but not required", fees ("$25/night. $10 reservation fee.")
  and "Reserve contact: Fox Creek Development at 780-865-2154". Written as platform phone, fcfs some_sites,
  reservation_fee 10, policy_ref none candidate (same as 8904/8910/8964).
- Switzer PP shop parkId 330112, Woolford PP 330317. gis.py (SLUG PARKID LIST.json LOOPREGEX) pulls campsiteDetails
  per site: Site Length, Max Equipment Length, GIS lat/lng. The "NR-" first-come placeholders carry no GIS or lengths.
- Cache Lake: every site on the shop shows "Max Equipment Length (ft): 20" (pads 28-67 ft). Not a park default,
  because other Switzer loops run 20-61 ft. Flagged as a fit drop candidate; max_rig_ft 20 written.
- Graveyard Lake and Halfway share the directions text "Many sites back directly on to Jarvis Creek." Neither has a
  site map with numbers (the Gregg tear sheet is a park overview), so both stay not waterfront with the lead described.
  Graveyard's page says "Season: Year-round" (winter: first-come, $5 less, limited maintenance).
- Stavely Elks (Wix) campground map: static.wixstatic.com/media/7c3e78_24e9c3fad7144c7e8cc6469506dad096~mv2.png,
  which numbers sites 1-54 plus Group A/B.
- gm.py needs PYTHONPATH=~/.cache/ekko-pw and NO -I (it is our own script):
  `PYTHONPATH=~/.cache/ekko-pw flock /tmp/ekko-headless-browser.lock python3 gm.py "..."`.
- sat2.sh fails at half-widths around 120 m. Take 200 m and crop with crop.py.
- Esri Wayback (wb1.py) returned black tiles at z18 for the Kinky Lake releases tried. Not useful here.

## Seniors line
Present: Kinky Lake 8885, Cache Lake 8965, Graveyard Lake 8966, Halfway 15392, Woolford 8870.
Absent: Wildhorse Lake 8886. Not applicable: Willow Creek 8852 (municipal, Elks-run).

## Phones
- West Fraser campgrounds: 780-865-2154 (FCDA).
- Switzer: the page gives the general line 1-877-537-2757; Switzer VC is 780-865-5600; the Cache tear sheet gives
  780-865-5600 (Summer) or 780-865-8395.
- Woolford: page 403-394-0150 vs tear sheet (Jul 2026) 403-381-5745.
- Willow Creek: 403-625-6239.
