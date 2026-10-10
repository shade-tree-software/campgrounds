#!/usr/bin/env python3
"""Turn the reservable PA state forest sites missing from the database into
candidate entries, one per 1 km cluster (AWH 2026-10-10).

    python3 audit/pa_sf_dispersed/build.py

Reads gap.json + ra_sites.jsonl, applies the inclusion gate per site (Drive-In,
RV/Trailer category, Max Vehicle Length >= 23 ft, and none of the site-page
limitations that rule a 23-ft RV out), clusters what survives within 1 km per
forest, and writes candidates.json (entries without id/elevation/waterfront)
and excluded.json (each dropped site with its reason).
"""
import json, math, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
RA = "https://pennsylvaniastateparks.reserveamerica.com"
DCNR = "https://www.pa.gov/agencies/dcnr/recreation/where-to-go/state-forests/find-a-forest/{slug}"
CLUSTER_KM = 1.0

# Site-page text that rules a 23-ft RV out (checked against Limitation /
# Caution / Description; the forest-wide "some roads require 4WD" boilerplate
# in Directions is deliberately not a reason).
EXCLUDE = [
    (r"(?i)tent[- ]only|tent only|tent and truck camping only", "tent-only site"),
    (r"(?i)limited to campers with a horse", "equine-only Memorial Day-Oct 31"),
    (r"(?i)restricted to hang gliders", "hang-gliders only May-Oct"),
    (r"(?i)limited to ATV riders", "ATV riders only in summer"),
    (r"(?i)tent and small RV", "tent and small RV only"),
    (r"(?i)REQUIRE a four-wheel|four-wheel drive and high clearance is recommended|4x4 recommended",
     "agency says 4WD/4x4 needed"),
    (r"(?i)not recommended for camper trailers|camper trailers are not recommended", "trailers not recommended"),
]
CAVEATS = [
    (r"(?i)not recommended for low-clearance|requiring high-clearance", "rough access: high clearance advised"),
    (r"(?i)Iron Bridge", "Rock Run Road's Iron Bridge is closed: reach it from the far side"),
    (r"(?i)closed annually from December 15 to April 30", "road and sites closed Dec 15-Apr 30 (ski trail)"),
    (r"(?i)Some Bald Eagle State Forest roads require 4WD", "some Bald Eagle SF roads need 4WD: check the route"),
    (r"(?i)not designed for such use", "RVs allowed but the site was not designed for them: check its dimensions"),
]


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def num(s):
    m = re.search(r"\d+", s or "")
    return int(m.group()) if m else None


def text(s):
    return " ".join(str(s.get(k) or "") for k in
                    ("Limitation", "Limitations", "Caution", "Description", "Equipment", "Notice", "NOTICE",
                     "Closures", "Access Alert", "Directions"))


def main():
    sites = {json.loads(l)["site_id"]: json.loads(l) for l in open(os.path.join(HERE, "ra_sites.jsonl"))}
    gap = json.load(open(os.path.join(HERE, "gap.json")))
    keep, excluded = [], []
    for g in gap:
        s = sites[g["site_id"]]
        why = None
        if s.get("Site Access") != "Drive-In":
            why = f"access {s.get('Site Access')}"
        elif not re.search(r"RV|Trailer", s.get("Looking For Category") or ""):
            why = f"category {s.get('Looking For Category')}"
        elif (num(s.get("Max Vehicle Length")) or 0) < 23:
            why = f"max vehicle length {s.get('Max Vehicle Length') or 'not given'}"
        else:
            t = text(s)
            why = next((r for p, r in EXCLUDE if re.search(p, t)), None)
        if why:
            excluded.append({"forest": s["forest"], "site": s["Site, Loop"], "site_id": s["site_id"], "reason": why})
            continue
        s["_ll"] = tuple(g["ll"])
        keep.append(s)
    # single-linkage clusters within a forest
    par = list(range(len(keep)))

    def root(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    for i in range(len(keep)):
        for j in range(i):
            if keep[i]["park_id"] == keep[j]["park_id"] and km(keep[i]["_ll"], keep[j]["_ll"]) <= CLUSTER_KM:
                par[root(i)] = root(j)
    groups = {}
    for i, s in enumerate(keep):
        groups.setdefault(root(i), []).append(s)
    out = []
    for members in groups.values():
        members.sort(key=lambda s: s["Site, Loop"])
        forest = members[0]["forest"]
        pid = members[0]["park_id"]
        clat = sum(s["_ll"][0] for s in members) / len(members)
        clng = sum(s["_ll"][1] for s in members) / len(members)
        pin = min(members, key=lambda s: km(s["_ll"], (clat, clng)))
        labels = [s["Site, Loop"].split(", ")[0] for s in members]
        loops = list(dict.fromkeys(s["Site, Loop"].split(", ", 1)[-1] for s in members))
        area = " / ".join(loops)
        if len(members) == 1:
            name = f"{forest} State Forest Campsite {labels[0]} ({area})"
        elif all(re.search(r"(?i)campground|camping area|CCC camp|parking area", l) for l in loops):
            name = f"{area} ({forest} State Forest)"
        else:
            name = f"{forest} State Forest Campsites {', '.join(labels)} ({area})"
        lens = sorted({num(s["Max Vehicle Length"]) for s in members})
        surf = sorted({s.get("Driveway Surface") or "?" for s in members})
        caveats = list(dict.fromkeys(c for s in members for p, c in CAVEATS if re.search(p, text(s))))
        water = [f"{s['Site, Loop'].split(', ')[0]} {s['Distance to Lake/Stream']}" for s in members
                 if s.get("Distance to Lake/Stream")]
        descr = [f"{s['Site, Loop'].split(', ')[0]}: {s['Description'][:160]}" for s in members if s.get("Description")]
        out.append({
            "forest": forest, "park_id": pid,
            "site_ids": [s["site_id"] for s in members], "labels": labels,
            "site_lls": [list(s["_ll"]) for s in members],
            "name": name, "location": f"{pin['_ll'][0]:.5f},{pin['_ll'][1]:.5f}",
            "max_len": lens, "surfaces": surf, "caveats": caveats,
            "ra_water": water, "descriptions": descr,
            "status": sorted({s["Status"] for s in members}),
            "pull_through": any("Pull-Through" in (s.get("Driveway Entry") or "") for s in members),
        })
    out.sort(key=lambda c: (c["forest"], c["name"]))
    json.dump(out, open(os.path.join(HERE, "candidates.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(excluded, open(os.path.join(HERE, "excluded.json"), "w"), indent=1, ensure_ascii=False)
    print(f"{len(keep)} sites kept in {len(out)} clusters; {len(excluded)} gap sites excluded")
    from collections import Counter
    print(Counter(e["reason"].split(" ")[0] if e["reason"].startswith(("access", "category", "max")) else e["reason"]
                  for e in excluded).most_common())


if __name__ == "__main__":
    main()
