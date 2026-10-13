"""Every site of a ReserveAmerica 'CUI' park (the .page platform, e.g. Colorado's cpwshop.com) from its map, 2026-10-12.

    python3 -I cui_sites.py CAMPGROUND_DETAILS_URL [...] > OUT.jsonl

The campground page (/camping/<slug>/r/campgroundDetails.page?parkID=N) draws its site map from
/ajax/CUIGISMap?event=getGISMap&componentId=<the page's ac-... id>&e_Page_ID=/campgroundDetails.page, a GeoJSON of
every site: loop, site type, maximum vehicle length, coordinates and the site page's link. Parks drawn on an SVG map
instead answer that call with nothing; their /ajax/CUISVGMap?event=getMapIcons layer still names every site
('<g id="s_1209" class="iconSite" ...><title>001, Basic</title>'), with no loop or length (read those off the site
pages - cui_rates.py does). One JSON line per park: {url, parkId, name, sites: [{siteId, site, loop, type, maxlen,
coords, action}]}."""
import html, json, re, sys, time, urllib.request, http.cookiejar
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"


def text(v):
    return html.unescape(re.sub(r"<[^>]+>", "", v or "")).strip()


for url in sys.argv[1:]:
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    op.addheaders = [("User-Agent", UA)]
    host = re.match(r"https?://[^/]+", url).group(0)
    rec = {"url": url, "parkId": re.search(r"parkID=(\d+)", url).group(1)}
    try:
        t = op.open(url, timeout=60).read().decode("utf-8", "replace")
        cid = re.search(r"componentId=(ac-[0-9a-z]+)", t).group(1)
        time.sleep(0.5)
        raw = op.open(f"{host}/ajax/CUIGISMap?event=getGISMap&componentId={cid}&e_Page_ID=/campgroundDetails.page",
                      timeout=60).read()
        if not raw.strip():
            time.sleep(0.5)
            svg = op.open(f"{host}/ajax/CUISVGMap?event=getMapIcons&componentId={cid}&e_Page_ID=/campgroundDetails.page",
                          timeout=60).read().decode("utf-8", "replace")
            rec["name"] = re.search(r"/camping/([^/]+)/", url).group(1).replace("-", " ").title()   # the <title> is generic
            rec["map"] = "svg"
            rec["sites"] = []
            for m in re.finditer(r'<g id="s_(\d+)" class="iconSite".*?<title>([^<]*)</title>', svg, flags=re.S):
                name, _, stype = html.unescape(m.group(2)).partition(", ")
                rec["sites"].append({"siteId": m.group(1), "site": name, "loop": None, "type": stype, "maxlen": None,
                                     "coords": None, "action": f"/camping/{re.search(r'/camping/([^/]+)/', url).group(1)}"
                                                               f"/r/campsiteDetails.page?parkID={rec['parkId']}&siteID={m.group(1)}"})
            print(json.dumps(rec), flush=True)
            time.sleep(1)
            continue
        g = json.loads(raw)
    except Exception as x:  # noqa: BLE001 - one bad park shouldn't stop the run
        rec["error"] = str(x)
        print(json.dumps(rec), flush=True)
        continue
    rec["name"] = (g.get("location") or {}).get("name")
    sites = []
    for f in (g.get("markersUnique") or {}).get("features") or []:
        p = f.get("properties") or {}
        ui = p.get("uiData") or {}
        head = ui.get("head") or {}
        attrs = {text(a.get("title")).rstrip(":"): text(a.get("value"))
                 for s in ui.get("sections") or [] for a in s.get("attributes") or []}
        loop = re.sub(r"^Loop:\s*", "", text(head.get("loop")))
        stype = re.sub(r"^Site type:\s*", "", text(head.get("siteType"))) or p.get("displayLabel")
        sites.append({"siteId": str(f.get("elementID") or p.get("id")), "site": text(head.get("siteName")), "loop": loop,
                      "type": stype, "maxlen": attrs.get("Maximum Vehicle Length"), "coords": ui.get("coords"),
                      "action": (ui.get("cta") or {}).get("action")})
    rec["sites"] = sites
    print(json.dumps(rec), flush=True)
    time.sleep(1)
