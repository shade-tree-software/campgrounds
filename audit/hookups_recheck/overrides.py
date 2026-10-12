# Hand corrections to the pre-classifier, from reading each entry (2026-10-12).
JOTR = "https://www.nps.gov/jotr/planyourvisit/campgrounds.htm"
DEVA = "https://www.nps.gov/deva/planyourvisit/camping-in-death-valley.htm"
OVERRIDES = {
    # RIDB's nearest match was the separate group campground; cite the family campground's own FS page.
    11864: {"why": {"water": ("page", "https://www.fs.usda.gov/r05/shasta-trinity/recreation/pigeon-point-campground",
                              "Potable water is not available at this site.")}},
    # The scan matched the concession RV park (10224525); the campground's own record is 10224515.
    11356: {"replace": True, "set": {}, "remove": ["electric", "water", "sewer"],
            "checked_extra": ["recreation.gov facility 10224515 (Katherine Landing Campground): description lists "
                              "restrooms, showers, laundry nearby, Wi-Fi, no hookup statement; the separate RV park "
                              "(10224525) has full hookups"]},
    # A temporary alert ("Currently, no potable water") is not a basis for water: false; the note's own
    # "no water" stays where it has one.
    12116: {"set": {}, "remove": ["electric", "sewer"]},
    12118: {"set": {}, "remove": ["electric", "sewer"]},
    12125: {"set": {}, "remove": ["electric", "water", "sewer"]},
    # Joshua Tree's campground table, per campground: "Pit toilets, tables, and fire grates. No water."
    12025: {"set": {"water": False}, "source": f"{JOTR}: 'Belle | 18 sites. $25 per night. 3,800 feet in elevation. "
                                               "Pit toilets, tables, and fire grates. No water.' (read 2026-10-12)"},
    12027: {"set": {"water": False}, "source": f"{JOTR}: 'White Tank | 15 sites. $25 per night. 3,800 feet in elevation. "
                                               "Pit toilets, tables, and fire grates. No water.' (read 2026-10-12)"},
    12028: {"set": {"water": False}, "source": f"{JOTR}: 'Hidden Valley | 44 sites. $25 per night. 4,200 feet. "
                                               "Pit toilets, tables, and fire grates. No water.' (read 2026-10-12)"},
    12019: {"checked_extra": [f"{DEVA}: RV length limits only, no amenities per campground"]},
    12023: {"checked_extra": [f"{DEVA} (the entry's own link is a 404): RV length limits only, no amenities per campground"]},
}

YOSE = ("https://www.nps.gov/yose/planyourvisit/campgrounds.htm: 'No campsites in Yosemite have hook-ups of any "
        "kind.' and 'Electrical, water, and sewer hookups are not available in Yosemite' (read 2026-10-12)")
for _i in (11921, 11922, 11923, 11924, 11925, 11926, 11928):
    OVERRIDES[_i] = {"set": {"electric": 0, "water": False, "sewer": False}, "remove": [], "source": YOSE,
                     "derived": False}
OVERRIDES[11356] = {"replace": True, "set": {"electric": 0, "water": False, "sewer": False}, "remove": [],
                    "source": "https://www.nps.gov/lake/planyourvisit/campgrounds.htm: 'RVs may park at any National "
                              "Park Service campsite; however, there are no hookups.' (the concession RV park at "
                              "Katherine Landing, with full hookups, is separate) (read 2026-10-12)",
                    "derived": False,
                    "checked_extra": ["recreation.gov facility 10224515 (Katherine Landing Campground): no hookup "
                                      "statement; the scan's nearest match 10224525 is the concession RV park"]}
# A shared Eldorado listing gave "It is best to bring your own water"; the campground's own FS page is cited instead.
OVERRIDES[12183] = {"why": {"water": ("page", "https://www.fs.usda.gov/r05/eldorado/recreation/camino-cove-campground",
                                      "Potable water is not available at this site.")}}
OVERRIDES[12184] = {"why": {"water": ("page", "https://www.fs.usda.gov/r05/eldorado/recreation/jones-fork-campground",
                                      "There is no piped water available at the campground.")}}
# RIDB's nearest match is the Badger Flats GROUP camp; cite the family campground's FS page.
OVERRIDES[12237] = {"why": {"water": ("page", "https://www.fs.usda.gov/r05/sierra/recreation/badger-flat-campground",
                                      "Drinking water not provided.")}}
OVERRIDES[12436] = {"set": {"electric": 0, "water": False, "sewer": False}, "remove": [], "derived": False,
                    "source": "https://www.nidwater.com/peninsula-campground: 'RV dump station & water fill-up is "
                              "available. (No RV site hookups)' (read 2026-10-12)"}
OVERRIDES[13963] = {"set": {"electric": 0}, "remove": [], "derived": False,
                    "source": "https://cpw.state.co.us/state-parks/arkansas-headwaters-recreation-area/arkansas-headwaters-"
                              "recreation-area-camping-lodging: 'Vallie Bridge and Five Points offer visitors basic "
                              "campsites.'; https://cpw.state.co.us/camping defines the tiers: 'Basic Amenities Campsite | "
                              "Tent pad | Table | Grill and/or fire ring', 'Electric Amenities Campsites | Electrical posts "
                              "are 30 amps or more' (read 2026-10-12)"}
OVERRIDES[13655] = {"set": {"water": False}, "derived": False,
                    "source": "https://monocounty.ca.gov/2119/Lundy-Canyon-Campground: 'Water in NOT available in the "
                              "campground.' (read 2026-10-12)"}
