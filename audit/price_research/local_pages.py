"""Read the web pages of unpriced LOCAL entries for posted camping fees (2026-10-15, AWH #10).
    python3 -I local_pages.py ST OUT.jsonl [--limit N] [--ids a,b]
Resumable (ids in OUT are skipped). For each entry: every website URL except social media, plus up to 4
same-site links whose href or text mentions camp/rv/rate/fee/reserv; for each page, every '$<digit>' with
~200 chars of context. Plain HTTP, one request a second. Nothing is written to campgrounds.json; the
findings are hand-built from OUT."""
import html, json, os, re, sys, time, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKIP = re.compile(r"facebook\.com|instagram\.com|twitter\.com|x\.com/|youtube\.com|tripadvisor|google\.", re.I)
LINK = re.compile(r"camp|rv|rate|fee|reserv|price|lodging", re.I)


def get(u):
    time.sleep(1)
    r = urllib.request.urlopen(urllib.request.Request(u, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36"}), timeout=30)
    b = r.read(3_000_000)
    ct = r.headers.get("Content-Type", "")
    if "pdf" in ct:
        return r.geturl(), "", True
    return r.geturl(), b.decode("utf-8", "replace"), False


def text(t):
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>|<!--.*?-->", " ", t)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</tr>|</h\d>|</td>", " | ", t, flags=re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()


def dollars(x):
    out, last = [], -999
    for m in re.finditer(r"\$\s?\d", x):
        if m.start() - last < 120:
            continue
        last = m.start()
        out.append(x[max(0, m.start() - 220):m.start() + 200])
    return out[:20]


def page(u):
    url, t, pdf = get(u)
    if pdf:
        return {"url": url, "pdf": True}, []
    host = urllib.parse.urlparse(url).netloc
    links = []
    for href, label in re.findall(r'<a[^>]+href="([^"#]+)"[^>]*>(.*?)</a>', t, re.S | re.I):
        a = urllib.parse.urljoin(url, html.unescape(href))
        if urllib.parse.urlparse(a).netloc != host or a.rstrip("/") == url.rstrip("/"):
            continue
        lab = text(label)[:60]
        if (LINK.search(urllib.parse.urlparse(a).path) or LINK.search(lab)) and a not in [l[0] for l in links]:
            links.append((a, lab))
    return {"url": url, "lines": dollars(text(t))}, links


def main():
    st, out = sys.argv[1], sys.argv[2]
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 10 ** 6
    only = {int(x) for x in sys.argv[sys.argv.index("--ids") + 1].split(",")} if "--ids" in sys.argv else None
    done = {json.loads(l)["id"] for l in open(out)} if os.path.exists(out) else set()
    sys.path.insert(0, ROOT)
    import campground_schema as cs
    reg = json.load(open(os.path.join(ROOT, "campground_policies.json")))
    db = json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))
    todo = [r for r in db if r.get("kind") == "campground" and r["ownership"] == "local" and r["state"] == st
            and not r.get("fees") and not cs.resolve(r, reg).get("fees") and r["id"] not in done
            and (only is None or r["id"] in only)]
    print(len(todo), "to read", flush=True)
    for r in todo[:limit]:
        rec = {"id": r["id"], "name": r["name"], "read": time.strftime("%Y-%m-%d"), "pages": []}
        seen = set()
        for u in [x.strip() for x in (r.get("website") or "").split("\n") if x.strip() and not SKIP.search(x)]:
            try:
                p, links = page(u)
            except Exception as e:
                rec["pages"].append({"url": u, "error": repr(e)[:160]})
                continue
            rec["pages"].append(p)
            seen.add(p["url"])
            for a, lab in links[:4]:
                if a in seen:
                    continue
                seen.add(a)
                try:
                    q, _ = page(a)
                    q["via"] = lab
                    rec["pages"].append(q)
                except Exception as e:
                    rec["pages"].append({"url": a, "error": repr(e)[:160]})
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(r["id"], r["name"][:34], "|", sum(len(p.get("lines", [])) for p in rec["pages"]), "lines,",
              len(rec["pages"]), "pages", flush=True)


if __name__ == "__main__":
    main()
