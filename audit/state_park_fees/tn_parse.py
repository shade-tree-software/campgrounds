"""Summarize Tennessee's calendar text (vendor_calendar.py) per park, window and campground.

    python3 -I tn_parse.py DIR > OUT.json

A row starts with its site name ('Fairview Campsite 52', 'Area A Campsite A12', 'Campsite 7'); its nightly
cells follow on the same line (tab-separated) and/or on their own lines ('$42', 'Unavailable'). The name's
part before 'Campsite'/'Site' is the campground ('' when the park has one). Tent, backcountry, hammock,
group and accessible-only rows are counted apart under kind 'other' and left out of the ranges; a row not
named as a campsite at all ('Backcountry 1', 'Little Island') is left out and listed on stderr."""
import json, os, re, sys, collections
D = sys.argv[1]
NAME = re.compile(r"^(?P<pre>.*?)\s*(?:Campsite|Campground \w+ Site|Site)\b", re.I)
OTHER = re.compile(r"(?i)tent|backcountry|^BC |hammock|group|accessible|trailside|hike|boat|shelter|cabin")
# Sites the calendar names like the RV sites that the park's campground page says are something else
# (tnstateparks.com/parks/campground/<park>, read 2026-10-12); the site counts agree with each page.
SITE_KIND = {
    "edgar-evins": [(r"Campsite \d+P", "tent")],                    # 'Nine primitive walk-in sites'
    "harrison-bay": [(r"Campsite D\d+", "tent")],                   # its primitive tent-only area
    "paris-landing": [(r"Campsite (4[6-9]|5\d|6[0-3])", "tent")],   # 45 RV sites, then the 18 primitive ones
    "fort-pillow": [(r"Campsite (2[2-9]|30)", "tent"),              # 'nine primitive campsites'
                    (r"Campsite (1[89]|20|3[12])", "lowamp")],      # priced between the two; see tn_build.py
    "roan-mountain": [(r"Campsite (19|2\d|3[0-8])", "tent")],       # the 20 tent sites: water, no electric
    "pickett": [(r"Campsite A(2|3|5|6|9|13|15|16|19|20)", "water")],  # the 10 not on the page's electric list
    "t-o-fuller": [(r"Campsite 19", "odd")],                         # every site has water and electric
}
out = collections.defaultdict(dict)
unnamed = {}
for f in sorted(os.listdir(D)):
    m = re.match(r"(.+)_(now|\d{4}-\d\d-\d\d)\.txt$", f)
    if not m:
        continue
    park, win = m.groups()
    rows = collections.defaultdict(list)
    cur = None
    for line in open(os.path.join(D, f)):
        line = line.rstrip("\n")
        cells = line.split("\t")
        head = cells[0].strip()
        if head and not head.startswith("$") and head not in ("Unavailable", "Call") and NAME.match(head):
            cur = head
            cells = cells[1:]
        elif head and not head.startswith("$") and head not in ("Unavailable", "Call"):
            # Any other text ends the row: a header, or a site not named as a campsite ('Backcountry 1',
            # 'Little Island', 'Pine Wheel'), whose prices must not land on the site above it.
            cur = None
            if NAME.match(head) is None and len(cells) > 1 and cells[1].strip().startswith("$"):
                unnamed[head] = park
            continue
        if cur is None:
            continue
        for c in cells:
            mm = re.match(r"\$([\d,.]+)", c.strip())
            if mm:
                rows[cur].append(int(float(mm.group(1).replace(",", ""))))
    camps = collections.defaultdict(lambda: {"prices": [], "sites": 0})
    for name, vals in rows.items():
        pre = NAME.match(name).group("pre").strip()
        kind = next((k for rx, k in SITE_KIND.get(park, []) if re.fullmatch(rx, name)), None) or (
            "other" if OTHER.search(name) else ("primitive" if re.search(r"(?i)primitive", name) else "rv"))
        key = f"{pre}|{kind}"
        camps[key]["prices"] += vals
        camps[key]["sites"] += 1
    out[park][win] = {k: {"sites": v["sites"], "n": len(v["prices"]), "min": min(v["prices"]), "max": max(v["prices"]),
                          "common": collections.Counter(v["prices"]).most_common(3)}
                      for k, v in camps.items() if v["prices"]}
json.dump(out, sys.stdout, indent=1)
for h, park in sorted(unnamed.items(), key=lambda x: (x[1], x[0])):
    print('left out (not named as a campsite):', park, '|', h, file=sys.stderr)
