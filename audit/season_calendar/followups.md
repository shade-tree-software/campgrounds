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
