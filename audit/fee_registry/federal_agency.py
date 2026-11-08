"""Which federal agency runs each US federal entry (fee-registry step 2, 2026-11-07).

The `federal` registry row is one row for five agencies whose fee rules differ
(the Forest Service and the Corps charge no entrance fee; the Park Service does,
per park). This decides `policy_ref: federal:<agency>` per entry:

  1. the website's domain (fs.usda.gov, usace.army.mil, blm.gov, nps.gov, ...)
  2. a recreation.gov facility link -> RIDB's ORGANIZATION for that facility,
     cached in ridb_orgs.json (resumable; needs RIDB_API_KEY)
  3. otherwise unassigned — the entry keeps inheriting plain `federal`.

Prints a tally; `--write out.json` saves {id: agency} for apply_federal.py.
"""
import json, os, re, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from ridb import fetch_facility as ridb

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "ridb_orgs.json")
CANADA = {"ON", "BC", "AB", "SK", "MB", "QC", "NB", "NS", "PE", "NL", "YT", "NT", "NU"}
DOMAINS = [("fs.usda.gov", "usfs"), ("fs.fed.us", "usfs"), ("landbetweenthelakes.us", "usfs"),
           ("usace.army.mil", "usace"), ("blm.gov", "blm"), ("nps.gov", "nps"),
           ("fws.gov", "fws"), ("usbr.gov", "bor")]
ORGS = {"USFS": "usfs", "USACE": "usace", "BLM": "blm", "NPS": "nps",
        "FWS": "fws", "USFWS": "fws", "BOR": "bor", "TVA": "tva"}


def load_cache():
    try:
        return json.load(open(CACHE))
    except FileNotFoundError:
        return {}


def classify(e, cache):
    w = (e.get("website") or "").lower()
    for d, a in DOMAINS:
        if d in w:
            return a, "domain " + d
    m = re.search(r"recreation\.gov/camping/campgrounds/(\d+)", w)
    if m:
        org = cache.get(m.group(1))
        if org and ORGS.get(org):
            return ORGS[org], "RIDB facility " + m.group(1) + " org " + org
        return None, "rec.gov " + m.group(1) + (" org " + org if org else " (not fetched)")
    return None, "no agency signal"


def main():
    cg = json.load(open(os.path.join(HERE, "..", "..", "campgrounds.json")))
    fed = [e for e in cg if e.get("kind") == "campground" and e.get("ownership") == "federal"
           and e.get("state") not in CANADA]
    cache = load_cache()
    if "--fetch" in sys.argv:
        ids = sorted({m.group(1) for e in fed
                      for m in [re.search(r"recreation\.gov/camping/campgrounds/(\d+)",
                                          (e.get("website") or "").lower())] if m} - set(cache))
        print(len(ids), "facilities to fetch", flush=True)
        for i, fid in enumerate(ids):
            try:
                f = ridb._get(f"facilities/{fid}", {"full": "true"})
                org = ((f.get("ORGANIZATION") or [{}])[0].get("OrgAbbrevName") or "").strip()
            except Exception as ex:  # noqa: BLE001 — a failure stays unfetched, never "no org"
                print("fail", fid, ex, flush=True)
                continue
            cache[fid] = org
            if i % 25 == 0:
                json.dump(cache, open(CACHE, "w"), indent=0, sort_keys=True)
                print(i, flush=True)
            time.sleep(1.3)
        json.dump(cache, open(CACHE, "w"), indent=0, sort_keys=True)
    from collections import Counter
    tally, out, why = Counter(), {}, Counter()
    for e in fed:
        a, reason = classify(e, cache)
        tally[a] += 1
        if a:
            out[str(e["id"])] = a
        else:
            why[reason.split(" ")[0] + " " + reason.split(" ")[-1]] += 1
    print(tally)
    print(why.most_common(10))
    if "--write" in sys.argv:
        json.dump(out, open(sys.argv[sys.argv.index("--write") + 1], "w"), indent=0, sort_keys=True)


if __name__ == "__main__":
    main()
