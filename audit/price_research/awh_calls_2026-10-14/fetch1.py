"""fetch1.py OUTFILE URL [URL...]: append each page's text to OUTFILE as '##### URL -> final', fetching exactly the
URLs given (no link following). HTML comments are dropped with scripts and styles: an operator can
comment out an obsolete rate table (Liberty Haven AZ, 2026-10-14), which a bare tag strip reads as live text. Commas in a URL are sent as %2C but kept literal in the header (Josephine County's
paths contain them, which opfetch.py splits on). Batch 29, 2026-10-14."""
import gzip, html as H, re, sys, urllib.request, zlib
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36",
      "Accept": "text/html,*/*;q=0.8", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9"}
def get(u):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30)
    d = r.read(5_000_000); e = r.headers.get("Content-Encoding", "")
    d = gzip.decompress(d) if e == "gzip" else zlib.decompress(d) if e == "deflate" else d
    return r.geturl(), d.decode("utf-8", "replace")
def text(t):
    t = H.unescape(re.sub(r"<[^>]+>", "\n", re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>|<!--.*?-->", " ", t)))
    return "\n".join(x for x in (re.sub(r"\s+", " ", l).strip() for l in t.splitlines()) if x)
out = sys.argv[1]
for u in sys.argv[2:]:
    try:
        final, t = get(u.replace(",", "%2C"))
        body = text(t)
        sec = f"\n##### {u} -> {final.replace('%2C', ',')}\n{body}\n"
        print(u, len(body))
    except Exception as ex:
        sec = f"\n##### {u} ERROR {ex}\n"
        print(u, "ERR", ex)
    open(out, "a", encoding="utf-8").write(sec)
