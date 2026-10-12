"""Illinois: each unpriced state entry's camping page (dnr.illinois.gov/parks/camp/park.<x>.html),
the lines that state its site classes. python3 -I il_classes.py OUT.json"""
import html, json, os, re, sys, time, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
rows = json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))
reg = json.load(open(os.path.join(ROOT, "campground_policies.json"), encoding="utf-8"))
out = {}
for e in rows:
    if e.get("state") != "IL" or e.get("ownership") != "state" or e.get("kind") != "campground":
        continue
    f = (cs.resolve(e, reg).get("fees") or {}).get("values", {})
    if "nightly_low" in f or "nightly_high" in f:
        continue
    m = re.search(r"https://dnr\.illinois\.gov/parks/(?:camp/)?park\.([a-z\-]+)\.html", e.get("website") or "")
    if not m:
        out[e["id"]] = {"name": e["name"], "lines": [], "url": None}
        continue
    url = f"https://dnr.illinois.gov/parks/camp/park.{m.group(1)}.html"
    try:
        t = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60).read().decode("utf-8", "replace")
    except Exception as x:  # noqa: BLE001
        out[e["id"]] = {"name": e["name"], "lines": [f"ERROR {x}"], "url": url}
        continue
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
    t = re.sub(r'(?s)data-cmp-data-layer="[^"]*"|data-[a-z-]+="\{[^"]*\}"', " ", t)
    L = [l for l in (re.sub(r"\s+", " ", x).strip() for x in html.unescape(re.sub(r"<[^>]+>", "\n", t)).split("\n")) if l]
    keep = []
    for l in L:
        if len(l) < 700 and re.search(r"(?i)\bclass\b|premium|electric|\bsites?\b|hook-?up|shower", l) and l not in keep:
            keep.append(l)
    out[e["id"]] = {"name": e["name"], "url": url, "lines": keep[:25]}
    print(e["id"], e["name"], "|", " || ".join(k for k in keep if re.search(r"(?i)class|premium|electric", k))[:600], flush=True)
    time.sleep(0.5)
json.dump(out, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
