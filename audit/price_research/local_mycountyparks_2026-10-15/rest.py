"""Third pass: entries priced by neither earlier pass. Fetch <park>/Activity/Camping on mycountyparks and every other
website link on the entry; save dollar-figure context lines. python3 -I rest.py IDS OUT.jsonl"""
import json, re, sys, os, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import read
ids = {int(x) for x in sys.argv[1].split(",")}
db = {r["id"]: r for r in json.load(open(os.path.join(read.ROOT, "campgrounds.json"), encoding="utf-8"))}
park = {}
for l in open("mcp_fees.jsonl"):
    r = json.loads(l)
    park[r["id"]] = re.sub(r"/(Facility|Activity)/.*$", "", (r.get("park_url") or r["src"]).rstrip("/"), flags=re.I)
for i in sorted(ids):
    urls = [park[i] + "/Activity/Camping"] + [u.strip() for u in db[i]["website"].split("\n") if u.strip() and "mycountyparks" not in u]
    rec = {"id": i, "name": db[i]["name"], "pages": []}
    for u in urls:
        try:
            url, t = read.get(u)
            x = read.text(re.sub(r"(?s)<script.*?</script>|<style.*?</style>", "", t))
            lines = [x[max(0, m.start() - 160):m.start() + 140] for m in re.finditer(r"\$\s?\d", x)]
            rec["pages"].append({"url": url, "lines": lines[:12]})
        except Exception as e:
            rec["pages"].append({"url": u, "error": repr(e)[:150]})
    open(sys.argv[2], "a").write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(i, db[i]["name"][:30], [(p["url"][-40:], len(p.get("lines", [])), p.get("error", "")[:40]) for p in rec["pages"]])
