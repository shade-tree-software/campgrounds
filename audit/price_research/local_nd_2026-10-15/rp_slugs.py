"""Find RoverPass slugs for the ND entries left unpriced: one RoverPass search per entry (name + ', ND'), keep /c/ slugs
ending -nd, match on name words. python3 -I rp_slugs.py > rp_candidates.json"""
import json, os, re, sys, time, urllib.parse, urllib.request
ROOT = os.path.abspath("../../..")
db = [r for r in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))
      if r.get("kind") == "campground" and r["ownership"] == "local" and r["state"] == "ND" and not r.get("fees")]
STOP = {"park", "campground", "city", "recreation", "area", "rv", "the", "and", "of", "county", "lake", "dam", "campgrounds"}
def words(s):
    return {w for w in re.findall(r"[a-z]+", s.lower()) if w not in STOP and len(w) > 2}
out = {}
for r in db:
    q = re.sub(r"\(.*?\)", "", r["name"]) + " ND"
    u = "https://www.roverpass.com/search/?search=" + urllib.parse.quote_plus(q)
    time.sleep(1)
    try:
        t = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 Chrome/140"}), timeout=40).read().decode("utf-8", "replace")
    except Exception as e:
        print(r["id"], "ERR", e, file=sys.stderr); continue
    slugs = sorted(set(re.findall(r"/c/([a-z0-9-]+-nd)\b", t)))
    w = words(r["name"]) | words((r.get("note") or "").split(";")[0][:60])
    hits = [s for s in slugs if words(s.replace("-", " ")) & words(r["name"])]
    out[r["id"]] = {"name": r["name"], "hits": hits}
    print(r["id"], r["name"][:34], hits[:4], file=sys.stderr)
print(json.dumps(out, indent=1))
