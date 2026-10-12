"""Next detail reads: for every (entry, loop, type, high-season price) group with no fitting site read yet, the next
unread site (up to 4 per group, spread across the group): python3 -I qc_sepaq_more_reads.py OUT_HREFS.json.
Run it, read the hrefs with qc_sepaq_details.js, merge into qc_site_details_*.json, repeat (3 rounds, 2026-10-12)."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ev = json.load(open(os.path.join(HERE, "qc_sites_2026-10-12.json")))
det = json.load(open(os.path.join(HERE, "qc_site_details_2026-10-12.json")))
TYPES = {"Rustic campsite", "Semi-serviced campsite", "Campsite furnished with 1 service (water)",
         "Campsite furnished with 1 service (electricity)", "Campsite furnished with 2 services (water, electricity)",
         "Campsite furnished with 2 services (water, sewer hookup)",
         "Campsite furnished with 3 services (water, electricity, sewer hookup)"}


def fits(d):
    for x in d.get("Eligible Equipment", []):
        if re.search(r"(?i)tent trailer", x) or not re.search(r"(?i)\b(trailers?|recreation(al)? vehicles?)\b", x):
            continue
        if re.search(r"(?i)all types", x):
            return True
        m = re.search(r"\((\d+) feet\)", x)
        if m and int(m.group(1)) > 23:
            return True
    return False


groups = {}
for eid, li, ti, name, slug, *p in ev["sites"]:
    t = ev["types"][ti]
    if t not in TYPES:
        continue
    leaf = ev["leaves"][li]
    groups.setdefault((eid, leaf, t, p[1]), []).append(f"/en/reservation/camping/{leaf}/{slug}")
todo, known = [], 0
for k, hrefs in groups.items():
    read = [h for h in hrefs if h in det]
    if any(fits(det[h]) for h in read):
        known += 1; continue
    if len(read) >= 4 or len(read) == len(hrefs):
        continue
    # spread: pick the unread site farthest (by list position) from the ones already read
    unread = [h for h in hrefs if h not in det]
    pos = {h: i for i, h in enumerate(hrefs)}
    taken = [pos[h] for h in read] or [-10 ** 6]
    todo.append(max(unread, key=lambda h: min(abs(pos[h] - t) for t in taken)))
json.dump(todo, open(sys.argv[1], "w"))
print(len(groups), "groups;", known, "with a fitting site;", len(todo), "more reads")
