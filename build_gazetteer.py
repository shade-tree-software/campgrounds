#!/usr/bin/env python3
"""Build the committed place gazetteer that `nearest_town.py` reads.

WHY THE EXTRACT IS COMMITTED
----------------------------
`nearest_town.py` answers "what town would a person name for this coordinate",
and the app materializes that onto every timeline card. So every host needs the
data: this laptop, PythonAnywhere, a fresh clone, and the offline USB build.

None of them can be handed a generated file. `trip_data/` is gitignored,
`sync-from-pa.sh` only runs PA -> local, and the two SSH keys are a read-only
rsync and a deploy key pinned to a forced command -- there is deliberately no
way to push a file to PA, and that is a property worth keeping. Downloading the
raw dumps on each host is not the answer either: PA has an outbound whitelist
(the same reason the campground map's route tool calls OSRM from the browser
rather than the server), and the USB build has no network at all.

So the extract is tracked, like `campgrounds.json` (13.6 MB) and
`static/vendor/na-borders.json` before it: a static extract that costs no
third-party requests, works offline, and keeps the styling of the answer ours.
2.2 MB gzipped for every populated place in the US and Canada is a good trade,
and it means this script is the ONLY thing that ever talks to GeoNames.

What must NOT be committed is the *output* of applying it --
`trip_data/place_context.json` is keyed by our own coordinates, family
driveways included, which is exactly why `trip_data/family.json` is gitignored.

    python build_gazetteer.py            # download if needed, report
    python build_gazetteer.py --apply    # write places.tsv.gz
"""

import argparse
import gzip
import io
import os
import re
import sys
import urllib.request
import zipfile

import nearest_town

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, "trip_data", "geonames")
DUMP_URL = "https://download.geonames.org/export/dump/{country}.zip"
COUNTRIES = ("US", "CA")
_UA = "EKKO-Trips/1.0 (gazetteer build; contact via repo owner)"

# Real places only. PPLQ/PPLH are abandoned or historical, PPLX is a section of
# another place (naming it points at a neighbourhood rather than a town), and
# the name filter drops developments -- "Fall River Estates Subdivision" was
# the closest record to Moraine Park Campground before it was excluded.
KEEP_CODES = nearest_town.KEEP_CODES
JUNK_NAME = nearest_town.JUNK_NAME

# 4 decimal places (~11 m). Coarser was tempting — these are town centroids
# matched against radii of one to twenty-five miles — but 3 dp moved 35 of the
# library's 1,144 answers and flipped two of them from a real town to a
# crossroads by nudging distances across the crossroads ratio test, and it
# merged two places into one outright. 240 KB is worth having the extract
# reproduce the raw dumps exactly, so it is a faithful substitute for them
# rather than an approximation.
PRECISION = 4


def fetch_dumps(download=True):
    os.makedirs(CACHE_DIR, exist_ok=True)
    paths = []
    for country in COUNTRIES:
        path = os.path.join(CACHE_DIR, f"{country}.zip")
        if not os.path.exists(path):
            if not download:
                continue
            print(f"  downloading {country}…")
            req = urllib.request.Request(DUMP_URL.format(country=country),
                                         headers={"User-Agent": _UA})
            tmp = path + ".part"
            with urllib.request.urlopen(req, timeout=180) as resp, \
                    open(tmp, "wb") as out:
                while True:
                    chunk = resp.read(1 << 20)
                    if not chunk:
                        break
                    out.write(chunk)
            os.replace(tmp, path)
        paths.append(path)
    return paths


def rows(paths):
    for path in paths:
        with zipfile.ZipFile(path) as zf:
            name = next(n for n in zf.namelist()
                        if n.endswith(".txt") and "readme" not in n.lower())
            with zf.open(name) as fh:
                for line in io.TextIOWrapper(fh, "utf-8"):
                    f = line.rstrip("\n").split("\t")
                    if len(f) < 15 or f[6] != "P" or f[7] not in KEEP_CODES:
                        continue
                    label = f[1].strip()
                    if not label or any(j in label.lower() for j in JUNK_NAME):
                        continue
                    # A tab in a name would corrupt the row; a newline likewise.
                    if "\t" in label or "\n" in label:
                        continue
                    try:
                        lat, lng, pop = float(f[4]), float(f[5]), int(f[14] or 0)
                    except ValueError:
                        continue
                    yield (round(lat, PRECISION), round(lng, PRECISION),
                           label, f[10].strip(), pop)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true", help="write the extract")
    ap.add_argument("--offline", action="store_true",
                    help="fail rather than download missing dumps")
    args = ap.parse_args()

    paths = fetch_dumps(download=not args.offline)
    if len(paths) != len(COUNTRIES):
        print("missing dumps and --offline was given", file=sys.stderr)
        return 1

    out = sorted(set(rows(paths)))
    body = "".join(f"{la}\t{lo}\t{nm}\t{st}\t{pop}\n" for la, lo, nm, st, pop in out)
    blob = gzip.compress(body.encode("utf-8"), 9)
    print(f"{len(out):,} places -> {len(body)/1e6:.1f} MB raw, "
          f"{len(blob)/1e6:.1f} MB gzipped")
    if not args.apply:
        print("(dry run — pass --apply to write)")
        return 0

    tmp = nearest_town.GAZETTEER_FILE + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(blob)
    os.replace(tmp, nearest_town.GAZETTEER_FILE)
    print(f"wrote {nearest_town.GAZETTEER_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
