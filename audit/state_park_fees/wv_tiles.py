"""Every WV State Parks booking supplier's unit prices on the given stays (Inntopia eComm SupplierTile).
python3 wv_tiles.py SUPPLIERS_JSON OUT_JSON ARRIVE:DEPART [...]"""
import html, json, re, sys, time, urllib.request
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
B = "https://book.wvstateparks.com/Ecomm/Listings/SupplierTile/7816932/en-US"
ids = [x["SupplierId"] for x in json.load(open(sys.argv[1]))]
out = {}
for sid in ids:
    rec = {"name": None, "stays": {}}
    for stay in sys.argv[3:]:
        a, d = stay.split(":")
        u = f"{B}?supplierId={sid}&arrivalDate={a}&departureDate={d}&adultCount=2&childCount=0"
        try:
            t = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=60).read().decode("utf-8", "replace")
        except Exception as x:
            rec["stays"][stay] = {"error": str(x)}; continue
        m = re.search(r'id="supplierName_\d+">([^<]*)<', t)
        if m: rec["name"] = html.unescape(m.group(1)).strip()
        rows = []
        for tag in re.findall(r'<tr\s[^>]*data-product-name=[^>]*>', t):
            a = dict(re.findall(r'(data-[\w-]+)="([^"]*)"', tag))
            rows.append({"product": a.get("data-product-id"), "unit": html.unescape(a.get("data-product-name", "")),
                         "price": float(a["data-price"]) if a.get("data-price") else None,
                         "original": float(a["data-original-price"]) if a.get("data-original-price") else None,
                         "att": a.get("data-att", "")})
        rec["stays"][stay] = rows
        time.sleep(0.4)
    out[sid] = rec
    print(sid, rec["name"], {k: len(v) if isinstance(v, list) else v for k, v in rec["stays"].items()}, flush=True)
json.dump(out, open(sys.argv[2], "w"), indent=1)
