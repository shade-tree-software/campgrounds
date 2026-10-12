"""NY state campgrounds: each entry's booking-site description and its agency page's fee lines.

    python3 -I ny_pages.py OUT.json

For every unpriced NY state entry: the ReserveAmerica campgroundDetails page (its description,
which states site counts such as '243 electric sites', and its link to the park's page), then
that parks.ny.gov page's camping fee lines (Base Rate, Electric Fee, ...). DEC campgrounds link
to dec.ny.gov, whose fees come from DEC's campground summary instead. parks.ny.gov refuses a
python client but serves curl, so pages are fetched with curl."""
import html, json, os, re, subprocess, sys, time, urllib.request, http.cookiejar
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"


def text_lines(t):
    t = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", t)
    t = html.unescape(re.sub(r"<[^>]+>", "\n", t))
    return [l for l in (re.sub(r"\s+", " ", x).strip() for x in t.split("\n")) if l]


rows = json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))
reg = json.load(open(os.path.join(ROOT, "campground_policies.json"), encoding="utf-8"))
out = {}
for e in rows:
    if e.get("state") != "NY" or e.get("ownership") != "state" or e.get("kind") != "campground":
        continue
    f = (cs.resolve(e, reg).get("fees") or {}).get("values", {})
    if "nightly_low" in f or "nightly_high" in f:
        continue
    u = next((w for w in (e.get("website") or "").split() if "parkId=" in w), None)
    if not u:
        continue
    pid = re.search(r"parkId=(\d+)", u).group(1)
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    op.addheaders = [("User-Agent", UA)]
    t = op.open(f"https://newyorkstateparks.reserveamerica.com/campgroundDetails.do?contractCode=NY&parkId={pid}",
                timeout=60).read().decode("utf-8", "replace")
    links = sorted(set(re.findall(r"https?://(?:www\.)?(?:parks\.ny\.gov/visit/[^\"'<> #]+|dec\.ny\.gov/[^\"'<> #]+)", t)))
    desc = [l for l in text_lines(t) if re.search(r"(?i)\belectric|hook-?up|\bsites?\b|amp\b", l) and len(l) < 1500][:12]
    rec = {"name": e["name"], "parkId": pid, "links": links, "ra_lines": desc, "fee_lines": [], "page_lines": []}
    page = next((l for l in links if "/visit/" in l), None)
    if page:
        r = subprocess.run(["curl", "-s", "-L", "-A", "Mozilla/5.0", "-m", "60", page], capture_output=True)
        L = text_lines(r.stdout.decode("utf-8", "replace"))
        i = next((k for k, l in enumerate(L) if l.startswith("Campsites:") or l == "Campsites"), None)
        if i is not None:
            rec["fee_lines"] = L[i:i + 16]
        rec["page_lines"] = [l for l in L if re.search(r"(?i)electric|campsites|\bsites\b|hook-?up", l) and len(l) < 900][:10]
        rec["page"] = page
    out[e["id"]] = rec
    print(e["id"], e["name"], "|", page or links[:1], "|", " / ".join(rec["fee_lines"][:8]), flush=True)
    time.sleep(1)
json.dump(out, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
