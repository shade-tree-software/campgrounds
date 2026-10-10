#!/usr/bin/env python3
"""Digest the dollar figures on unpriced entries' own websites (2026-10-10).

    python3 audit/price_research/site_digest.py --state WI --ownership local OUT.txt
    python3 audit/price_research/site_digest.py --ids 123,456 OUT.txt

For each entry still without a price (no fees after registry inheritance, no RV
Life price_tier) it fetches every URL in `website`, then up to 3 same-site
links whose text or href says rate/fee/price/camp/reserv/tarif, and prints the
lines that carry a money figure (with a little context). Read by hand: a
finding needs the operator's own page, and the digest shows each URL so the
source can be cited. Plain urllib only; a page that needs JS shows as empty.
"""
import argparse, gzip, html, json, os, re, sys, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,*/*;q=0.8", "Accept-Encoding": "gzip",
      "Accept-Language": "en-US,en;q=0.9,fr;q=0.7"}
MONEY = re.compile(r"(\$\s?\d[\d,]*(\.\d\d)?|\d[\d,]*(,\d\d|\.\d\d)?\s?\$|\bCAD\b)")
LINKWORD = re.compile(r"(?i)rate|fee|price|pricing|camp|reserv|tarif|prix|rv|site")
SKIPLINK = re.compile(r"(?i)\.(jpg|png|gif|zip)$|facebook|twitter|instagram|mailto:|tel:|javascript:|zoning|court|"
                      r"probate|clerk|planning|tax|licens|health|breast|treasur|register-of|deeds|election|"
                      r"employ|job|career|bid|agenda|minutes|permit-fee|division-fees|misc-fees")


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        data = r.read(3_000_000)
        if r.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
        ctype = r.headers.get("Content-Type", "")
        return r.geturl(), data, ctype


def text_of(raw):
    t = re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>", " ", raw)
    t = re.sub(r"(?i)<(br|p|li|tr|h\d|div|td|th)[^>]*>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return [re.sub(r"\s+", " ", l).strip() for l in t.split("\n") if l.strip()]


def pdf_text(data):
    import subprocess, tempfile
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(data)
        f.flush()
        try:
            out = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, timeout=60).stdout
        except Exception:
            return []
    return [re.sub(r"\s+", " ", l).strip() for l in out.decode("utf-8", "replace").split("\n") if l.strip()]


def money_lines(lines, cap=40):
    out = []
    for i, l in enumerate(lines):
        if MONEY.search(l) and len(l) < 400:
            ctx = lines[i - 1] if i and len(lines[i - 1]) < 120 and not MONEY.search(lines[i - 1]) else ""
            out.append((ctx + " | " if ctx else "") + l)
    return out[:cap]


def digest(url, depth=0, seen=None):
    seen = seen if seen is not None else set()
    if url in seen or len(seen) > 5:
        return []
    seen.add(url)
    try:
        final, data, ctype = fetch(url)
    except Exception as e:
        return [f"  [{url}] ERROR {str(e)[:80]}"]
    if "pdf" in ctype or final.lower().endswith(".pdf"):
        lines = pdf_text(data)
    else:
        raw = data.decode("utf-8", "replace")
        lines = text_of(raw)
    title = next((l for l in lines[:5]), "")[:80]
    ml = money_lines(lines)
    if depth and not ml:
        return [f"  [{final}] (no money lines)"]
    out = [f"  [{final}] ({len(lines)} lines) {title}"] + ["      " + l for l in ml]
    if depth == 0 and "pdf" not in ctype:
        host = urllib.parse.urlparse(final).netloc
        links = []
        for href, txt in re.findall(r'(?is)<a[^>]+href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', raw):
            u = urllib.parse.urljoin(final, html.unescape(href))
            label = re.sub(r"<[^>]+>|\s+", " ", txt).strip()
            if SKIPLINK.search(u) or urllib.parse.urlparse(u).netloc != host or u in seen:
                continue
            score = len(re.findall(r"(?i)rate|fee|price|pricing|tarif|prix", label + " " + u)) * 3 + \
                len(LINKWORD.findall(label + " " + u))
            if score >= 3:
                links.append((score, u))
        for _, u in sorted(set(links), reverse=True)[:3]:
            out += digest(u, 1, seen)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--state")
    ap.add_argument("--ownership")
    ap.add_argument("--ids")
    a = ap.parse_args()
    reg = json.load(open(os.path.join(ROOT, "campground_policies.json")))
    reg = reg.get("policies", reg) if isinstance(reg, dict) else reg
    rows = json.load(open(os.path.join(ROOT, "campgrounds.json")))
    ids = {int(x) for x in a.ids.split(",")} if a.ids else None
    todo = []
    for r in rows:
        if r.get("kind") != "campground":
            continue
        if ids is not None:
            if r["id"] in ids:
                todo.append(r)
            continue
        if a.state and r.get("state") != a.state or a.ownership and r.get("ownership") != a.ownership:
            continue
        if (r.get("rating") or {}).get("price_tier") is not None or cs.resolve(r, reg).get("fees"):
            continue
        todo.append(r)
    with open(a.out, "w") as fh:
        for r in todo:
            fh.write(f"=== {r['id']} {r['name']} ({r.get('state')}, {r.get('ownership')})\n")
            fh.write(f"  note: {(r.get('note') or '')[:300]}\n")
            for u in (r.get("website") or "").split():
                if u.startswith("http"):
                    fh.write("\n".join(digest(u)) + "\n")
            fh.flush()
            print(r["id"], flush=True)


if __name__ == "__main__":
    main()
