# Splits: 5392 Lake Bronson, 5425 Zippel Bay (2026-11-11)

Sources: the DNR record (maps.dnr.state.mn.us feature_detail id=spk00208 / spk00284; dumps in dl/bronson.json, dl/zippel.json),
the DNR park map PDFs (spk00208.pdf 2025, spk00284.pdf 2024; renders in dl/, dlpdf/), and the ReserveMN UseDirect API
(mnrdr.usedirect.com MinnesotaRDR rdr/search/grid, search/details/{unit}, fd/facilities). Per-unit amenity dumps are dl/am<facility>.txt
(name|unittype|web|rate|pad|pull/back|amp|WaterFront|Lake/River/Creek|shade|dist showers|dist dump|lat|lng), all for the night of 2027-08-15.
Imagery: Esri World_Imagery with the ReserveMN unit points plotted (img/ls_esri_pts.jpg, img/tr_esri_pts.jpg, img/ang_esri_pts.jpg),
USGS ImageryOnly at full pool (img/ls_usgs_pts.jpg). All of them rendered. Elevations are from Open-Meteo.

## Lake Bronson (5392): SPLIT
- Facilities: 758 Lakeside (48 units: 42 electric 1E-41E,43E,44E at Amp 50 and $34; non-electric 42, 45-48 at $24; CH10 is the camp host; OF1 is an overflow unit without coordinates). 897 Lakeside Extension (13 electric 50E-62E at Amp 50 and $34; 50E-55E pull-through 45-120 ft; 56E-62E back-in 35-45). 842 Two Rivers (96 units: 82 Drive-In at $24, 12 Electric at 30 A and $34 including H158, 2 equestrian at $24; all back-in; pads 30-60).
- 47 + 13 = 60 public Lakeside sites; 60 - 5 non-electric = 55 electric. With Two Rivers' 12 that makes the DNR's 67.
- Lakeside and Extension: AllowWebBooking false, and no 2027 SeasonDates (closed). Two Rivers is in season 2027-05-14..10-24.
- Distance: the Lakeside centroid 48.72264,-96.62558 to the Two Rivers centroid 48.72598,-96.60350 is about 1.65 km. Each has its own road (DNR map). That meets the split rule.
- Waterfront for Lakeside:
  - ReserveMN flags 'Water Front: Yes' on 37E-41E, 45 and 46.
  - On the Esri frame (0.244 m/px) the south-edge sites are 7-13 m from the grass/exposed-lakebed line, the east edge 13-22 m and the west edge 17-20 m.
  - Site 42 is on the south edge but not flagged; I included it by imagery.
  - Full-pool USGS imagery shows water on three sides of the point.
  - Dam check: site 45 DEM 296 m equals the lakebed DEM 296 m.
  - Call: LAKEFRONT, with the caveat in the note naming 37E-41E, 42, 45 and 46.
  - Judgement call: the east-edge sites face an inlet with day-use fishing piers (now removed). Only a footpath lies between those sites and the water.
- Waterfront for Two Rivers: no site is flagged; all sites are in continuous woods; water is 130-170 m away through forest. NOT WATERFRONT.
- Parent season: removed. Its source was 842, and Lakeside has no dates.
- Dump: at the park office near Lakeside (DNR map) and outside the closed area. Marked true on both entries because it is the same park.

## Zippel Bay (5425): SPLIT
- Anglers (888): 16 sites, #42-57, 'Standard Back In' at $24, AllowWebBooking true, pads 30-60 (54 = 60 ft, 55 = 45 ft, the rest 30-40).
- The Angler's inset on the DNR map shows its own loop road with a hand pump and toilets, off the ranger-station-to-marina road. So Anglers has its own road and RV sites a 23-ft rig fits, which allows the split.
- Distance: Anglers centroid 48.85454,-94.86007 to the Ridge centroid 48.85727,-94.83913 is about 1.56 km.
- The DNR's "not past Ridge" advice applies to the eastern road, not to Anglers.
- Eastern loops: Birch 1098 (16 sites, 22-40 ft), Ridge 1099 (14 sites, 20-40 ft), Lady's Slipper 757 (11 sites, 24-36 ft). Centroid of the 41 sites: 48.85936,-94.83720.
- 2027 season for all four: 04-16..11-03.
- Showers and dump are at the ranger station (DNR map), shared by both entries.
- No electric anywhere.
- Waterfront: no 'Water Front' flags. Anglers is under canopy with no water in a 500 m frame. NOT WATERFRONT for both.
- The DNR uses no collective name for the three eastern loops, so 5425 keeps its name.

## Not done / unread
- Nothing refused.
- The Lake Bronson GeoPDF insets are not georeferenced, so I used the ReserveMN map points instead.
- No RV Life rating was given to the new entries, because the park rating stays on the parent.
