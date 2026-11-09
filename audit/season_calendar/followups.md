# Season pass follow-ups

- 5210 Little Coon Creek (Gillham Lake): `booking.reservable: true`, but the recreation.gov
  rules list reservationCutOff "Not Reservable" and a notice says campers register with the
  Big Coon Creek park attendant. Check booking (chunk 03). USACE swl site is a bot wall.
- 5199 Arrowhead Point, 5210: no agency season found (USACE mvk/swl pages 403); calendar
  season left as is.
- 5905 CCC (Dakota Prairie, ND): `booking` absent, but the FS page lists 6 single + 3
  group + 1 equestrian sites reservable on recreation.gov (chunk 04).
- 5906 Buffalo Gap (ND): FS page says 5 sites reservable; the note says 12.
- 5488 Onegume, 5473 Flour Lake: pages say some sites first-come; `booking.fcfs` absent.
- Booking (audit/booking_recgov/past_months.json): 5183 Mill Creek (Greers Ferry) showed
  Reserved nights on only 2 of 36 sites and 12070 Curly Jack on 2 standard sites (note says
  individual sites FCFS, groups reservable) - left not reservable. 6478, 6505, 6511, 10331,
  11905, 11908, 13272 showed no booked night Jul-Oct 2026 - left as is.
- 6405 Nash Fork, 6443 Brooklyn Lake: FS pages post a 22-ft trailer limit (22 ft does not
  fail, AWH 2026-10-20); 6405's note says RVs to ~25 ft.
- 6510 Vedauwoo, 6467 Fremont Lake: pages describe first-come sites; `booking.fcfs` absent.
- 6414 Ryan Park, 6476 Hog Park: open in winter with no fees or services, as road access
  permits; season left as the serviced span.
- 6488 Libby Creek Willow, 6495 North Fork: no agency season stated (chunk 05).
- 7993 Elephant Rock, 7994 Columbine, 9518 Pine Flats, 9520 Mountain View: rec.gov lists
  first-come sites; `booking.fcfs` absent. 8037 Water Canyon: reservations 03-15..11-30,
  open year-round (booking.season candidate). 8021 Agua Piedra: no season stated (chunk 06).
- 9651 O'Hara: FS page contradicts itself (Current Conditions "april 17 ... 10/3026" vs Seasons
  of Use "May 12 - September 18"); calendar season left. 9619 Upper Payette Lake, 9760
  Huckleberry: no stated season. 9556 Hower's, 9898 Devils Canyon: notes carry closures the
  pages no longer show. 9552, 9553, 9556, 9662: first-come sites, `booking.fcfs` absent.
  9934 King's Bottom: website links the group-site facility (10362432) (chunk 07).
- 9952 Maple Grove: booking says reservable:false / fcfs always, FS page says some single
  sites reservable; website is a dead recid URL. 9984 Renegade, 9985 Aspen Grove, 10017
  Shady Dell: fcfs absent (generic rec.gov FCFS notice). 9997 Green River: note has the
  reservable/first-come loops swapped (NPS: A+B reservable, C first-come). 9944 Big Bend
  (BLM): no season; facility 251842 is the 3 group sites only (chunk 08).
- 10073 Anderson Cove: FS page gives peak 4/24-10/31, first-come 11/1-12/31 and a "Winter
  Non-Peak Season 01/01-4/23" (rec.gov prices a winter site), yet also says "open
  seasonally"; chip left at 04-24..10-31 (year-round?). 10673 Cinder Hill (from 09-27),
  10677 Fall River (from 09-17): first-come only late season, not in `booking`. 10272 Johnny
  Creek: pages say first-come only, booking says reservable/some_sites. 10337 Bonaparte
  Lake: FS page 404. 10272, 10286, 10294, 10337: no stated season (chunk 09).
- Deschutes (chunk 10): 10678, 10679, 10686, 10704, 10733, 10743, 10755 go first-come only
  from Sep 27 to their close (booking.season candidates); 10703, 10745, 10747 Metolius are
  year-round with reservations ending Oct 17.
- Chunk 11: 10756, 10860, 10862, 10863, 10864, 10969 (Deschutes) first-come Sep 27 to Oct 18,
  not in `booking`. 10863 Little Crater: FS max spur 40 ft, note says ~30 ft. 11235 Timber
  Creek NV: rec.gov facility is the 5 group sites, says singles are first-come; FS says
  reservations generally required — booking unclear. 10763 Diamond Lake: rec.gov "All sites
  are available by reservation only" vs fcfs some_sites; no stated season.
- Chunk 13: 11364 Schoolhouse set temporarily_closed (lake levels) + year-round; page states
  the reservation window two ways. 11369 Spillway: FS page "small motorhomes up to 16 foot
  are allowed" vs rec.gov "no RV/trailer over 32' recommended" vs note 25-42 ft — fit unclear
  (AWH: under ~20 ft = out). 11370 Aspen: page 55 first-come sites, note 27. 11350 Luna Lake:
  FS gives only "May 15" (close dropped). First-come sites/periods missing from `booking`:
  11350, 11363, 11369, 11373, 11386, 11388. 11388 Grayling: no stated season.
- Chunk 14: notes cut — 11373 ", open about May-Oct", 11389 "; open ~Apr-Nov" (FS: Apr 1-Oct 31),
  11418 "open ~mid-May to mid-Sep, " (the Sep edge was the calendar's; FS states no close).
  11395 White Horse Lake: FS max length 38 ft vs entry 45; FS 94 single sites vs note 77 + 10
  doubles. 11895 Rocky Rest: page states Apr 17-Oct 15 AND Memorial-Labor Day (left).
  11915 Merrill: close given two ways (left out); 45 walk-in sites. 11435 Dairy Springs: FS
  "Early-May to mid-October". First-come sites/periods missing from `booking`: 11389 (Apr 1-14
  all first-come), 11395, 11849 (reservations late spring-early fall only). No stated season:
  11397 Winn, 11865 Minersville.
- Chunk 15: 13291 Lower Onion Creek (BLM): rec.gov facility 255118 is GROUP SITES ONLY, so its
  02-10/11-30 chip is the group window; the 21 individual sites are first-come only (entry says
  fcfs some_sites). No stated season — chip left, but it is not the campground's season.
  12177 Ice House: page gives "May - October", "Memorial Day Weekend and mid-October" and a dated
  Oct 11, 2026 closure (used Memorial Day / Oct 11). 12104 Loganville: close stated as Oct 15 AND
  Labor Day (close left out). 12101 Indian Valley: Apr 17-Oct 15 AND Memorial-Labor Day (left).
  11956 Spring Creek: FS 16 reservable vs rec.gov/note 12. 12205 Frenchman: 17 of 38 reservable,
  booking lacks fcfs. 12204 Grasshopper Flat: 33 of 71 reservable.
- Chunk 16 (last): 13292 Upper Onion Creek (BLM): no_source. rec.gov 251835 is the GROUP SITE
  facility (Group A and B only), so the 02-10/11-30 chip is the group window; BLM: the 14
  individual sites are first-come only, so `booking.reservable: true` / fcfs some_sites describe
  the group sites. Same pattern as 13291 Lower Onion Creek. PASS COMPLETE: 151 of 151 read.

## Worked 2026-11-08 (51 entries; script kept in the session scratchpad, sources in each `provenance.booking`)
- `fcfs: some_sites` from the agency/rec.gov text or the RIDB catalog's unreservable public sites:
  5473 6510 6467 7993 7994 9518 9520 9552 9553 9556 9662 9985 11363 11373 11388 11395 11849
  12204 12205, and 5905 (booking was absent) and 9952 (was reservable:false/always; website
  moved to the r04 page). 11386 also gets booking.season 11-01..03-15; 11389 04-15..10-31.
- 5488 Onegume: `after_cutoff`, reserve_until 96 h before arrival, booking.season until 09-27.
- Deschutes first-come-late-season: booking.season `closes` the day before first-come starts
  (09-26; 10677 Fall River 09-16) on all 15. Metolius 10703/10745/10747: booking.season until
  10-17 (calendar). 11369/11370: booking.season from the calendar edges.
- 10272 Johnny Creek: reservable false, fcfs always. 10763 Diamond Lake: fcfs never (rec.gov
  "All sites are available by reservation only"); the note's loop split cut.
- 13291/13292 Onion Creek: reservable false, fcfs always (individual sites; groups only on
  rec.gov); the group-facility season REMOVED (unknown), recorded in curation_note.
- Sites: 10863 max rig 40 (FS spur), 11395 count 94 / max rig 38 (FS). Notes cut where they
  contradicted the agency: 5906 (12 reservable), 9997 (loops; booking.note now says A+B
  reservable, C first-come), 11370 (27 FCFS), 11956 (12 reservable), and the late-season FCFS
  phrases the booking.season now carries.
- LEFT: 5210 (USACE bot wall; reservable vs "Not Reservable"), 11235 Timber Creek (FS
  "reservations generally required" vs rec.gov singles first-come), 8037 Water Canyon (FS
  reservation season Mar 15-Nov 30 vs rec.gov "First Come First Serve season of October through
  March"), 9662 Powell reservation dates (2024 only), 10073 Anderson Cove (AWH).
