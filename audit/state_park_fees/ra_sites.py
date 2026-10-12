"""Save every site of each classic ReserveAmerica park that an unpriced state entry links to.

    python3 -I ra_sites.py --states NH,VT,RI,CT DIR

One park at a time (ra_list.park, plain urllib), written to DIR/<contract>_<parkId>.json, so a
rerun skips the parks already saved. Then prints each park's site types with counts."""
import collections, json, os, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ra_list  # noqa: E402
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

states = sys.argv[sys.argv.index("--states") + 1].split(",")
out = sys.argv[-1]
os.makedirs(out, exist_ok=True)
rows = json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))
reg = json.load(open(os.path.join(ROOT, "campground_policies.json"), encoding="utf-8"))


def rated(e):
    f = (cs.resolve(e, reg).get("fees") or {}).get("values", {})
    return "nightly_low" in f or "nightly_high" in f


todo = {}
for e in rows:
    if e.get("kind") != "campground" or e.get("ownership") != "state" or e["state"] not in states or rated(e):
        continue
    u = next((w for w in (e.get("website") or "").split() if "parkId=" in w and "contractCode=" in w), None)
    if not u:
        print("no classic RA link:", e["id"], e["name"])
        continue
    cc = re.search(r"contractCode=(\w+)", u).group(1)
    pid = re.search(r"parkId=(\d+)", u).group(1)
    todo.setdefault((cc, pid), {"url": u, "ids": []})["ids"].append(e["id"])
for (cc, pid), t in sorted(todo.items()):
    path = os.path.join(out, f"{cc}_{pid}.json")
    if not os.path.exists(path):
        try:
            d = ra_list.park(t["url"])
        except Exception as x:  # noqa: BLE001 - report and go on to the next park
            print("FAILED", cc, pid, t["ids"], x)
            continue
        d["entry_ids"] = t["ids"]
        json.dump(d, open(path, "w"), indent=1)
        time.sleep(1)
    d = json.load(open(path))
    c = collections.Counter(r["cells"][1] if len(r["cells"]) > 1 else "?" for r in d["sites"])
    print(f"{cc} {pid} ids {t['ids']}: {len(d['sites'])} sites {dict(c)}", flush=True)
