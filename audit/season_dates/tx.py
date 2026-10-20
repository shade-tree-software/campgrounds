#!/usr/bin/env python3
"""Texas State Parks: season from each park's own TPWD page (2026-10-20).

    python3 -I audit/season_dates/tx.py [--apply]

TPWD has no statewide statement, so each park answers for itself. A park page whose Hours block
reads "Open daily" is open every day of the year; a park whose campsites page sells a winter
(December - February) weekly rate is camped in winter. Either makes the entry year-round. The
exceptions the pages name go in the note: Garner's Live Oak loop closes in January and February,
Kickapoo Cavern closes Tuesday to Thursday, and the beach sites at Mustang Island and Sea Rim
close in bad weather and high tides.

tpwd.texas.gov serves the wrong intermediate certificate (a Sectigo cross-sign instead of its
issuer, "Entrust OV TLS Issuing RSA CA 2"), so curl fails verification. The pages were fetched
with the right intermediate added from the certificate's own AIA URL
(http://crt.sectigo.com/EntrustOVTLSIssuingRSACA2.crt) and the full chain verified against the
system roots. Verification was never turned off.

Not written: Balmorhea (7011) and Franklin Mountains (7038), whose pages give hours and nothing
that says they camp all year.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

SLUGS = {
    7009: "abilene",
    7010: "atlanta",
    7012: "bastrop",
    7013: "big-bend-ranch",
    7014: "blanco",
    7016: "bonham",
    7017: "brazos-bend",
    7018: "buescher",
    7019: "caddo-lake",
    7022: "caprock-canyons",
    7023: "cedar-hill",
    7025: "choke-canyon",
    7026: "cleburne",
    7027: "cooper-lake",
    7028: "cooper-lake",
    7029: "copper-breaks",
    7030: "daingerfield",
    7031: "davis-mountains",
    7032: "dinosaur-valley",
    7033: "eisenhower",
    7034: "falcon",
    7036: "fort-parker",
    7037: "fort-richardson",
    7039: "galveston-island",
    7040: "garner",
    7041: "goliad",
    7042: "goose-island",
    7044: "guadalupe-river",
    7046: "hueco-tanks",
    7047: "huntsville",
    7048: "inks-lake",
    7049: "kickapoo-cavern",
    7050: "lake-arrowhead",
    7051: "lake-bob-sandlin",
    7052: "lake-brownwood",
    7053: "lake-casa-blanca",
    7054: "lake-colorado-city",
    7055: "lake-corpus-christi",
    7056: "lake-livingston",
    7057: "lake-mineral-wells",
    7058: "lake-somerville",
    7059: "lake-somerville",
    7060: "lake-tawakoni",
    7061: "lake-whitney",
    7062: "lockhart",
    7063: "lost-maples",
    7064: "martin-creek-lake",
    7065: "martin-dies-jr",
    7066: "mckinney-falls",
    7067: "meridian",
    7069: "mission-tejas",
    7070: "monahans-sandhills",
    7071: "mother-neff",
    7072: "mustang-island",
    7073: "palmetto",
    7074: "palo-duro-canyon",
    7075: "palo-pinto-mountains",
    7076: "pedernales-falls",
    7077: "possum-kingdom",
    7078: "purtis-creek",
    7079: "ray-roberts-lake",
    7080: "ray-roberts-lake",
    7081: "san-angelo",
    7082: "sea-rim",
    7083: "seminole-canyon",
    7085: "south-llano-river",
    7086: "stephen-f-austin",
    7089: "tyler",
    7090: "village-creek",
    14816: "big-bend-ranch",
}

# Pages without "Open daily" whose campsites page sells a winter rate.
WINTER_RATE = {
    7061: "Weekly rate is available from November through February.",
    7077: "Peak rates are from March through November.",
}

NOTES = {
    7040: "The Live Oak Camping Area is closed in January and February; the Rio Frio area stays open.",
    7049: "The park is closed Tuesday to Thursday; gates open Friday to Sunday 7 a.m. - 10 p.m., Monday 7 a.m. - 4:30 p.m.",
    7072: "The beach sites close from time to time in bad weather; TPWD suggests calling ahead.",
    7082: "The West Beach primitive sites close for extreme high tides and other weather.",
}

# What the Hours block says where it isn't the literal "Open daily".
HOURS_QUOTE = {
    7049: "Gate Hours: Friday - Sunday 7 a.m. - 10 p.m., Monday 7 a.m. - 4:30 p.m. ... Park Closed: Tuesday - Thursday",
    7051: "Gate Hours 6 a.m. - 10 p.m. daily",
    7053: "Gate Hours: 7 a.m.-10 p.m. daily",
}

DECISIONS = {}
for i, slug in SLUGS.items():
    season = {"year_round": True}
    if i in NOTES:
        season["note"] = NOTES[i]
    if i in WINTER_RATE:
        src = (f"https://tpwd.texas.gov/state-parks/{slug}/fees-facilities/campsites "
               f"(\"{WINTER_RATE[i]}\"), read 2026-10-20")
    else:
        quote = HOURS_QUOTE.get(i, "Open daily")
        src = f"https://tpwd.texas.gov/state-parks/{slug} (Hours: \"{quote}\"), read 2026-10-20"
    if i == 7040:
        src += f"; https://tpwd.texas.gov/state-parks/{slug}/fees-facilities/campsites (Live Oak closure)"
    DECISIONS[i] = (season, src)

if __name__ == "__main__":
    run(DECISIONS)
