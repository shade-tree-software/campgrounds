"""Fetch each remaining target's own pages and keep rate snippets (resumable).
    python3 -I pages.py work.txt pages.jsonl"""
import json, os, re, sys, time, html, urllib.request, urllib.parse
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
SUB = re.compile(r"rate|pric|tarif|fee|camping|rv|site|reserv|book|stay|season|terrain|emplacement", re.I)
MONEY = re.compile(r"\$\s?\d|\d\s?\$|\d+[.,]\d\d\s?\$")
def get(u):
    time.sleep(1)
    r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA, "Accept-Language": "en-CA,en;q=0.9,fr;q=0.8"}), timeout=30)
    return r.geturl(), r.read(4_000_000).decode("utf-8", "replace")
def text(t):
    t = re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<!--.*?-->", " ", t)
    t = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</tr>|</h\d>|</td>|</th>|</div>", " | ", t)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()
cg = {e["id"]: e for e in json.load(open("/home/andrew/Dev/campgrounds/campgrounds.json"))}
ids = [int(l.split("|")[0]) for l in open(sys.argv[1]) if l[:1].isdigit()]
out = sys.argv[2]
done = {json.loads(l)["id"] for l in open(out)} if os.path.exists(out) else set()
for i in ids:
    if i in done or i not in cg: continue
    urls = [u for u in re.split(r"\s+", cg[i].get("website") or "") if u.startswith("http") and not re.search(r"facebook|campspot|resnexus|camplife|firefly|newbook|rmscloud", u)]
    rec = {"id": i, "pages": [], "err": []}
    seen = set(); queue = list(urls[:2])
    while queue and len(rec["pages"]) < 7:
        u = queue.pop(0)
        if u in seen: continue
        seen.add(u)
        try:
            fu, t = get(u)
        except Exception as ex:
            rec["err"].append(f"{u}: {ex}"[:150]); continue
        x = text(t)
        sn = []; last = -999
        for m in MONEY.finditer(x):
            if m.start() - last < 150: continue
            last = m.start(); sn.append(x[max(0, m.start() - 200):m.start() + 160])
        rec["pages"].append({"url": fu, "title": (re.search(r"(?is)<title[^>]*>(.*?)</title>", t) or [None, ""])[1].strip()[:100], "snip": sn[:15]})
        if len(seen) <= 2:
            host = urllib.parse.urlparse(fu).netloc
            for h in re.findall(r'href="([^"#]+)"', t):
                l = urllib.parse.urljoin(fu, html.unescape(h))
                if urllib.parse.urlparse(l).netloc == host and SUB.search(urllib.parse.urlparse(l).path) and not re.search(r"\.(jpg|png|pdf|css|js)$|wp-json|feed|xmlrpc|/tag/|/category/", l, re.I) and l not in seen and l not in queue:
                    queue.append(l)
    with open(out, "a") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(i, len(rec["pages"]), flush=True)
