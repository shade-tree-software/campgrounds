# Alberta notes from p3-376 (2026-11-10)

## Alberta Parks (provincial)
- Each campground page has the table (sites / power / $ / reservable dates / status), the
  amenities list, "Bookings Open <date>", dated advisories, the "Information:" phone, and a
  tear-sheet PDF under /media/<code>/<park>-tear-sheet.pdf (park map + campground map, dated).
- "Season: Year-round" on the page is a campground statement (Carson-Pegasus): a stored
  derived year_round false was wrong.
- The shop (shop.albertaparks.ca, Aspira, contract ABPP) pages every site with
  `python3 -I ralist.py SLUG PARKID OUT.json` then `rasum.py OUT.json '.'`: type, loop, max
  vehicle length, Pull-Through, and "Near Water" tags. The Near Water tags found lakeside sites
  that the stored evidence missed (Carson-Pegasus G144-G147, H170-H175).
- Park ids: Beauvais 330290 (beauvais-lake-provincial-park), Carson-Pegasus 330102
  (carsonpegasus-provincial-park), Chain Lakes 330292 (chain-lakes-provincial-park).
- The shop's park-level "Status: Open year round" is no campground season.
- Winter first-come rates sit in the advisories (Carson-Pegasus power C$30; Beauvais C$28).
- A seniors-discount line appears on some pages ("qualifies for the camping fee discount for
  Alberta seniors" - Chain Lakes); Beauvais and Carson-Pegasus have none.
- Do not write window 90 / max_stay 10 / reservation_fee 12 / GST included per entry: the
  provincial:AB row holds them.

## Local (county / town)
- Yellowhead County campgrounds (Bear Lake etc.) are run by L.O.C.K. Properties, 780-396-9185.
- Beaverlodge: www.beaverlodge.ca fails DNS; use https://beaverlodge.ca/. The campground page
  is /visiting-us/learn/south-peace-centennial-museum-2; the Fees & Charges policy PDF is
  found through the wp-json media search. Campspot slug
  beaverlodge-pioneer-campground-beaverlodge-ab (park 4806); no 2027 dates loaded yet.
- Bow Island Campspot slug bowislandcentennialparkandcampground (park 5563).

## Private engines
- Campspot via cs1.py (in a cs/ subfolder, under the flock). averagePricePerNight INCLUDES
  the park's Campspot reservation fee and any transaction fee (CampN RV: 47.47 = 42 + 4 +
  1.47); compare against the posted rate before calling it the base. Slugs: campinclass
  (park 840), campn-rv (park 1032).
- A Campspot failureReason "There is a 30 night minimum" shows a time-of-year monthly-only
  rule (Camp'n Class Nov-Feb).
- Newbook (Black Sheep Camp): nbd.py URL A1 D1 [A2 D2 ...] sets the jQuery form fields
  (available_from/to "Mon D YYYY", nights, Feet, length 23, Motorhome). Run under the flock,
  output redirected to a file; a Nov 2026 control run proved the dates apply. C$76.65 =
  73 + 5% GST.
- RezExpert: Bow RiversEdge business_code=4884. Google resolves only to its "Sanidump" listing.
- Let's Camp: the sites endpoint returns {"sites": [...]}; Aspen Ridge id 67b8c6eb2e1c498e9d0ce3e5.
- WordPress /wp-json/wp/v2/pages?per_page=50&_fields=modified,link dates a rates page.
- Webflow sites (campinclass.com) have no wp-json; the rates page header ("2027 Pricing")
  dated the rate.

## Waterfront
- Alberta lakeside loops are usually behind a shoreline strip of spruce/willow: measure the
  RV pads, call the trees a screen (view at best).
- Chain Lakes: Loop C west pads ~13 m above the reservoir, ~150-175 m back across open slope:
  lakeview holds.
