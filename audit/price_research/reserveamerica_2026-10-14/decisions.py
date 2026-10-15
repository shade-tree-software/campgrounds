"""Per-entry decisions of the ReserveAmerica pass (2026-10-14), read by ra_apply.py. Keys as in
../roverpass_ops_2026-10-14/decisions.py, plus fees_extra (merged into the fees group: nonresident, surcharges).
Read from pages.jsonl (ops_read.py, viewed with ../roverpass_ops_2026-10-14/ops_view.py), ra.jsonl
(ra_explore_prices.py: ReserveAmerica's per-site 'Camping Fees (1 night)' through the one browser, since the explore
pages sit behind an AWS WAF challenge) and ../ra_site_prices.py on the classic hosts.
"""
D = {}
RA = "https://www.reserveamerica.com/explore/"
INYO = "https://www.inyocounty.us/services/parks-recreation/campgrounds/"


def d(i, **kw):
    assert i not in D, i
    D[i] = kw


def cad(lo, hi, text):
    return (lo, hi, text, "CAD")


def nonres(amount):
    return {"nonresident": {"type": "surcharge", "amount": amount, "per": "night"}}


# ---- operator pages and classic ReserveAmerica ----
d(220, act="price", rf=5,
  fees=(68, 78, "ReserveAmerica's quotes for June 2027: electric sites $68 a night, full hookups $73 on a weekday "
                "and $78 on a Saturday (primitive tent sites $38-43). Read 2026-10-14."),
  src=("https://charlestoncountyparks.reserveamerica.com/camping/the-campground-at-james-island-county-park/r/"
       "campgroundDetails.do?contractCode=CHST&parkId=1240020",
       ["Standard Electric 042: $68.00 Per Night (6/15 and 6/19/2027)", "Full Hookup 023d: $73.00 Per Night (6/15/2027)",
        "$78.00 Per Night (6/19/2027)", "reservation fee $5.00"]))
OCONEE = ("Oconee County's posted fees: ${lo} a night for a county resident (${wf} waterfront), ${nlo} for everyone else "
          "(${nwf} waterfront). Read 2026-10-14.")
d(733, act="price", fees=(20, 25, OCONEE.format(lo=20, wf=25, nlo=30, nwf=40)), fees_extra=nonres(10),
  src=("https://experienceoconee.com/park-fees/south-cove-fees", ["Oconee County Residents", "$20.00 - Normal Site",
       "$25.00 - Waterfront Site", "Non-Residents", "$30.00 - Normal Site", "$40.00 - Waterfront Site"]))
d(4381, act="price", fees=(20, 25, OCONEE.format(lo=20, wf=25, nlo=30, nwf=40)), fees_extra=nonres(10),
  src=("https://experienceoconee.com/park-fees/high-falls-fees", ["Oconee County Residents", "$20.00 - Normal Site",
       "$25.00 - Waterfront Site", "Non-Residents", "$30.00 - Normal Site", "$40.00 - Waterfront Site"]))
d(4379, act="price", fees=(20, None, "Oconee County's posted fees: $20 a night for a county resident, $30 for everyone "
                                    "else. Read 2026-10-14."), fees_extra=nonres(10),
  src=("https://experienceoconee.com/park-fees/chau-ram-fees", ["Oconee County Residents", "$20.00 - Normal Site",
       "Non-Residents", "$30.00 - Normal Site"]))
d(2664, act="price", drop_web=RA + "routt-county-fairgrounds/PRCG/1068250/overview",
  note=("Routt County-operated fairgrounds RV park in Hayden. 9 full-hookup sites (20/30/50 amp) open year-round, "
        "plus 12 primitive electric-only (20 amp) sites open Apr 15-Nov 30; dump station, showers. RVs to 50 ft. "
        "14-day max per 30 days; general transient camping (not event-only), closed to the public only during the "
        "August fair. Reservation required. --Claude"),
  fees=(28, 48, "Primitive electric (20 amp) $28 a night, full hookups $48, plus taxes and fees; closed to the public "
                "during the county fair in August. Read 2026-10-14."),
  src=("https://www.routtcountyfair.org/p/other/campingrv-park", ["Full Hook- Up Sites: (water, sewer, and electric "
       "20/30/50 ) are $48.00/day plus taxes and fees.", "Primitive Electric Sites: (20 amp) are $28.00/day plus taxes "
       "and fees.", "All sites will be closed to the public and not available for reservation during the annual Routt "
       "County Fair in August."]))
d(4324, act="price", drop_web="https://www.reserveamerica.com/explore/clay-county-recreation-park/NC",
  add_web=RA + "clay-county-rec-park/PRCG/1072250/overview",
  fees=(30, 35, "2027 season: RV sites $30 a night lake view, $35 lakefront (tent sites $20); stays up to 14 days book "
                "on ReserveAmerica, and a separate lottery fills the seasonal sites. Read 2026-10-14."),
  src=("https://campgrounds.claync.us/_files/ugd/fe4bcd_866a752a1a9d44148808c1a1f1450fe4.pdf",
       ["CLAY COUNTY REC. PARK CAMPING RATES 2027 CAMPING SEASON", "RV Daily $ 30.00 $ 35.00 (Lake View, Lake Front)",
        "All Tent Sites are $20.00"]))
d(4832, act="price",
  fees=(45, None, "RV sites $45 a night all year (electric, water and sewer, up to four people; primitive $35). Rates "
                  "approved by the county board on 2026-04-06. Read 2026-10-14."),
  src=("https://hartsprings.com/wp-content/uploads/Hart-Springs-Rates-Approved-at-04.06.26-BOCC-Meeting.pdf",
       ["Camping Rates (Includes Electric)", "RV Camping", "Includes 4 People per site", "Daily $45 $45",
        "Primitive Camping", "$35 Per Night", "Updated at 04/06/2026 BOCC meeting"]))
d(6768, act="price", drop_web="https://www.reserveamerica.com/campgroundDetails.do?contractCode=CHUB&parkId=781565", fees=(45, None, "$45 a night ($225 a week). Read 2026-10-14."),
  src=("https://secludedpines.com/rates/", ["Nightly/Weekly Rates", "Nightly: $45/night", "Weekly: $225/week"]))
d(7716, act="price", name="Corpus Christi Boardwalk RV Park",
  drop_web=RA + "portland-rv-park/CHUB/784013/overview",
  add_web="https://www.campspot.com/book/corpuschristiboardwalkrvpark",
  note=("Waterfront RV park at 601 US-181, Portland, on the US-181 causeway spit across Nueces Bay near Indian "
        "Point/Sunset Lake (formerly Portland RV Park). Full hookups 30/50-amp, gravel/grass drive-through and back-in "
        "sites, WiFi. Nightly plus weekly/monthly; bookable online. --Claude"), fees=(40, None, "$40 a night ($200 a week, $425 a month). Read 2026-10-14."),
  src=("https://www.corpuschristiboardwalkrvpark.com/", ["Daily RV Rate", "$40.00", "Weekly RV Rate", "$200.00"]))
KCCA = ("2026, Victoria Day to Thanksgiving: unserviced $48 a night, 15 amp with water $57, 30 amp with water $61; "
        "$15 per online reservation. Read 2026-10-14.")
for i in (8269, 8279):
    d(i, act="price", rf=15, fees=cad(48, 61, KCCA),
      src=("https://www.kettlecreekconservation.on.ca/camping-fees/", ["2026 Fees", "Online Reservations", "$15",
           "Site Description | Unserviced | 15 Amp with Water | 30 Amp with Water",
           "Nightly Campsite | $48 | $57 | $61"]))
d(9804, act="price", fees=(22, None, "RV sites $22 a night for a county resident, $30 for everyone else; no electric "
                                    "or water hookups. Open Memorial Day weekend to Labor Day. Read 2026-10-14."),
  fees_extra=nonres(8),
  src=("https://www.bonnercountyid.gov/parks", ["RV sites are available at $22 a night for residents and $30 a night "
       "for nonresidents.", "The park is open the weekend before Memorial Day to the weekend after Labor Day"]))
d(9809, act="price", drop_web=RA + "city-of-burley-snake-river-rv-park/CHUB/784450/overview",
  add_web="https://app.fireflyreservations.com/reserve/property/CityofBurleySnakeRiverRVPark", fees=(25, None, "$25 a night (24 hours) plus processing fees. Read 2026-10-14."),
  src=("https://burleyidaho.org/236/Burley-Snake-River-RV-Park", ["All sites cost for a 24 hour stay is $25.00 plus "
       "processing fees."]))
d(10482, act="price", drop_web=RA + "entiat-city-park/PRCG/1068200/overview",
  add_web="https://www.campspot.com/book/entiat-city-park",
  note=("City of Entiat 40-acre park on the Columbia River (Lake Entiat) shoreline. 31 RV sites (29 full hookup "
        "30/50 amp, 2 without sewer), 26 tent sites, restrooms/showers, boat launch, waterfront trail. Reservable "
        "online (Campspot), open ~mid-Mar to mid-Nov. --Claude"),
  fees=(40, 65, "2026: RV sites with sewer $65 a night; sites 41-42 (no sewer) $55 May to Labor Day, $40 in April "
                "and after Labor Day; $10 off for seniors and veterans; $7 per reservation. Read 2026-10-14."),
  rf=7,
  src=("https://www.entiatwa.us/your_community/parks/entiat_city_park.php", ["Rates for 2026", "RV Spaces 9-37 "
       "$65.00 per night", "RV Spaces 41 & 42 $40.00 per night (No sewer)", "RV Spaces 41 & 42 $55.00 per night (No "
       "sewer)", "Reservation Fee $7.00 per reservation"]))
EBRPD = "East Bay Regional Park District, per night: {}; $8 per reservation. Read 2026-10-14."
d(11719, act="price", rf=8,
  fees=(35, 45, EBRPD.format("tent or RV site with no hookups $35, RV site with water, sewer and 30 amp $45")),
  src=("https://www.ebparks.org/parks/anthony-chabot/camping", ["Tent or RV site (no hook-ups) : $35",
       "RV Site (Water, Sewer, 30 amp electrical hook-up): $45", "Reservation Fee: $8 per site"]))
d(11740, act="price",
  fees=(45, 65, "$45 a night with water only, $65 with sewer, water and electric up to 50 amp. Read 2026-10-14."),
  src=("https://www.ebparks.org/parks/dumbarton-quarry/campground", ["Campsite: $45 per night; water only, no "
       "electrical or sewer", "Campsite: $65 per night; sewer, water, electric up to 50 amp"]))
d(11744, act="price", rf=8,
  fees=(35, 50, EBRPD.format("tent or RV site with no hookups $35, RV site with water, sewer and 30 amp $50")),
  src=("https://www.ebparks.org/parks/del-valle/camping", ["Tent or RV site (no hook-ups) : $35",
       "RV Site (Water, Sewer, 30 amp electrical hook-up): $50", "Reservation Fee: $8 per site"]))
INYO_FEE = "Inyo County: $14 a vehicle a night ($5 each extra vehicle), no hookups. Read 2026-10-14."
d(11721, act="price", fees=(14, None, INYO_FEE),
  src=(INYO + "baker-creek-campground", ["$14 per vehicle per night. No hook ups.", "Additional vehicle: $5.00 per night"]))
d(12402, act="price", fees=(14, None, INYO_FEE),
  src=("https://www.inyocounty.us/services/parks-recreation/diaz-lake-campground-0", ["$14 per site/vehicle per night",
       "Additional vehicle: $5.00 per night"]))
d(11766, act="price", fees=(14, None, INYO_FEE), drop_web=["https://www.inyocounty.us/services/parks-recreation",
  "https://www.reserveamerica.com"], add_web=[INYO + "independence-creek",
  RA + "independence-creek-campground/INYO/1100015/overview"],
  src=(INYO + "independence-creek", ["$14 per vehicle per night. No hook-ups.", "Additional vehicle: $5.00 per night"]))
d(11826, act="price", fees=(14, None, INYO_FEE), drop_web="https://www.reserveamerica.com",
  add_web=[INYO + "taboose-creek-campground", RA + "taboose-creek-campground/INYO/1100013/overview"],
  src=(INYO + "taboose-creek-campground", ["$14 per vehicle per night. No hook ups.",
       "Additional vehicle: $5.00 per night"]))
d(11831, act="price", fees=(14, None, INYO_FEE), drop_web=["https://www.inyocounty.us/services/parks-recreation",
  "https://www.reserveamerica.com"], add_web=[INYO + "tinnemaha-creek-campground",
  RA + "tinnemaha-creek-campground/INYO/1100012/overview"],
  src=(INYO + "tinnemaha-creek-campground", ["$14 per vehicle per night. No potable water, no hook ups.",
       "Additional vehicle: $5.00 per night"]))
d(11828, act="price", drop_web=["https://www.inyocounty.us/services/parks-recreation", "https://www.reserveamerica.com"],
  add_web=["https://tecopahotspringsandcampground.com/", INYO + "tecopa-park-campground"],
  fees=(15, None, "Run by a concessionaire, booked through RoverPass: $15 a night for an RV or tent site on every "
                  "date read (October 2026, January and June 2027), power an optional upgrade. Read 2026-10-14."),
  src=("https://www.roverpass.com/c/tecopa-hot-springs-campground-tecopa-ca/booking/",
       ["RV Sites - Camping: nightPrice $15.00 (2026-10-17/20, 2027-01-26/30, 2027-06-08/12)",
        "RV Sites - Camping with Optional Power Upgrade: $15.00"]))
d(632, act="price", rf=6.5,
  fees=(39, 75, "ReserveAmerica's quotes for June 2027: electric (30 amp) $39 a night on a weekday and $43 on a "
                "Saturday, electric and water $50-60, full hookups $73-75; $6.50 per reservation. Read 2026-10-14."),
  src=(RA + "bull-run-regional-park--centreville/NOVA/1020011/campsites",
       ["Electric Campsite (30 amp): $39.00 Per Night (2027-06-15), $43.00 (2027-06-19)",
        "Electric Campsite (50/30 amp) with Water: $55.00 / $60.00", "Full Hook Up (50/30 amp): $73.00 / $75.00",
        "Reservation Fees $6.50"]))
d(308, act="drop", rule="TENT",
  why="DCNR's camping page lists only rustic tenting sites along Silver Creek (plus cottages and group tenting), run "
      "by the Friends of Salt Springs Park by phone; a camper report calls the tent sites walk-in and no fit for "
      "even a small RV. ReserveAmerica lists only the pavilion.")

# a single posted rate is that rate, not a "from" price
for _i in (4379, 4832, 6768, 7716, 9804, 9809, 11721, 12402, 11766, 11826, 11831, 11828):
    _f = D[_i]["fees"]
    D[_i]["fees"] = (_f[0], _f[0]) + tuple(_f[2:])

# ---- ReserveAmerica reads, and the parks it no longer lists ----
# RA's CHUB pages ("Private and Local Campgrounds") are directory listings with no booking; the PRCG ones that answer
# "OOPS" or a blank error page have left ReserveAmerica (most for Firefly, Aspira's other system).
d(4150, act="price", rf=4, fees_extra=nonres(37),
  fees=(17, 27, "ReserveAmerica's quotes for June 2027: $17 a night without electric, $27 with (a Massachusetts "
                "resident's rate; DCR charges out-of-state campers $54 at its inland campgrounds, plus $10 here for "
                "electric). Massasoit isn't named on DCR's fee table. $4 per reservation. Read 2026-10-14."),
  src=("https://massdcrcamping.reserveamerica.com/camping/massasoit-state-park/r/campgroundDetails.do?contractCode=MA"
       "&parkId=32611", ["STANDARD ELECTRIC A002: $27.00 Per Night (6/15 and 6/19/2027)",
       "STANDARD NON ELECTRIC C055: $17.00 Per Night", "reservation fee $4.00"]),
  src2="https://www.mass.gov/info-details/camping-fees ('Inland Campgrounds', 'Basic Campsites MA Resident Out of "
       "State Resident', '$17 $54'), read 2026-10-14")
d(4677, act="price", rf=3.5,
  fees=(30, 30, "ReserveAmerica's quote for a full-hookup site: $30 a night ($210 a week), plus $3.50 per "
                "reservation. Read 2026-10-14 for 2026-10-28."),
  src=(RA + "diamond-lakes-regional-park-campground---augusta/PRCG/1063600/15350/campsite-booking",
       ["Standard Electric", "Camping Fees (1 night)", "$30.00 Per Night, $210.00 Per Week", "Reservation Fees $3.50"]))
d(5073, act="price",
  fees=(35, 35, "ReserveAmerica's quote for a standard full-hookup site in June 2027: $35 a night ($245 a week). "
                "Read 2026-10-14."),
  src=(RA + "mcleod-park-campground/PRCG/1070600/campsites", ["Standard Full Hookup", "$35.00 Per Night, $245.00 Per "
       "Week (2027-06-15 and 2027-06-19)"]))
d(6801, act="price", drop_web=["http://www.buffalorvparkok.com/", RA + "buffalo-rv-park--oklahoma/CHUB/783563/overview"],
  add_web="https://www.hipcamp.com/en-US/land/oklahoma-buffalo-rv-park-88lhxmdr",
  note=("RV park on US-64 in Buffalo (Harper County), NW Oklahoma; 18 full-hookup 20/30/50-amp sites (rigs to 50 ft), "
        "dump station, trash service; near Fort Supply Lake and Gloss Mountain SP. Booked through Hipcamp. --Claude"),
  fees=(31, 31, "Hipcamp lists its 18 full-hookup sites at $31 a night (before Hipcamp's service fee). Read 2026-10-14."),
  src=("https://www.hipcamp.com/en-US/land/oklahoma-buffalo-rv-park-88lhxmdr", ["Full Hook Up RV Sites",
       "pricePerNight 31.0", "rvMaxLength 50 ft", "18 sites"]))
d(4653, act="keep", drop_web=RA + "towns-bluff-park-and-heritage-center/CHUB/783844/overview",
  add_web="https://app.fireflyreservations.com/Reserve/Property/TownsBluffParkandHeritageCenter",
  note=("County park operated by Jeff Davis County on the Altamaha River at 45 Riverwood Trail, Hazlehurst; ~23-24 "
        "leveled RV/tent sites plus 2 yurts, bathhouse, boat ramp, heritage museum. Reservable online (Firefly). "
        "--Claude"),
  why="county park; it now books on Firefly (behind reCAPTCHA) and posts no rate")
d(4765, act="keep", drop_web=RA + "lake-in-the-forest-resort/PRCG/1062250/campsites",
  add_web="https://app.fireflyreservations.com/reserve/property/LakeintheForestResort",
  note=("Transient/nightly RV resort on Half Moon Lake in the Ocala National Forest; 30/50-amp full-hookup sites plus "
        "cabins, heated pool, rec center, boat slips, lake fishing. Also takes seasonal/snowbird stays. Reserve online "
        "or by phone (no walk-ins)."),
  why="its rate page still advertises the 2017-2018 season, so it prices nothing; it now books on Firefly, and RV "
      "Life's $$ is the price indicator; a website with a phone and a Google listing (4.7, 127 reviews) are the presence")
d(6014, act="keep", drop_web=RA + "sportsmens-centennial-park/CHUB/781463/overview",
  add_web="https://app.fireflyreservations.com/Reserve/Property/SportsmensCentennialPark",
  why="county park; it now books on Firefly (behind reCAPTCHA) and posts no rate")
d(9773, act="keep", drop_web=RA + "buhl-chamber-of-commerce-rv-park/CHUB/784666/overview",
  add_web="https://visitsouthidaho.com/lodging/buhl-rv-park/",
  note=("Small in-town RV park run by the Buhl Chamber of Commerce (a business nonprofit, not city government) on "
        "US-30. 4 water/electric pull-through/pull-in sites (3 crushed rock, 1 concrete), dump station by the Chamber "
        "office, 14-day max, self-pay drop box; walkable to grocery/laundry. --Claude"),
  why="no booking site now (ReserveAmerica only ever listed it) and no website of its own; Google lists it open with "
      "a phone and 33 reviews (4.6), and RV Life's $$ is the price indicator (AWH 2026-10-14)")
COLUMBIA = ("Columbia County's fee table (effective May 1, 2020, still the one posted): full hookups $31 a night "
            "November-April and $33 May-October, water and electric $28-30; no-hookup sites $20-23. Read 2026-10-14.")
COLSRC = ("https://www.columbiacountyor.gov/departments/ParksForestsRecreation/park-fees", ["COLUMBIA COUNTY PARK FEES",
          "Effective May 1, 2020", "Campsite with Full Hookups", "$31.00 per night*", "$33.00 per night*",
          "Campsite with water and electric hookup", "$28.00 per night*", "$30.00 per night*"])
d(11074, act="price", drop_web=RA + "camp-wilkerson/PRCG/1067150/campsites",
  add_web="https://app.fireflyreservations.com/Reserve/Property/CampWilkerson",
  note=("Columbia County forested park (~280 acres) on Apiary Road near Rainier/Vernonia: mix of ~10 tent-or-RV sites "
        "plus 2 no-hookup RV sites, Adirondack shelters, cabins, a horse camp and a day lodge; some sites accept RVs up "
        "to ~44 ft. Reservable online (Firefly), with drop-in camping if space allows. --Claude"),
  fees=(20, 33, COLUMBIA, "USD", "2020"), src=COLSRC)
d(11075, act="price", drop_web=RA + "hudsonparcher-park/PRCG/1067200/overview",
  add_web="https://app.fireflyreservations.com/Reserve/Property/HudsonParcherPark",
  note=("Columbia County park in the forested hills ~4 mi from Rainier, along Beaver Creek: ~25 RV sites (10 "
        "water/electric + 15 gravel sites, some full-hookup), plus 10 tent sites and a bike-camp site; RVs to ~50 ft, "
        "dump station, showers, playgrounds, ballfields. Reservable online (Firefly). --Claude"),
  fees=(28, 33, COLUMBIA, "USD", "2020"), src=COLSRC)
d(4609, act="keep", drop_web="https://www.reserveamerica.com",
  note=("USACE Savannah District campground on J. Strom Thurmond (Clarks Hill) Lake at Fishing Creek, run by a lessee "
        "(Georgia Freshwater Campgrounds). 16 RV sites with water + electric (30-amp, some 50-amp), no sewer (dump "
        "station); separate loop of 10 primitive sites. Neither ReserveAmerica nor recreation.gov lists it; Explore "
        "Georgia gives $27 a night for the water-and-electric sites (undated). Federal land. --Claude"),
  why="federal campground; no booking site found and no dated rate (Explore Georgia's $27 is undated)")
d(5068, act="keep", why="county park; ReserveAmerica's booking page errors on every date tried, and the county posts no rate")
