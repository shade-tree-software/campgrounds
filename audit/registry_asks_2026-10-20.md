# Questions from the policy-registry pass (2026-10-20) — ANSWERED by AWH 2026-10-20

Answers: 1 a trailer limit applies to a motorhome too unless the source says otherwise (20-ft
FAS dropped); 2 drop; 3 read the SEPAQ page once (done: `provincial:QC`); 4, 5 drop; 6 wait for
RIDEM's new reservation provider; 7 drop; 8 keep Hackberry Bend 6626, drop Pioneer 6621; 9, 10
drop. Removals are logged in audit/drops_2026-10-20/removals.json.

1. **Montana FAS trailer limits.** FishMT's site pages post a "Vehicle Length: Trailer Length
   is N ft" for fishing access sites. Of the 26 pages that loaded (the site is flaky; 49 still
   unread), 11 say 20 ft, 6 say 25 ft, the rest 28-48 ft; earlier reads also had Valley Garden
   6098 at 25 ft and Chief Looking Glass 6088 at 28 ft. EKKO is a 23-ft motorhome, not a
   trailer. Does a posted 20-ft *trailer* limit exclude us under the min-site-length rule, or is
   it about towed units only? Until answered nothing is dropped. (Every posted stay limit read
   was "Maximum stay of 7 days", which the state:MT row already carries.)

2. **Whiteshell "Falcon Creek Campground" (9363).** Not on Manitoba Parks' 2026 operating
   dates, its goingtocamp catalog, or the Whiteshell campground-map list; Toniata Beach (the
   only other Falcon Lake campground) is at the east end of the lake. The pin, 2 km west of
   Falcon Beach Campground, shows a small loop of cabins and trailers. Probably an RV Life
   phantom or a private/organisational camp. Drop it? (Note carries a dated caveat meanwhile.)

3. **Quebec (SEPAQ) row is on hold.** SEPAQ's booking terms (sepaq.com/reservation/modalites/
   camping.dot) answer 403 to curl and to web fetchers, and article 2 of its site terms forbids
   "un robot, araignée ou autre dispositif automatique ... afin de contrôler ou copier les pages".
   The headless-browser driver would get through, but that is exactly what the clause names, so I
   stopped. (The 2026-10-12 price research read its booking site with that driver; worth knowing.)
   Options: you open the page and paste the reservation/cancellation/stay rules, or give the OK
   to read that one page with the driver, or skip `provincial:QC`.

4. **Drop Golden Memorial State Park (5002, MS)?** MDWFP's own park page now says it "is managed as
   a day use park only" (questions to Roosevelt SP). The Dyrt and Campendium say the same. Marked
   `temporarily_closed` with a dated caveat for now; with no overnight camping it fails inclusion.

5. **Drop Holmes County State Park (5004, MS)?** It is gone from MDWFP's list of state parks (its
   page 404s) and from the reservation site's catalog; eRegulations lists it closed for
   renovations and MDWFP lists its lakes closed. Campendium says permanently closed. No transfer to
   the county turned up. Marked `temporarily_closed` with a caveat; drop, or keep and wait?

6. **Rhode Island peak-season minimum stays (state:RI, 4 entries).** The ReserveAmerica park pages
   say "See full policy for Minimum Stay requirements", and that policy is on riparks.ri.gov, which
   answers every automated read with a Cloudflare challenge. The row leaves `min_stay` unknown.
   If you can open riparks.ri.gov/campgrounds/camping-policies and paste the minimum-stay section,
   I'll add it. (2027 bookings are also on hold while RIDEM changes reservation provider, so this
   may be worth waiting for the new vendor's terms anyway.)

7. **Little Blue / Disney Area at Grand Lake State Park (6617, OK) may now be tent-only.** TravelOK's
   page (read 2026-10-20) describes "30 primitive tent camping spots" and lists only tent sites; the
   entry was added for ~18 developed sites including roadside RV spots with electric. Nothing on
   ReserveAmerica. Drop as tent-only, or keep with a caveat?
8. **Beaver Dunes Park's Pioneer Campground (6621, OK)** sits beside the OHV dune-riding area with
   "direct access to the dunes", i.e. close to an OHV staging camp, which your 2026-10-02 rule puts out
   of scope; Hackberry Bend (6626) is the lakeside loop of the same city park. Keep both, keep only
   Hackberry Bend, or drop both? (Both are now `local`: the city took the park over from the state.)
9. **Busiek State Forest and Wildlife Area (13827, MO) may be walk-in tent camping by permit.** Its
   MDC page (read 2026-10-20) says "Visitors will find eight primitive, walk-in tent campsites.
   Camping is permitted ONLY with a permit" (Southwest Regional Office, 417-895-6880). The entry was
   added on the 'Individual Campsites' tag and 2 GIS camping points at drive-in lots. Drop, or keep
   with a caveat? No season written until you decide.
10. **Little Indian Creek Conservation Area (13903, MO)** now posts a notice "Camping is allowed by
   permit only and requested 10 days in advance" (636-441-4554), while the same page's area
   regulations also say "Camping is prohibited." Keep with a permit caveat, or drop? No season written.
