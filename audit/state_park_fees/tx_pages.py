"""Texas state parks' own fee pages (tpwd.texas.gov), read 2026-10-12.

    python3 -I tx_pages.py OUT.json SLUG [SLUG ...]

For each park slug: every campsite type on /state-parks/<slug>/fees-facilities/campsites (name, number of sites,
amenities, the listing's description - where a maximum vehicle length is given - and the nightly and weekly fee),
and the daily entrance fee lines from /fees-facilities/entrance-fees. Plain
urllib; a park already in OUT is skipped, and OUT is rewritten after each park."""
import html, json, os, re, sys, time, urllib.request
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
BASE = "https://tpwd.texas.gov/state-parks/"
out_path, slugs = sys.argv[1], sys.argv[2:]
out = json.load(open(out_path)) if os.path.exists(out_path) else {}


def get(u):
    time.sleep(0.5)
    return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=60).read().decode(
        "utf-8", "replace")


def text(fragment):
    f = re.sub(r"<script.*?</script>|<style.*?</style>", "", fragment, flags=re.S | re.I)
    f = re.sub(r"<(br|p|li|tr|td|th|h\d|div)[^>]*>", "\n", f, flags=re.I)
    return [re.sub(r"\s+", " ", l).strip() for l in html.unescape(re.sub(r"<[^>]+>", " ", f)).split("\n") if l.strip()]


for slug in slugs:
    if slug in out:
        continue
    rec = {"slug": slug, "types": [], "entrance": []}
    try:
        t = get(BASE + slug + "/fees-facilities/campsites")
    except Exception as x:  # noqa: BLE001
        rec["error"] = f"campsites: {x}"
        out[slug] = rec
        json.dump(out, open(out_path, "w"), indent=1, ensure_ascii=False)
        print(slug, rec["error"], flush=True)
        continue
    book = re.search(r'href="(https://texasstateparks\.reserveamerica\.com[^"]+)"', t)
    rec["booking"] = html.unescape(book.group(1)) if book else None
    for blk in t.split('<div class="chartrow')[1:]:
        h = re.search(r'<h3>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', blk, re.S)
        price = re.search(r'<div class="col3">\s*\$([\d,.]+)', blk)
        weekly = re.search(r'weeklyfee">\s*<strong>\$([\d,.]+)', blk)
        sites = re.search(r"Number of Sites:\s*(\d+)", blk)
        lines = text(blk)
        typ = {"name": html.unescape(re.sub(r"<[^>]+>", "", h.group(2))).strip() if h else None,
               "href": h.group(1) if h else None, "sites": int(sites.group(1)) if sites else None,
               "nightly": float(price.group(1).replace(",", "")) if price else None,
               "weekly": float(weekly.group(1).replace(",", "")) if weekly else None, "listing": lines}
        rec["types"].append(typ)
    try:
        e = text(get(BASE + slug + "/fees-facilities/entrance-fees").split('id="content-core"')[-1])
        rec["entrance"] = e[:40]
    except Exception as x:  # noqa: BLE001
        rec["entrance_error"] = str(x)
    out[slug] = rec
    json.dump(out, open(out_path, "w"), indent=1, ensure_ascii=False)
    print(slug, len(rec["types"]), [(x["name"], x["nightly"]) for x in rec["types"]][:8], flush=True)
