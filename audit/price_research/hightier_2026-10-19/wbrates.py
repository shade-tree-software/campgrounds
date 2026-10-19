"""Wayback 2024+ captures of each target's rate-looking pages; print $ snippets (resumable).
    python3 -I wbrates.py targets.json wb.jsonl"""
import json, os, re, sys, time, urllib.parse, urllib.request, html
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gateways
RATE = re.compile(r"rate|pric|fee|camping|rv-?site|reserv|stay", re.I)
SKIP = re.compile(r"facebook|instagram|google|rvlife|goodsam|koa\.com|roverpass|campspot|thousandtrails|sunoutdoors", re.I)
def get(u, t=90):
    for k in range(3):
        try:
            time.sleep(2)
            r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 ekko-research"}), timeout=t)
            return r.read(3_000_000).decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(60); continue
            raise
        except Exception:
            if k == 2: raise
            time.sleep(10)
def text(t):
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>|<!--.*?-->", " ", t)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</tr>|</h\d>|</td>|</div>", " | ", t, flags=re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()
T = json.load(open(sys.argv[1])); out = sys.argv[2]
done = {json.loads(l)["id"] for l in open(out)} if os.path.exists(out) else set()
for t in T:
    if t["id"] in done or "koa" in t["why"]: continue
    if gateways.gateways(*map(float, t["loc"].split(","))): continue
    urls = [u for u in re.split(r"\s+", t["web"]) if u and not SKIP.search(u)]
    rec = {"id": t["id"], "caps": [], "err": []}
    if urls:
        dom = urllib.parse.urlparse(urls[0]).netloc.replace("www.", "")
        try:
            cdx = json.loads(get(f"https://web.archive.org/cdx/search/cdx?url={dom}/*&output=json&from=2024&filter=statuscode:200&filter=mimetype:text/html&collapse=urlkey&fl=timestamp,original&limit=400") or "[]")[1:]
        except Exception as ex:
            cdx = []; rec["err"].append(str(ex)[:120])
        root = [c for c in cdx if urllib.parse.urlparse(c[1]).path in ("", "/")]
        cand = [c for c in cdx if RATE.search(urllib.parse.urlparse(c[1]).path)][:4] + root[:1]
        for ts, orig in cand:
            try:
                # latest 2024+ capture of this exact url
                last = json.loads(get(f"https://web.archive.org/cdx/search/cdx?url={urllib.parse.quote(orig, safe='')}&output=json&from=2024&filter=statuscode:200&fl=timestamp&limit=-1") or "[]")[1:]
                ts = last[-1][0] if last else ts
                x = text(get(f"https://web.archive.org/web/{ts}id_/{orig}"))
                snip = []; lastp = -999
                for m in re.finditer(r"\$\s?\d", x):
                    if m.start() - lastp < 120: continue
                    lastp = m.start(); snip.append(x[max(0, m.start() - 160):m.start() + 140])
                rec["caps"].append({"ts": ts, "url": orig, "snip": snip[:12]})
            except Exception as ex:
                rec["err"].append(f"{orig}: {ex}"[:150])
    with open(out, "a") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(t["id"], len(rec["caps"]), flush=True)
