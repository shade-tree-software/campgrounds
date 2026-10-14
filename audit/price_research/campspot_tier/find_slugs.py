"""find_slugs.py --ids 1,2,3 OUT.json [--follow 6]
Find the Campspot slug of entries whose note says they book on Campspot but whose website carries no campspot.com
link (2026-10-13, the 64 tier-only entries with booking.platform "campspot"). A slug is copied from the operator's own
pages, never composed from the name ([[reference_campspot_api]]).

For each entry: fetch every URL in `website`, then up to --follow links from those pages whose text or href says
book/reserve/rate/stay/camp/RV (same site, or another host the link text calls booking - a white-label booking
domain). Each page's raw HTML (with JSON-escaped slashes undone) and its final URL after redirects are searched for
campspot.com/book/<slug> and campspot.com/park/<slug>. campspot.com itself is never fetched (it answers 403 to a plain
client); a link to it is read from the href. Other booking engines the pages link to are listed too, since a park
that moved off Campspot is the usual reason for finding none.

OUT = {id: {"slugs": {slug: [kind, page it was found on, ...]}, "engines": [...], "pages": [...], "errors": [...]}}.
Plain urllib: a site that builds its links in JS shows nothing; run audit/private_gap_browser/scan.py on those.
"""
import argparse, concurrent.futures, gzip, html, json, os, re, sys, urllib.parse, urllib.request, zlib

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,*/*;q=0.8", "Accept-Encoding": "gzip, deflate",
      "Accept-Language": "en-US,en;q=0.9,fr;q=0.7"}
SLUG = re.compile(r"(?i)campspot\.com/(book|park)/([a-z0-9][a-z0-9_-]*)")
ENGINE = re.compile(r"(?i)https?://[^\"'\s<>]*(resnexus|newbook|firefly|camplife|staylist|roverpass|hipcamp|campable|"
                    r"rmscloud|webrez|rezexpert|checkfront|cloudbeds|innroad|reserveamerica|usedirect|aspira|"
                    r"goingtocamp|campreservations\.ca|parkwith\.us|reservationsoft|bookingcenter|sitebuilder|"
                    r"campgroundviews|reserve\.|book\.|booking\.)[^\"'\s<>]*")
FOLLOW = re.compile(r"(?i)book|reserv|rate|pric|stay|camp|\brv\b|site|availab")
SKIP = re.compile(r"(?i)\.(jpe?g|png|gif|webp|svg|pdf|zip|mp4|css|js)(\?|$)|facebook|twitter|instagram|youtube|"
                  r"tiktok|pinterest|google\.|mailto:|tel:|javascript:|campspot\.com")
HREF = re.compile(r"""(?is)<a\b[^>]*?href\s*=\s*["']([^"']+)["'][^>]*>(.*?)</a>""")


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        data = r.read(4_000_000)
        enc = r.headers.get("Content-Encoding", "")
        if enc == "gzip":
            data = gzip.decompress(data)
        elif enc == "deflate":
            data = zlib.decompress(data)
        return r.geturl(), data.decode("utf-8", "replace")


def host(u):
    return re.sub(r"^www\.", "", urllib.parse.urlsplit(u).netloc.lower())


def scan(text, where, rec):
    text = text.replace("\\/", "/").replace("%2F", "/").replace("%2f", "/")
    for kind, slug in SLUG.findall(text):  # kept in the case found: a slug is copied exactly, never normalized
        rec["slugs"].setdefault(slug, [])
        tag = f"{kind.lower()} @ {where}"
        if tag not in rec["slugs"][slug]:
            rec["slugs"][slug].append(tag)
    for m in ENGINE.finditer(text):
        u = m.group(0)[:160]
        if "campspot" not in u and u not in rec["engines"] and len(rec["engines"]) < 12:
            rec["engines"].append(u)


def work(entry, follow):
    rec = {"name": entry["name"], "state": entry.get("state"), "slugs": {}, "engines": [], "pages": [], "errors": []}
    starts = [u.strip() for u in (entry.get("website") or "").split() if u.strip().startswith("http")]
    queue, seen = [], set()
    for u in starts:
        scan(u, "website field", rec)
        if "campspot.com" not in u:
            queue.append((u, True))
    n_follow = 0
    while queue:
        u, first = queue.pop(0)
        if u in seen:
            continue
        seen.add(u)
        try:
            final, text = fetch(u)
        except Exception as e:  # a dead page is information, not a failure of the run
            rec["errors"].append(f"{u}: {str(e)[:120]}")
            continue
        rec["pages"].append(u if final == u else f"{u} -> {final}")
        scan(final, f"redirect of {u}", rec)
        scan(text, final, rec)
        if not first:
            continue
        base_host = host(final)
        for href, label in HREF.findall(text):
            href = html.unescape(href.strip())
            label = re.sub(r"<[^>]+>|\s+", " ", label).strip()[:60]
            absu = urllib.parse.urljoin(final, href).split("#")[0]
            if not absu.startswith("http") or SKIP.search(absu) or absu in seen:
                continue
            same = host(absu) == base_host
            booking_label = re.search(r"(?i)book|reserv", label + " " + absu)
            if (same and FOLLOW.search(label + " " + urllib.parse.urlsplit(absu).path)) or (not same and booking_label):
                if n_follow < follow and absu not in [q for q, _ in queue]:
                    queue.append((absu, False))
                    n_follow += 1
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", required=True)
    ap.add_argument("--follow", type=int, default=6)
    ap.add_argument("out")
    a = ap.parse_args()
    ids = [int(x) for x in a.ids.split(",") if x.strip()]
    by = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
    out = {}
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        futs = {ex.submit(work, by[i], a.follow): i for i in ids}
        for f in concurrent.futures.as_completed(futs):
            out[futs[f]] = f.result()
    out = {i: out[i] for i in ids}
    json.dump(out, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    for i, r in out.items():
        s = "; ".join(f"{k} [{v[0]}]" for k, v in r["slugs"].items()) or "NONE"
        print(f"{i:>6} {r['state']} {r['name'][:38]:38} | {s[:150]}" + (f" | ERR {len(r['errors'])}" if r["errors"] else ""))
    print(sum(1 for r in out.values() if r["slugs"]), "of", len(out), "with a slug")


if __name__ == "__main__":
    main()
