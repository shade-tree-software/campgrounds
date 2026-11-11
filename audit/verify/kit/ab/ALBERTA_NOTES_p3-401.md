# p3-401 Alberta notes (2026-11-11)

## Camping pages read
- 8969 Sheep Creek: https://www.albertaparks.ca/parks/central/sheep-creek-pra/information-facilities/camping/sheep-creek/ (stored)
- 8967 Simonette River: https://www.albertaparks.ca/parks/north/simonette-river-pra/information-facilities/camping/simonette-river/
- 8980 Smoke Lake: https://www.albertaparks.ca/parks/north/smoke-lake-pra/information-facilities/camping/smoke-lake/ (+ For-Site leaseholder page)
- 8968 Smoky River South: https://www.albertaparks.ca/parks/central/smoky-river-south-pra/information-facilities/camping/smoky-river-south/
- 8920 Strachan: https://www.albertaparks.ca/parks/central/strachan-pra/information-facilities/camping/strachan/ (+ shop parkId 330233)
- 9009 Sulphur Lake: https://www.albertaparks.ca/parks/north/sulphur-lake-pra/information-facilities/camping/sulphur-lake/
- 8974 Emerson Lakes: stored camping page + https://www.westfraser.com/responsibility/recreation/frma/campgrounds/emerson-lake
- 15659 Swalwell Dam (local): https://kneehillcounty.com/2199/Swalwell-Dam + Let's Camp camp API (slug swalwell-dam)
- 8918 Swan Lake: https://www.albertaparks.ca/parks/central/swan-lake-pra/information-facilities/camping/swan-lake/
- 8919 Tay River: https://www.albertaparks.ca/parks/central/tay-river-pra/information-facilities/camping/tay-river/
- 8944 The Narrows: stored camping page + https://www.rochonsands.net/narrows-fees.html + Rochon Sands PP guide PDF (/media/vjjldszo/, Sep 2026; holds The Narrows map)
- 8993 Thunder Lake: https://www.albertaparks.ca/parks/central/thunder-lake-pp/information-facilities/camping/thunder-lake/ (+ shop parkId 330240, tear sheet /media/4qnft0ar/)

## Seniors line ("qualifies for the camping fee discount for Alberta seniors")
- Present: 8967, 8920, 8918, 8919, 8993
- Absent: 8969, 8980 (leaseholder posts its own 60+ rate), 8968, 9009, 8974, 8944

## Policy row (provincial:AB) contradictions
- 8980 Smoke Lake: leaseholder booking by phone/text, opens Jan 1, C$10.50 fee, monthly/seasonal sales -> policy_ref none candidate.
- 8974 Emerson Lakes: West Fraser / Fox Creek Development phone booking, C$10 fee, 3 days ahead -> policy_ref none candidate.
- FCFS-only (row booking terms moot, reservation_fee 0 written): 8969, 8968, 9009, 8918, 8919, 8944.
- Reservable on the shop, the row's terms agree: 8920, 8993 (pages say "90 days in advance").

## Shop access
- shop.albertaparks.ca now answers curl with a Queue-it waiting room. A headless browser under the
  shared lock gets through after ~40 s. Site rows come from the innerText of campgroundDetails.do /
  campsitePaging.do?startIdx=10k (rabt.py + ratsum.py here); "Closed through <date>" from the page HTML.
