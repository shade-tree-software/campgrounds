#!/usr/bin/env python3
"""Read Campendium's camper-reported rates for parks with no operator web page (2026-10-17).

    python3 -I audit/price_research/camper_2026-10-17/cpd_read.py CANDIDATES.json OUT.jsonl [--limit N]

AWH 2026-10-11: a dated (2024+) camper report may price an entry only when the operator has no web page
(feedback_camper_report_rates). candidates.json holds the private unpriced entries whose website field
names nothing but Facebook / directory / aggregator pages.

Campendium's search page answers 404 now, but campendium.com/<slug> still redirects to the place page on
maps.campendium.com. So each park tries a few slugs built from its name, and a page is accepted ONLY when
its own coordinates lie within MATCH_KM of our pin (names repeat across states; a slug hit is not a match).
Per accepted page: the "Last Nightly Rate $X Reported M/D/YY" header, every review's date and Nightly Rate,
and any closure wording. One JSON line per park, written as it is read, so a rerun resumes. Plain HTTP,
one request per PAUSE seconds.
"""
import html, json, math, os, re, sys, time, urllib.request, urllib.error

PAUSE = 1.5
MATCH_KM = 3.0
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"


def slugify(s):
    s = s.lower().replace("&", " and ").replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def slugs(name):
    base = re.sub(r"\s*\([^)]*\)", "", name).strip()
    out = [slugify(base), slugify(base.replace("&", " "))]
    if "rv" not in base.lower() and "camp" not in base.lower():
        out.append(slugify(base + " RV Park"))
    out.append(slugify(re.sub(r"(?i)\b(rv|campground|camping|resort|park|and|&)\b", " ", base)))
    seen, res = set(), []
    for s in out:
        if s and s not in seen:
            seen.add(s); res.append(s)
    return res[:4]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.geturl(), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return None, str(e.code)
    except Exception as e:
        return None, "ERR " + str(e)[:80]


def text_of(page):
    s = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", "", page)
    t = html.unescape(re.sub(r"<[^>]+>", "|", s))
    return re.sub(r"\s*\|[\s|]*", " | ", t)


def km(a, b):
    la1, lo1 = a; la2, lo2 = b
    x = math.radians(lo2 - lo1) * math.cos(math.radians((la1 + la2) / 2))
    y = math.radians(la2 - la1)
    return 6371 * math.hypot(x, y)


MON = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"


def parse(t):
    rec = {}
    m = re.search(r"\| ([^|]+) \| View on map", t)
    m = re.search(r"\| (-?\d{1,2}\.\d+), (-?\d{1,3}\.\d+) \|", t)
    if m:
        rec["coords"] = [float(m.group(1)), float(m.group(2))]
    m = re.search(r"\| -?\d{1,2}\.\d+, -?\d{1,3}\.\d+ \|(.*?)\| View on map", t)
    if m:
        rec["links"] = [x.strip() for x in m.group(1).split("|") if x.strip()]
    m = re.search(r"Last Nightly Rate \| (\$[\d,.]+) \| Reported (\d+/\d+/\d+)", t)
    if m:
        rec["last_rate"] = [m.group(1), m.group(2)]
    m = re.search(r"Longest Vehicle Reported \| ([\d.]+ ft) \| Reported (\d+/\d+/\d+)", t)
    if m:
        rec["longest"] = [m.group(1), m.group(2)]
    revs = []
    for m in re.finditer(r"\| (" + MON + r" \d{2}, \d{4}) \| (.*?)(?=\| " + MON + r" \d{2}, \d{4} \||$)", t):
        body = m.group(2)
        r = {"date": m.group(1)}
        mm = re.search(r"Nightly Rate \| (\$[\d,.]+)", body)
        if mm:
            r["rate"] = mm.group(1)
        r["text"] = body.split("| Access |")[0][:400].strip(" |")
        revs.append(r)
    rec["reviews"] = revs
    closed = re.findall(r"(?i)[^|]{0,60}(?:permanently closed|temporarily closed|is closed|now closed|no longer)[^|]{0,60}", t)
    if closed:
        rec["closed_text"] = closed[:4]
    return rec


def main():
    cands = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 10 ** 9
    done = set()
    if os.path.exists(out):
        done = {json.loads(l)["id"] for l in open(out)}
    n = 0
    for c in cands:
        if c["id"] in done or n >= limit:
            continue
        pin = tuple(float(v) for v in c["location"].split(","))
        rec = {"id": c["id"], "name": c["name"], "state": c["state"], "tried": []}
        for s in slugs(c["name"]):
            url, page = fetch("https://www.campendium.com/" + s)
            time.sleep(PAUSE)
            if not url or "maps.campendium.com" not in url:
                rec["tried"].append([s, page if not url else url[:80]])
                continue
            t = text_of(page)
            p = parse(t)
            d = km(pin, p["coords"]) if p.get("coords") else None
            rec["tried"].append([s, url, None if d is None else round(d, 2)])
            if d is not None and d <= MATCH_KM:
                rec.update(p, url=url, km=round(d, 2))
                break
        with open(out, "a") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        n += 1
        print(c["id"], c["state"], c["name"][:40], "->", rec.get("url", "no match")[-60:], rec.get("last_rate"), flush=True)


if __name__ == "__main__":
    main()
