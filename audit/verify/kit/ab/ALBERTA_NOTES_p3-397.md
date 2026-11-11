# p3-397 Alberta notes (2026-11-11)

Results written: 8859 15000 9016 9063 9064 8907 14998 8977 15002 8861 8978 8908. The apply.py dry run is clean (12 ready, 12 note rewrites, no "!!").

## New method notes
- Let's Camp (Smoky Lake County, Hanmore Lake East/West): the camp API needs the header `X-Tenant-Type: camp`. Without it you get 400 "Invalid tenant type".
  - Site records carry `description` (the operator's per-site text, e.g. "Premium Waterfront ... can moor boat to your shoreline"), `minUnits` (group sites need 3) and `allowedUnitTypes` (tent-only sites).
  - Gallery photos: https://res.cloudinary.com/letscamp/image/upload/f_jpg,w_600/<publicId>.
  - With no 2027 dates loaded, nightlyRate is 0 and the availability search returns noSitesFound, so premium prices are unreadable in November.
- Park With Us (HandHills): the camp JSON is embedded in the HTML. Its /api needs a session (401).
- fees.seasonal shape: [{"name","opens","closes","nightly_low","nightly_high"}], not from/to.
- Westward Bound Campgrounds (Clearwater County FCFS PRAs, 855-721-3975):
  - Pages are https://www.westwardbound.ca/<name>-campground.htm.
  - They give the rate, a 16-night maximum stay, self-registration, and ATV restrictions.
  - Harlech and Jackfish Lake both use them.
- For-Site Environmental Services (Iosegun Lake, for the Town of Fox Creek):
  - Reservations are by phone or text from January 1, for 11 named sites only, with a C$10.50 fee.
  - Monthly and seasonal stays are also sold.
  - The provincial:AB row does not fit, so policy_ref none is a candidate.
- Indian Graves moved to shop.albertaparks.ca in 2026 (parkId 330277). Corrals are still booked through Wild Rose (403-651-4235). reservation.albertaparks.ca no longer resolves.
- Harlech imagery predates or hides the loop. Use the Alberta Parks directions point.

## OHV / road flags
- Harlech 8907:
  - "Ride in and stay at campsites 12-17 or stage your OHV camp from this location" (Rail Trail).
  - "Access road is not suitable for large RV units."
- Indian Graves 8861: the Upper Loop has an OHV access trail to the trails south of Hwy 532, and no OHV use is allowed in the campground. A general campground with an OHV side.
- Jackfish Lake 8908: OHV trails are nearby and OHVs must stay on trailers inside the park. Mention only.

## Pins to move (recommended)
- 9063 Hanmore Lake East: 54.2909,-112.5035 (~625 m)
- 8907 Harlech: 52.50226,-115.91460 (~290 m; the stored point is south of Hwy 11)
- 14998 Hidden Grove: 53.6225,-115.7653 (~250 m)

## Waterfront recommendations
- 8859 Greenford: riverfront -> riverview
- 9063 Hanmore East: not waterfront -> lakefront, caveat sites 1, 3, 5, 7, 9, 11, 17
- 9064 Hanmore West: lakefront -> lakeview (the waterfront pads are 3-unit group sites or tent-only)
- 8978 Iosegun: lakefront -> not waterfront
- 8861 Indian Graves: creekside confirmed (Lower Loop)
- 8908 Jackfish: lakeview confirmed
- The rest: not waterfront confirmed
