# Criteria follow-ups from phase 7

Entries a verifier found may fail the inclusion criteria. I decide these (standing rules let
me drop and report); each needs the research named before a verdict.

- **14312 James Creek RV Resort (PA)** — $50 base rests only on our own note; RJourney blocks
  plain HTTP and showed no rates with the park closed. Re-quote when 2027 booking opens.
- **525 Grindstone (VA, USFS)** — closed for 2026 (no reopening date). `booking.reservable: true`
  came from note prose, but every rec.gov rate season since 2022 is "First-come, First-served"
  with walk-in prices. Re-check booking when it reopens; the USFS page currently 404s.
- **940 Tall Pines / Chesapeake Bay KOA (VA)** — possibly mostly seasonal, on secondary evidence
  only: a 2026-10-10 camper review on koa.com says "the cg is almost all seasonal/fulltime. There
  is one section remaining that is transient." The family has stayed (--AWH). Needs the operator's
  own word (site map / call) before any verdict.
- **474 Big Bend boondocking sites (VA, GW NF)** — the forest's dispersed rules say "Dispersed
  camping is not allowed in the vicinity of developed recreation areas such as campgrounds,
  picnic areas, or trailheads" (fs.usda.gov/r08/gwj/recreation/camping-cabins); the spot is a
  former picnic area that is now an overlook, and the site details rest on TMBtent/boondocking
  listings. Needs the ranger district's word (540-432-0187) on overnighting there.
- **255 Bath County Recreational Campground** — kept by AWH 2026-10-11 as an FCFS utility area with
  no posted fee; p3-20 found no official site count, size limit or rate either (DWR: "Primitive
  Camping Only", "a small fee"). Stands on AWH's call.
- **476 Crooked Creek WMA** — one of its two parking areas is "near the old concession building";
  DWR's 300-ft rule (building/boat ramp) may bar camping there. The East Fork lot is unaffected.
- **763 Burton Family Farm (Hipcamp)** — kept: sites 1, 3 and 10 are 2WD; Hipcamp marks 6, 8, 9
  "four-wheel drive recommended" (note says so). Not the access road, so not the Rapidan case.
- **478 Hog Camp Gap** — GWJ rules bar dispersed camping "in the vicinity of developed recreation
  areas such as ... trailheads"; the FS Mount Pleasant trailhead parking is ~0.25 mi past the gap.
  No FS page bars the clearing by name; widely used. Kept.
- **8 Fauquier Horse & Campground (Hipcamp)** — listing contradicts itself on hookups (overview:
  "hookups for water and electricity"; lakeside site text: 4 x 30A + 8 x 50A; amenity flags: no
  electric, no water). Left as AWH's note had it (no hookups). Host question.
- **447 McClintic Point** — every site listed at 21 ft, and the FS says "All equipment must fit on
  the space provided"; under the ~23-ft floor. Kept on AWH's own note ("will probably handle a few
  feet more"). Its two pages disagree on drinking water (rec.gov seasonal; FS none).
- **1108 Jamison Mill** — ownership federal -> local (Franklin County runs it on Corps land; same
  as Glen Lyn). Now county-reservable; the old FCFS/USACE claims were wrong.
- **239 Oronoco** — Modern Campground (2023-10-01) reported a GWNF proposal to make it a $14 fee
  campground with water and marked sites; no official page says whether it was adopted. If it
  was, the $0 fee and dispersed rules are stale. Inclusion rests on Campendium alone. Call the
  Glenwood-Pedlar district (540-291-2188).
- **472 The Pines / 237 Walnut Flats** — FS says only "small recreation vehicles can be
  accommodated", no length; 23-ft fit unconfirmed.
- **759 Seven Islands (Hipcamp)** — $54 base, over the $50 gate; AWH added it, so kept.
  **761 Private Paradise** is $46.75 only under a 15% discount (list $55).

## Resolved 2026-10-21
- **436 Thompson Lake Parking Area** — DWR 300-ft rule: satellite 2026-10-21 puts the pin in
  woods ~250 m east of the lake, nowhere near the ramp; no problem.
- **Long Run Road #1-#6 (520, 519, 522, 56, 57, 58)** — DROPPED under the 4WD rule: DWR's FR 72
  page says the road "is recommended only for 4-wheel drive vehicles with high clearance".
  **521 Western-Facing Campsite** (0.5 mi up FR 72C off FR 72) dropped on the same page.
- **13090 Lonesome Pine RV Park (VA)** dropped (criteria_drops.py): no website, Facebook behind a
  login, Google 16 reviews, no rate (RV Life's $ is a ~$1 placeholder).
- **15518 Richmond North / Kings Dominion KOA** kept: base $35 (November weeknight); weekends and
  season run $71-150, and it is 34 km from Richmond (gateway).
- **1131 Parkview RV Park** kept: static 2022 site with no rates, phone; RV Life $$ is the price indicator.
- **13095 Jubilee Park and Horse Show Grounds (VA)** dropped (criteria_drops.py): login-walled
  Facebook only, no operator rate, Google listing (43 reviews) has no phone.
- **894 Chincoteague Bay RV Resort** kept: base $59 ($49 + $10 resort fee) is over the gate but it
  sits 4 km from Chincoteague/Assateague (gateway). Campspot's record still points at a Sun Outdoors
  URL, which now lands on Sun's Virginia index without it (Sun lists only Jellystone Chincoteague);
  the operator site is "Blue Water" - a past Sun affiliation, not a current Sun park.
- **1140 Glen Maury Park** rates ($70 W/E, $55 tent, 2026 page) are high for a city park and rest on
  one page; earlier city/news pages said $35-40. Kept as posted.

- Dropped (audit/verify/criteria_drops.py, logged in removals.json): **1168 Lake Bonin** (long-stay
  test 2: "focus on seasonal sites", daily rates only by call/email, nothing posted, no booking
  site), **13118 Valleyview Farm** (domain parked, booking host gone, no Google listing at the
  pin), **1164 Frey's** (Facebook only; Google listing has no phone; no posted rate - AWH's
  2026-10-11 drop class), **1188 Woodhaven Acres** (site has no phone/rates/booking; Google 5 reviews).
- Kept: **4375 King's RV Park** (own site kingsrvcampground.com found via Google: $35 nightly,
  phone; website added, fees corrected - the $45 was King's Campground in Dillsburg PA),
  **1181 Shady Rest** (Google open, 139 reviews, phone 570-222-2365 added), **13113 Sunvalley**
  (Google open, 69 reviews, phone matches), **1136 Cavitts Creek** (local; Google 237 reviews,
  phone 276-988-7250 confirmed), **14277 Fire Pit** and **14278 Pine Lane** (both pass the five
  long-stay tests: 2026 nightly rates posted + phone, no standing minimum, no site count; Fire
  Pit's note now says it is mostly seasonal), **1104 Breaks** (the park page does not say its
  $27 primitive sites are tent-only; Firefly is behind reCAPTCHA, so the stored base stands).
- **14267 Harts Content** kept: a live ParkWith booking page sells RV sites (price + presence);
  fees.checked corrected 2026 -> 2023 (the table is titled "2023 Rates").
- **14274 Ledgedale** kept: posted nightly RV rate + phone, the waitlist is for SEASONAL sites
  only; the rate page is undated and its holiday dates fit 2022, so fees.checked -> 2022 and
  inclusion_evidence corrected. Re-check for a current rate when the 2027 season is posted.
- **1147 Washington County Park** closed: it is a LOCAL park (county park authority), and the
  long-stay five tests apply to private parks only.
- **13087 Amelia Family Campground** kept: the verifier found the operator site stale (newest post
  2020, no rates); Google listing active, 159 reviews, phone 804-561-3011 matches - the same state
  AWH kept it in on 2026-10-14 (own site + phone + RV Life $$).
