#!/usr/bin/env python3
"""Re-check the US private-gap entries admitted without a rate read on their own site (2026-10-12).

    python3 -I audit/us_private_recheck/scan.py [--limit N] [--ids 1,2,3]
    python3 -I audit/us_private_recheck/scan.py --report [--ids ...]

The 2026-10-01..07 US private gap admitted 125 parks (ids.json) on RV Life's price tier, a Google
listing or an operator page nobody read a rate from. The same screen in Canada let through a
closed park, a dead domain, a seasonal-only resort and a tent-only area. This is the Canada
re-check's scan (audit/canada_recheck/scan.py) pointed at those ids: it reads the home page and
up to 6 same-site pages whose link mentions FAQ / rates / camping / sites / booking / rules, and
keeps the lines that say closed, sold, seasonal-only, members-only, tent-only, monthly-only,
age-restricted, login-walled or a minimum stay, the lines that count sites, the lines that carry
a dollar rate, and how often the pages talk about seasonal versus nightly camping.

Results go to scan_2026-10-12.json after every entry, keyed by id, so a rerun skips what is
done. Plain urllib only: an entry whose pages come back empty or refused gets `browser: true`
and is read through the one-browser driver instead (audit/private_gap_browser/README.md).
"""
import argparse, gzip, html, json, os, re, ssl, subprocess, sys, tempfile, time, urllib.parse, urllib.request, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "scan_2026-10-12.json")
IDS = os.path.join(HERE, "ids.json")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8", "Accept-Encoding": "gzip, deflate",
      "Accept-Language": "en-US,en;q=0.9"}

SIGNALS = {
    "closed": r"permanently closed|closed permanently|no longer (?:be )?(?:operat|open|accept|offer)|ceased (?:operat|business)"
              r"|will not (?:re)?open|won.t (?:re)?open|not (?:be )?open(?:ing)? (?:in|for|this) (?:20\d\d|season|year)"
              r"|closed for (?:the )?20\d\d|temporarily closed|closed until|ferm[ée]e?s? d[ée]finitivement|fermeture (?:d[ée]finitive|temporaire)"
              r"|ne (?:sera|seront) pas ouverts?|ne rouvrira pas|n.ouvrira pas|cess[ée] (?:ses |nos )?(?:activit|op[ée]ration)|cessation",
    "sold": r"\bsold\b(?! out)|new owners?\b|under new (?:ownership|management)|for sale\b|\b[àa] vendre\b|\bvendu\b"
            r"|nouveaux? propri[ée]taires?|nouvelle (?:direction|administration)",
    "dead": r"domain (?:is )?for sale|buy this domain|parked (?:free|domain)|hugedomains|sedo\.com|dan\.com|afternic"
            r"|account (?:has been )?suspended|(?:site|website) (?:is )?(?:suspended|unavailable|expired)|coming soon|under construction",
    "seasonal_only": r"seasonals? (?:sites? |campers? |camping )?only|only seasonals?|no (?:overnight|nightly|transient|daily|short[- ]term)"
                     r"|not open to the (?:general )?public|members? only|members? and (?:their )?guests|friends and family of"
                     r"|private (?:campground|park|resort)|by invitation|waiting list|wait list|waitlist|full for the (?:20\d\d )?season"
                     r"|saisonniers? seulement|(?:seulement|uniquement) (?:des |aux )?(?:terrains |sites |emplacements )?saisonniers"
                     r"|aucun (?:terrain|emplacement|site)s? (?:pour )?(?:les )?(?:voyageurs?|journaliers?|passants?|de passage)"
                     r"|pas de (?:terrains? |sites? )?(?:voyageurs?|journaliers?|passants?|de passage)|liste d.attente"
                     r"|complet pour la saison|membres? seulement|r[ée]serv[ée]s? aux membres|camping priv[ée]",
    "tent_only": r"tents? only|tent camping only|tent sites only|only tents?\b|no (?:rvs?|trailers?|campers?|motorhomes?|motor homes)\b"
                 r"|(?:rvs?|trailers?) (?:are )?not (?:permitted|allowed|accepted)|cars are not permitted|walk[- ]in (?:sites? )?only"
                 r"|hike[- ]in|boat[- ]in|canoe[- ]in|paddle[- ]in|glamping only|tentes? seulement|uniquement (?:pour )?(?:les )?tentes"
                 r"|pas de (?:vr|roulottes?|caravanes?|motoris[ée]s?|v[ée]hicules? r[ée]cr[ée]atifs?)\b|aucun (?:vr|v[ée]hicule r[ée]cr[ée]atif|roulotte)",
    "monthly_only": r"monthly (?:only|rentals? only|stays? only|sites? only)|(?:only|just) (?:monthly|long[- ]term)|no (?:daily|nightly|weekly|short[- ]term)"
                    r"|(?:1|one|30)[- ](?:month|day) minimum|minimum (?:stay )?(?:of )?(?:1|one) month|long[- ]term (?:stays? )?only|extended stays? only"
                    r"|not (?:accepting|taking) (?:overnight|nightly|daily|short)",
    "age": r"55\s?\+|55 (?:and|&) (?:older|over|up)|age[- ]restricted|adults? only|adult[- ]only|21\s?\+|no (?:children|kids)",
    "login": r"log ?in to (?:see|view|book|reserve)|must (?:be )?(?:a )?(?:member|logged in)|members? log ?in|create an account to|sign in to (?:see|view|book)",
    "min_stay": r"(?:minimum|min\.?) (?:stay |booking |reservation |of |de )*(?:2|3|4|5|6|7|14|two|three|four|five|seven|fourteen|deux|trois|quatre|cinq|sept)[- ]?(?:nights?|nuits?|nuit[ée]es?)"
                r"|(?:2|3|4|5|7|14|two|three|four|five|seven|deux|trois)[- ](?:nights?|nuits?) (?:minimum|min)|s[ée]jour minimum|minimum stay",
}
SIGNALS = {k: re.compile(v, re.I) for k, v in SIGNALS.items()}
NOT_SALE = re.compile(r"roulotte|trailer|camper|motorhome|park model|mod[èe]le|firewood|\bbois\b|glace|\bice\b|propane|bait|app[âa]t|t-shirt|souvenir", re.I)
COUNT = re.compile(r"\b\d{2,4}\s+(?:terrains|emplacements|sites|campsites|lots|spaces|places)\b", re.I)
SEASONAL = re.compile(r"saisonn|seasonal", re.I)
RATE = re.compile(r"\$\s?\d{2,3}(?:\.\d\d)?")
RATEWORD = re.compile(r"night|daily|\bday\b|/\s?nt|per (?:site|unit)|\brv\b|full hook|\bfhu\b|w/e|water|electric|30\s?a|50\s?a|weekly|week|monthly|month|site|rate|tent|back[- ]in|pull[- ]thr", re.I)
TRAVELLER = re.compile(r"voyageur|passant|de passage|transient|overnight|nightly|per night|par nuit|/\s?nuit|la nuit|nuit[ée]e|daily|journalier", re.I)
LINKWORD = re.compile(r"faq|question|tarif|rate|price|prix|camping|terrain|emplacement|site|r[ée]serv|reserv|book|r[èe]gle|rule|polic|politique|info|saison|seasonal|voyageur|about|propos|service|rv\b|vr\b", re.I)
SKIPLINK = re.compile(r"(?i)\.(jpe?g|png|gif|webp|svg|zip|mp4|docx?)(\?|$)|facebook|twitter|instagram|youtube|tiktok|pinterest|mailto:|tel:|javascript:|wp-login|/cart|/panier|/feed")
ENGINE = re.compile(r"campspot|newbook|reservationpleinair|reservationcamping|reservpro|rms(?:cloud|north)|camplife|roverpass|letscamp"
                    r"|resnexus|checkfront|fareharbor|firefly|bookingcenter|innroad|webrez|staylist|campertunity|hipcamp|campable|elcampo|parkbridge", re.I)


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    try:
        r = urllib.request.urlopen(req, timeout=20)
    except urllib.error.URLError as e:
        if isinstance(getattr(e, "reason", None), ssl.SSLError):
            r = urllib.request.urlopen(req, timeout=20, context=ssl._create_unverified_context())
        else:
            raise
    with r:
        data = r.read(4_000_000)
        enc = r.headers.get("Content-Encoding", "")
        if enc == "gzip":
            data = gzip.decompress(data)
        elif enc == "deflate":
            data = zlib.decompress(data, -zlib.MAX_WBITS)
        return r.geturl(), r.status, data, r.headers.get("Content-Type", "")


def decode(data, ctype):
    m = re.search(r"charset=([\w-]+)", ctype) or re.search(rb'<meta[^>]+charset=["\']?([\w-]+)', data[:4000], re.I)
    cs = m.group(1) if m else None
    cs = cs.decode() if isinstance(cs, bytes) else cs
    for c in ([cs] if cs else []) + ["utf-8", "cp1252"]:
        try:
            return data.decode(c)
        except (LookupError, UnicodeDecodeError):
            continue
    return data.decode("utf-8", "replace")


def text_lines(raw):
    t = re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>|<svg.*?</svg>", " ", raw)
    t = re.sub(r"(?i)<(br|p|li|tr|h\d|div|td|th|section|article|header|footer)[^>]*>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return [re.sub(r"\s+", " ", l).strip() for l in t.split("\n") if l.strip()]


def pdf_lines(data):
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(data)
        f.flush()
        try:
            out = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, timeout=60).stdout
        except Exception:
            return []
    return [re.sub(r"\s+", " ", l).strip() for l in out.decode("utf-8", "replace").split("\n") if l.strip()]


def site_of(u):
    return urllib.parse.urlparse(u).netloc.lower().removeprefix("www.")


def read_page(url):
    """-> (page record, raw html or '')"""
    rec = {"url": url}
    try:
        final, status, data, ctype = fetch(url)
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {str(e)[:120]}"
        return rec, "", []
    rec.update(final=final, status=status)
    if "pdf" in ctype or final.lower().split("?")[0].endswith(".pdf"):
        return rec, "", pdf_lines(data)
    raw = decode(data, ctype)
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", raw)
    rec["title"] = html.unescape(re.sub(r"\s+", " ", m.group(1))).strip()[:120] if m else ""
    return rec, raw, text_lines(raw)


def scan_lines(lines, hits, counts):
    for i, l in enumerate(lines):
        if len(l) > 1500:
            l = l[:1500]
        for k, rx in SIGNALS.items():
            for m in rx.finditer(l):
                s = l[max(0, m.start() - 110): m.end() + 110]
                if k == "sold" and NOT_SALE.search(l[max(0, m.start() - 45): m.end() + 45]):
                    continue  # trailers, firewood or ice for sale, not the park
                if s not in hits.setdefault(k, []) and len(hits[k]) < 8:
                    hits[k].append(s)
        if RATE.search(l) and len(hits.setdefault("rates", [])) < 16:
            # a bare price in a table cell takes its label from the line before it
            r = l[:300] if RATEWORD.search(l) else (f"{lines[i-1][:140]} | {l[:150]}" if i and RATEWORD.search(lines[i-1]) else "")
            if r and r not in hits["rates"]:
                hits["rates"].append(r)
        if COUNT.search(l) and len(l) < 300 and len(hits.setdefault("counts", [])) < 10 and l not in hits["counts"]:
            hits["counts"].append(l)
        counts["seasonal"] += len(SEASONAL.findall(l))
        counts["traveller"] += len(TRAVELLER.findall(l))


def scan_entry(e):
    urls = (e.get("website") or "").split()
    res = {"id": e["id"], "name": e["name"], "state": e["state"], "checked": time.strftime("%Y-%m-%d"),
           "pages": [], "signals": {}, "mentions": {"seasonal": 0, "traveller": 0}, "engines": [], "chars": 0}
    if not urls:
        res["no_website"] = True
        return res
    seen, queue = set(), [(u, 0) for u in urls]
    home_site = site_of(urls[0])
    while queue and len(res["pages"]) < 7:
        url, depth = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        rec, raw, lines = read_page(url)
        rec["lines"] = len(lines)
        res["pages"].append(rec)
        res["chars"] += sum(len(l) for l in lines)
        if depth == 0 and rec.get("final") and site_of(rec["final"]) != home_site:
            res["moved_to"] = rec["final"]
        scan_lines(lines, res["signals"], res["mentions"])
        if not raw:
            continue
        base = rec.get("final") or url
        links = []
        for href, label in re.findall(r'(?is)<a[^>]+href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', raw):
            u = urllib.parse.urljoin(base, html.unescape(href).strip())
            if not u.startswith("http") or SKIPLINK.search(u):
                continue
            if ENGINE.search(u) and site_of(u) not in res["engines"]:
                res["engines"].append(site_of(u))
            if site_of(u) != site_of(base) or u in seen or depth:
                continue
            label = re.sub(r"<[^>]+>|\s+", " ", label).strip()
            score = len(LINKWORD.findall(label + " " + urllib.parse.urlparse(u).path))
            if re.search(r"faq|question|r[èe]gle|rule|polic|politique|tarif|rate|price|prix", label + " " + u, re.I):
                score += 3
            if score:
                links.append((score, u))
        for _, u in sorted(set(links), key=lambda x: -x[0])[:6]:
            queue.append((u, depth + 1))
        time.sleep(0.4)
    res["signals"] = {k: v for k, v in res["signals"].items() if v}
    res["browser"] = res["chars"] < 1500 or all("error" in p for p in res["pages"])
    return res


def worklist(ids=None):
    rows = json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))
    want = set(json.load(open(IDS)))
    out = [r for r in rows if r["id"] in want]
    return [r for r in out if r["id"] in ids] if ids else out


def save(done):
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(done, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, OUT)


def report(done, ids=None):
    for k, r in sorted(done.items(), key=lambda kv: int(kv[0])):
        if ids and int(k) not in ids:
            continue
        flags = sorted(r.get("signals", {}))
        m = r.get("mentions", {})
        extra = []
        if r.get("browser"):
            extra.append("BROWSER")
        if r.get("moved_to"):
            extra.append("MOVED " + r["moved_to"])
        if r.get("no_website"):
            extra.append("NO WEBSITE")
        print(f"{k} {r['state']} {r['name'][:40]:40} chars={r.get('chars',0):6} seas={m.get('seasonal',0):3} trav={m.get('traveller',0):3} "
              f"{','.join(f for f in flags if f not in ('counts', 'rates'))} rates={len(r.get('signals', {}).get('rates', []))} {' '.join(extra)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--ids")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--redo", action="store_true", help="rescan ids already in the results")
    a = ap.parse_args()
    ids = {int(x) for x in a.ids.split(",")} if a.ids else None
    done = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    if a.report:
        report(done, ids)
        return
    todo = [e for e in worklist(ids) if a.redo or str(e["id"]) not in done]
    print(f"{len(todo)} to scan, {len(done)} already done", flush=True)
    for n, e in enumerate(todo[: a.limit] if a.limit else todo, 1):
        r = scan_entry(e)
        done[str(e["id"])] = r
        save(done)
        print(n, e["id"], e["state"], e["name"][:40], "chars", r["chars"], sorted(r["signals"]), "BROWSER" if r.get("browser") else "", flush=True)


if __name__ == "__main__":
    main()
