"""Summarize vendor_calendar.py text: per park and window, the nightly prices of each RV site kind.

    python3 -I vendor_parse.py DIR > OUT.json

A row is a site name, then a tab-separated price per day ($N, blank when booked). Kinds: 'std'
(Campsite N, Campsite N ADA, Live Oak / Beach / Overflow / RV Campsite N), 'fhu' (Full Service /
Full Hookup ...), 'ne' (... Non-Electric ...); tent, hike-in, boat-in, rustic, hammock, trailside,
double, group, equestrian and cabin rows are left out."""
import json, os, re, sys, collections
D = sys.argv[1]
SKIP = re.compile(r"(?i)tent|hike|boat|rustic|hammock|trailside|double|group|equest|cabin|yurt|cottage|lodge|primitive|walk|shelter|pavilion")
out = collections.defaultdict(dict)
for f in sorted(os.listdir(D)):
    m = re.match(r"(.+)_(now|\d{4}-\d\d-\d\d)\.txt$", f)
    if not m:
        continue
    park, win = m.groups()
    kinds = collections.defaultdict(list)
    days = []
    prev = ""
    for line in open(os.path.join(D, f)):
        line = line.rstrip("\n")
        if line.strip() in ("Unavailable", "Call", "-", ""):
            # Tennessee prints each unbookable night as its own 'Unavailable' line inside the row.
            continue
        if line.startswith("$"):
            # Alabama's calendar puts the site name on its own line, then the prices.
            name, cells = prev, line.split("\t")
        elif "\t" in line:
            name, *cells = line.split("\t")
        else:
            prev = line
            continue
        # Only rows named as campsites: Alabama's calendar also lists named backcountry sites
        # ('Never Land', 'CCC Quary', 'Holly Trail Campsite' at $0) among them.
        if (not any(c.strip().startswith("$") for c in cells) or SKIP.search(name)
                or not re.search(r"(?i)\b(camp)?site\b", name) or re.search(r"(?i)trail", name)):
            continue
        if re.search(r"(?i)non-?electric", name):
            k = "ne"
        elif re.search(r"(?i)full (service|hook)", name):
            k = "fhu"
        else:
            k = "std"
        # A cell can read '$33 Call' (bookable by phone only); the price is still the price.
        kinds[k] += [int(float(re.match(r"\$([\d,.]+)", c.strip()).group(1).replace(",", "")))
                     for c in cells if re.match(r"\$[\d,.]+", c.strip())]
    out[park][win] = {k: {"n": len(v), "min": min(v), "max": max(v), "common": collections.Counter(v).most_common(3)}
                      for k, v in kinds.items()}
json.dump(out, sys.stdout, indent=1)
