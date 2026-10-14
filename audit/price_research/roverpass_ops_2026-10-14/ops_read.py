"""ops_read.py IDS OUT.jsonl - read the operator's own pages for the RoverPass pass (#8f, 2026-10-14).

IDS is a comma-separated id list. For each entry it fetches every `website` URL that isn't an aggregator listing,
then up to four same-site links whose text or href says rate/fee/price/reserve/book/camp/rv/site, and records for
each page its final URL, title and visible text (scripts, styles and HTML comments dropped - an operator can
comment out an obsolete rate table, Liberty Haven AZ 2026-10-14), plus every phone number on the pages, every link
into a booking engine, and whether the domain is parked or for sale. Plain urllib; a page that needs JavaScript
reads as empty. ops_view.py prints the per-entry digest that was read by hand.
"""
import concurrent.futures as cf, gzip, html as H, json, os, re, sys, time, urllib.parse, urllib.request, zlib
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,*/*;q=0.8", "Accept-Encoding": "gzip, deflate",
      "Accept-Language": "en-US,en;q=0.9"}
AGG = ("roverpass.com", "hipcamp.com", "facebook.com", "campendium", "rvparky", "goodsam", "rvlife", "tripadvisor",
       "yelp.", "google.", "allstays", "thedyrt", "campgroundviews", "campsitecollective", "koa.com", "instagram.com",
       "travelok.com", "visit", "campingroadtrip", "camplinq")
ENGINES = ("campspot.com", "fireflyreservations.com", "newbook", "camplife.com", "staylist.com", "rezexpert.com",
           "campedge", "resnexus.com", "reservemyspot", "checkfront.com", "rmscloud.com", "bookingsrm", "letscamp",
           "setyoursites.com", "hipcamp.com", "roverpass.com", "campgroundreservations", "ireserve", "webreserv",
           "cloudbeds.com", "lodgify.com", "innroad.com", "reserveamerica.com", "usedirect.com", "recreation.gov",
           "campground-reservations", "camp-ez", "campgroundmanager", "secure.campedge", "bookingcenter", "sirvoy",
           "airbnb.com", "vrbo.com", "booking.com", "pitchup.com", "reservations.", "/reserve", "parkrez",
           "bookyoursite", "campgroundbooking", "campsitecloud", "mycampsite", "rvreservations", "campreservations",
           "inngenius", "rezstream", "eviivo", "thinkreservations", "beds24", "littlehotelier", "squareup.com",
           "wix.com/booking", "simplybook", "calendly", "acuityscheduling", "fareharbor", "peek.com", "itsnapp")
PARKED = re.compile(r"(?i)domain (is )?for sale|buy this domain|this domain (may be|is) for sale|parked (free|domain)|"
                    r"hugedomains|sedo\.com|dan\.com|afternic|godaddy\.com/domainsearch|domain has expired|"
                    r"account (has been )?suspended|future home of|website coming soon|under construction")
PHONE = re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?\(?([2-9]\d{2})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})(?!\d)")
LINKWORD = re.compile(r"(?i)rate|fee|price|pricing|tarif|reserv|book|camp|rv|site|stay|accommodation|lodging")


def get(u):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25)
    d = r.read(5_000_000)
    e = r.headers.get("Content-Encoding", "")
    d = gzip.decompress(d) if e == "gzip" else zlib.decompress(d) if e == "deflate" else d
    return r.geturl(), r.headers.get("Content-Type", ""), d


def visible(raw):
    t = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>|<!--.*?-->", " ", raw)
    t = re.sub(r"(?i)<(br|p|li|tr|h\d|div|td|th|section|article|span)[^>]*>", "\n", t)
    t = H.unescape(re.sub(r"<[^>]+>", " ", t))
    return "\n".join(x for x in (re.sub(r"\s+", " ", l).strip() for l in t.splitlines()) if x)


def pdf_text(data):
    import subprocess, tempfile
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(data); f.flush()
        try:
            out = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, timeout=60).stdout
        except Exception:
            return ""
    return "\n".join(re.sub(r"\s+", " ", l).strip() for l in out.decode("utf-8", "replace").splitlines() if l.strip())


def read(u):
    final, ctype, data = get(u)
    if "pdf" in ctype or final.lower().endswith(".pdf"):
        return final, "", pdf_text(data), "", []
    raw = data.decode("utf-8", "replace")
    title = re.search(r"(?is)<title[^>]*>(.*?)</title>", raw)
    title = re.sub(r"\s+", " ", H.unescape(title.group(1))).strip() if title else ""
    links = []
    for href, txt in re.findall(r'(?is)<a[^>]+href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', raw):
        links.append((urllib.parse.urljoin(final, H.unescape(href.strip())), re.sub(r"<[^>]+>|\s+", " ", txt).strip()))
    tels = re.findall(r'(?i)href=["\']tel:([^"\']+)', raw)
    for m in re.finditer(r'(?is)<iframe[^>]+src=["\']([^"\']+)', raw):
        links.append((urllib.parse.urljoin(final, H.unescape(m.group(1))), "[iframe]"))
    return final, title, visible(raw), raw, (links, tels)


def phones(text, tels):
    out = []
    for m in list(PHONE.finditer(text)) + [PHONE.search(t) for t in tels if PHONE.search(t)]:
        p = "-".join(m.groups())
        if p not in out:
            out.append(p)
    return out


def host(u):
    return urllib.parse.urlparse(u).netloc.lower().removeprefix("www.")


def one(e):
    rec = {"id": e["id"], "name": e["name"], "state": e.get("state"), "ownership": e.get("ownership"),
           "phone": e.get("phone"), "website": e.get("website"), "pages": [], "engines": [], "phones": [],
           "errors": [], "parked": False}
    urls = [u.strip() for u in (e.get("website") or "").split("\n") if u.strip().startswith("http")]
    ops = [u for u in urls if not any(a in host(u) for a in AGG)]
    seen, follow = set(), []
    for u in ops:
        if any(g in u.lower() for g in ENGINES) and u not in rec["engines"]:
            rec["engines"].append(u)
    for depth, todo in ((0, ops), (1, follow)):
        for u in todo:
            if u in seen or len(seen) >= 7:
                continue
            seen.add(u)
            try:
                final, title, text, raw, extra = read(u)
            except Exception as ex:
                rec["errors"].append(f"{u} {str(ex)[:100]}")
                continue
            rec["pages"].append({"url": u, "final": final, "title": title, "depth": depth, "text": text[:80000]})
            if PARKED.search(title + " " + text[:3000]) and len(text) < 6000:
                rec["parked"] = True
            if not extra:
                continue
            links, tels = extra
            for p in phones(text, tels):
                if p not in rec["phones"]:
                    rec["phones"].append(p)
            if depth == 0:
                h0 = host(final)
                scored = []
                for lu, lt in links:
                    lh = host(lu)
                    if any(g in lu.lower() for g in ENGINES) and lh != h0:
                        if lu not in rec["engines"] and len(rec["engines"]) < 12:
                            rec["engines"].append(lu)
                        continue
                    if lh != h0 or re.search(r"(?i)\.(jpg|jpeg|png|gif|zip|webp)$|mailto:|tel:|javascript:", lu):
                        continue
                    s = len(re.findall(r"(?i)rate|fee|price|pricing|tarif", lt + " " + lu)) * 3 + \
                        len(LINKWORD.findall(lt + " " + urllib.parse.urlparse(lu).path))
                    if s >= 2 and lu.rstrip("/") != final.rstrip("/"):
                        scored.append((s, lu))
                for s, lu in sorted(set(scored), key=lambda x: -x[0])[:4]:
                    if lu not in follow:
                        follow.append(lu)
            time.sleep(0.5)
    return rec


def main():
    ids = {int(x) for x in open(sys.argv[1]).read().replace("\n", ",").split(",") if x.strip()}
    rows = [e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8")) if e["id"] in ids]
    with open(sys.argv[2], "w", encoding="utf-8") as out, cf.ThreadPoolExecutor(6) as ex:
        for rec in ex.map(one, rows):
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
            print(rec["id"], len(rec["pages"]), len(rec["errors"]), "PARKED" if rec["parked"] else "", flush=True)


if __name__ == "__main__":
    main()
