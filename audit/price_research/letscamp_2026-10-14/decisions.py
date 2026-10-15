"""Per-entry decisions of the Let's Camp pass (2026-10-14), read by letscamp_apply.py. Keys as in
../roverpass_ops_2026-10-14/decisions.py. Read from pages.jsonl (ops_read.py) with ../roverpass_ops_2026-10-14/ops_view.py,
lc.jsonl (lc_fetch.py) and the Let's Camp directory (letscamp_directory_2026-10-14.json, /api/camps with
X-Tenant-Type: camp). Canadian fees are CAD (fee tuple element 4).
"""
D = {}
LC = "https://letscamp.ca/camps/"


def d(i, **kw):
    assert i not in D, i
    D[i] = kw


def cad(lo, hi, text):
    return (lo, hi, text, "CAD")


# ---- batch 1 ----
d(3578, act="price",
  fees=(35, None, "Let's Camp lists RV sites from $35 a night. Read 2026-10-14."),
  src=(LC + "harbour-village-resort", ["startingAtPrice 35, per night (Let's Camp directory API)"]))
d(8275, act="price",
  fees=cad(35, 45, "Victoria Day to Thanksgiving: unserviced $35 a night, hydro only $43, hydro and water $45. "
                   "Read 2026-10-14."),
  src=("https://lowerthames-conservation.on.ca/wp-content/uploads/2026-Fee-Schedule.pdf",
       ["Camping Nightly Monthly Season (Victoria Day - Thanksgiving)", "Premium Sites $45",
        "(Hydro & Water/Waterfront Sites Big Bend)", "Hydro Only $43", "Un-serviced $35"]))
d(8309, act="price",
  fees=cad(46, 53.5, "2026: powered sites (15 amp, water) $53.50 a night, non-powered $46; 10% off for 55+. "
                     "Read 2026-10-14."),
  src=("https://brockville.com/things-to-do/camping/", ["Daily Camping Rates (2026 Season):", "Powered: $53.50",
       "Non-powered: $46.00"]))
d(8582, act="price",
  fees=cad(40, 50, "Electric only $40 a night, electric and water $45, full service $50 (tent sites $26-30). "
                   "Read 2026-10-14."),
  src=("https://www.nelson.ca/680/City-Campground", ["Partial Serviced Site (electricity Site (electricity only) "
       "$40.00/night", "Services Site (electricity and water) $45.00/night",
       "Full Service Site (electricity, water, sewer) $50.00/night"]))
d(8672, act="price", drop_web="https://www.letscamp.ca/", add_web=LC + "burton-historical-park",
  fees=cad(33, 40, "Serviced sites $40 a night, unserviced $33 ($38 and $31 for 65+), GST included. Read 2026-10-14."),
  src=("https://burtonhistoricalpark.com/2014/03/04/reservation-information/", ["Nightly rates:",
       "Serviced $40, Seniors (65+) $38", "Unserviced $33, Seniors (65+) $31", "5% GST included"]),
  ie="its bare letscamp.ca link now points at the park's own Let's Camp page")
d(8330, act="keep", why="run by the Dawson Citizen's Improvement Association (a non-profit); its page gives no rate and "
  "sends bookings to its Let's Camp page, which is a working booking page (both indicators, AWH 2026-10-14)")

# ---- batch 2 ----
d(8680, act="keep", why="regional-district campground; its page gives the season (May long weekend to September 30, "
  "14 nights at most) and its Let's Camp page but no rate")
d(8750, act="keep", why="its own site gives only the monthly rate ($800, April-September) and books nights through its "
  "Let's Camp page, which is a working booking page (both indicators, AWH 2026-10-14)")
d(8787, act="price",
  fees=cad(22, 42, "Non-power sites $22 a night, power $27, full service $42. Read 2026-10-14."),
  src=("https://districtoftaylor.com/peace-island-park/", ["Park Rates", "Non-power sites $22/unit/night",
       "Power sites $27/unit/night", "Full Service sites $42/unit/night"]))
d(9018, act="keep", drop_web=["https://www.albertaparks.ca/parks/north/fort-vermilion-pra/",
                              LC + "6790f212b01821878ab16757"],
  add_web=LC + "fortvermilionbridge",
  why="Alberta Parks' page for it now answers 404; Mackenzie County books it on Let's Camp as Fort Vermilion Bridge "
      "Campground, which posts no rate off-season")
d(9032, act="price",
  fees=cad(40, 40, "Individual sites (30-amp power) $40 a night. Read 2026-10-14."),
  src=("https://www.mdtaber.ab.ca/p/taber-municipal-park", ["Camping rates", "Individual Sites:", "$40 per night",
       "All sites have been upgraded to 30-amp power."]))
d(9037, act="price",
  fees=cad(25, 40, "Summer: power-only sites $25 a night, full service $40 (no-service $20); winter power-only $60. "
                   "Rates as of July 1, 2026. Read 2026-10-14."),
  src=("https://www.threehills.ca/p/campground", ["Full- Service Sites - Daily", "$ 40.00", "Power Only Sites - Daily",
       "$ 25.00", "*Rates as of July 1, 2026"]))

# ---- batch 3 ----
d(9049, act="price",
  fees=cad(30, None, "Let's Camp lists sites from $30 a night (the county's page gives only the $3,500 seasonal rate). "
                     "Read 2026-10-14."),
  src=(LC + "black-nugget-lake", ["startingAtPrice 30, per night (Let's Camp directory API)"]))
d(9050, act="price",
  fees=cad(27, 27, "$27 a night per unit; 25 sites. Read 2026-10-14."),
  src=("https://www.county.wetaskiwin.ab.ca/Facilities/Facility/Details/Coal-Lake-South-Park-14",
       ["Admission Fee", "$27.00 per night per unit. 25 sites available"]))
d(9057, act="price",
  fees=cad(45, 50, "2026: partial service (power, water, one firewood bundle) $45 a night, full service $50; open tent "
                   "area $25. Read 2026-10-14."),
  src=("https://mdgreenview.ab.ca/tourism/campgrounds-day-use-areas/grande-cache-campground/", ["2026 Fee Schedule:",
       "Full-service (power, water, sewer & one firewood bundle): $ 50.00 per night",
       "Partial-service (power, water & one firewood bundle): $ 45.00 per night"]))
for _i, _s, _n in ((9063, "hanmore-lake-east-campground", "16 campsites"), (9064, "hanmore-lake-west-campground", "39 campsites")):
    d(_i, act="price", drop_web="https://letscamp.ca", add_web=LC + _s,
      fees=cad(25, 25, "No power, water or sewer; $25 a night. Open May 14 to October 4. Read 2026-10-14."),
      src=("https://www.smokylakecounty.ab.ca/campgrounds", ["Hanmore Lake", _n, "No power, water or sewer services",
           "$25.00/ night", "Campground Open: May 14 to October 4"]),
      ie="its bare letscamp.ca link now points at its own Let's Camp page")
d(9067, act="keep", why="M.D. of Bonnyville park; neither the M.D.'s page nor its Let's Camp page (off-season) gives a rate")
d(9068, act="price",
  fees=cad(25, 35, "County of St. Paul campgrounds: non-power $25 a night, power $35; 14 nights at most. "
                   "Read 2026-10-14."),
  src=("https://www.county.stpaul.ab.ca/campgrounds/", ["Campers may book up to 14 consecutive days at Floatingstone",
       "Daily", "Non-power: $25/night", "Power: $35/night"]))
d(9069, act="keep", why="M.D. of Bonnyville park; neither the M.D.'s page nor its Let's Camp page (off-season) gives a rate")
d(9070, act="keep", drop_web="https://letscamp.ca/", add_web=LC + "chepi-sepe-park",
  why="town campground; neither the town's page nor its Let's Camp page (off-season) gives a rate; its bare "
      "letscamp.ca link now points at its own Let's Camp page")
d(9118, act="keep", drop_web="https://pihtokwe.letscamp.ca/", add_web=LC + "pihtokwe-campsite",
  why="its only link, a pihtokwe.letscamp.ca subdomain, no longer connects; its Let's Camp page "
      "(pihtokwe-campsite: full service, power only and non-service sites, rigs to 50 ft) is a working booking page "
      "(both indicators, AWH 2026-10-14), and RV Life rates it $$")

# ---- batch 4 ----
SRP = ("regional park; saskregionalparks.ca sits behind a human captcha (SiteGround) and its Let's Camp page posts "
       "no rate off-season")
d(9207, act="keep", why=SRP)
d(9208, act="keep", drop_web="https://letscamp.ca", add_web=LC + "attons-lake",
  why=SRP + "; its bare letscamp.ca link now points at its own Let's Camp page")
d(9209, act="price",
  fees=cad(20, None, "Let's Camp lists sites from $20 a night. Read 2026-10-14."),
  src=(LC + "bengough-regional-park", ["startingAtPrice 20, per night (Let's Camp directory API)"]))
d(9213, act="keep", why="town campground; neither the town's page nor its Let's Camp page (off-season) gives a rate")
d(9214, act="keep", why=SRP)
d(9216, act="price",
  fees=cad(25, 35, "Electrified sites $35 a night plus GST, non-electric $25; 40 of the sites go to seasonal "
                   "campers by draw. Read 2026-10-14."),
  src=("https://www.rvchiteklake.com/camping-fees", ["Nightly Camping Fees - Electrified - $35.00 + GST = $36.75",
       "Nightly Non-Electric Fees- $25.00 + GST = $26.25"]))
d(9219, act="keep", why=SRP)
d(9222, act="price",
  fees=cad(35, 40, "Lots 1-16 (15/30-amp power and water) $35 a night, lots 17-25 (30-amp power, water, sewer) $40; "
                   "less by the week or month. Read 2026-10-14."),
  src=("https://townofmaidstone.com/attractions/campgrounds/", ["Lots 1-16, 15 or 30 amp power & water",
       "$35.00 / 1 – 6 nights", "Lots 17-25, 30 amp power, water & sewer", "$40.00 / 1 – 6 nights"]))
d(9224, act="keep", why="regional park; its own site renders nothing without JavaScript and its Let's Camp page posts "
  "no rate off-season")
d(9237, act="keep", why=SRP)

# ---- batch 5 ----
d(9242, act="price",
  fees=cad(40, 50, "2026: 30-amp with water $40 a day, 30-amp full hookup $45, 50-amp full hookup $50, GST included; "
                   "park entry extra ($15 a day). Read 2026-10-14."),
  src=("https://lacpelletierregionalpark.ca/camping/rates/", ["2026 Camping Rates", "30 Amp/Water Sites $40.00 / day",
       "50 Amp Full Hook-up Sites $50.00 / day", "GST is included in the above prices."]))
d(9243, act="keep", why=SRP)
d(9244, act="keep", why=SRP)
d(9247, act="keep", why="regional park; its own site renders nothing without JavaScript and its Let's Camp page posts "
  "no rate off-season")
d(9248, act="price",
  fees=cad(39, 55, "Electric only (15/30 amp) $39 a night, water and electric $45, full service $55; no services $30. "
                   "Read 2026-10-14."),
  src=("https://www.wakamow.ca/camping", ["Campsite fees are as follows:", "Electric only (30 amp/15 amp) – $39.00 per night",
       "Full Service (30 amp, water, sewer) – $55.00 per night"]))
d(9250, act="price",
  fees=cad(25, None, "Let's Camp lists sites from $25 a night, tax included. Read 2026-10-14."),
  src=(LC + "macklin-lake", ["minimumPrice 25, includeTax true (Let's Camp camp API)"]))
d(9252, act="keep", why=SRP)
d(9255, act="keep", drop_web="https://meetinglake.letscamp.ca/", add_web=LC + "meeting-lake",
  why="regional park; its own site renders nothing without JavaScript, its meetinglake.letscamp.ca subdomain no longer "
      "connects (now its Let's Camp camp page), which posts no rate off-season")
d(9257, act="price",
  fees=cad(25, 40, "20-amp power and water $25 a day, 30-amp power and water $35, 30-amp full service $40, plus an $8 "
                   "daily park pass. Read 2026-10-14."),
  src=("https://melvilleregionalpark.com/campground-info", ["30A Full Service Daily $40", "30A Power/Water Daily $35",
       "20A Power/Water Daily $25", "A $8.00 daily park pass for each day of stay"]))
d(9258, act="price", drop_web="https://memoriallake.letscamp.ca/", add_web=LC + "memorial-lake",
  fees=cad(37, 37, "2026: camping $37 a night per unit, plus park entry ($12 a day). Read 2026-10-14."),
  src=("https://memoriallakeregionalpark.com/pages/rates", ["Camping Rates", "Camping - per night per unit", "$37",
       "Park Entry - Daily", "$12"]),
  ie="its memoriallake.letscamp.ca subdomain no longer connects; now its Let's Camp camp page")
d(9270, act="keep", why=SRP)
d(9271, act="price",
  fees=cad(20, None, "Let's Camp lists sites from $20 a night before tax. Read 2026-10-14."),
  src=(LC + "redvers-tourism-campground", ["minimumPrice 20, includeTax false (Let's Camp camp API)"]))
d(9273, act="keep", why=SRP)
d(9277, act="keep", why="regional park; its own site renders nothing without JavaScript and its Let's Camp page posts "
  "no rate off-season")

# ---- batch 6 ----
NOJS = "regional park; its own site renders nothing without JavaScript and its Let's Camp page posts no rate off-season"
d(9281, act="keep", why=NOJS)
d(9284, act="keep", drop_web="https://whitesandregionalpark.com/",
  why="regional park; its own domain no longer resolves and its Let's Camp page posts no rate off-season")
d(9287, act="keep", why="regional park; neither its own site nor its Let's Camp page (off-season) gives a rate")
d(9289, act="keep", why="regional park; neither its own site nor its Let's Camp page (off-season) gives a rate")
d(9299, act="keep", drop_web="https://www.gulllakesk.com/recreation/campground",
  why="town campground; the town's campground page now answers 404 and its Let's Camp page posts no rate off-season")
d(9406, act="keep", why="R.M. campground; neither the R.M.'s page nor its Let's Camp page (off-season) gives a rate")
d(9410, act="price",
  fees=cad(21, None, "Let's Camp lists sites from $21 a night. Read 2026-10-14."),
  src=(LC + "lakeview", ["startingAtPrice 21, per night (Let's Camp directory API)"]))
d(12554, act="price",
  fees=cad(38, 66, "2026 (June 1 - September 19), before tax, for two adults and two children: 2-service 20-amp sites "
                   "$38-44 a night by season, 3-service 20-amp $40-46, 30-amp $46-56 ($48-58 on the beach), beachfront "
                   "50-amp $60-66. Read 2026-10-14."),
  src=("https://www.chaletscampingdessillons.com/camping", ["Tarifs Camping", "2026", "2 services, 20 amps",
       "Haute saison:44$", "Basse saison: 38$", "Au bord de la plage,", "3 services, 50 amps", "Haute saison:66$",
       "- Taxes en sus"]))
d(12745, act="keep", drop_web="https://www.lwlionscampground.com/",
  why="Lions Club campground; its own site now answers 404 and its Let's Camp page posts no rate off-season")
d(12798, act="keep",
  why="its own site renders nothing without JavaScript; its Let's Camp page is a working booking page (both "
      "indicators, AWH 2026-10-14), and Waterton Lakes NP is a gateway 6 km away")
d(13017, act="price",
  fees=cad(30, None, "Let's Camp lists sites from $30 a night (the town's 2022 rates: semi-serviced $35, unserviced "
                     "$30). Read 2026-10-14."),
  src=(LC + "bantingpark", ["minimumPrice 30 (Let's Camp camp API)"]))
