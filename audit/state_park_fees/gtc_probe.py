"""Probe a GoingToCamp (Camis) host: every resource of each park whose category matches CATRE (default
"campsite"), grouped by fee schedule, with its maps, allowed equipment, hookup attributes and the feeDetails answer for each date.

    CATRE="(?i)short stay" python3 -I gtc_probe.py HOST 2027-07-13[,DATE...] OUT.json [park-substring ...]

feeDetails can answer with more than one fee for a site (Newfoundland: the nightly AND the weekly rate), so every
fee is kept as returned; gtc_prices.py sums them, which is right only where a site has one fee (2026-10-12)."""
import json, os, re, sys, time, urllib.parse, urllib.request, http.cookiejar
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
host, dates, out = sys.argv[1], sys.argv[2].split(","), sys.argv[3]
only = [s.lower() for s in sys.argv[4:]]
CATRE = os.environ.get("CATRE", "(?i)campsite")
base = f"https://{host}"
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
op.addheaders = [("User-Agent", UA), ("Accept", "application/json, text/plain, */*")]
op.open(base + "/", timeout=30).read()
def get(ep):
    time.sleep(0.3)
    return json.load(op.open(base + ep, timeout=60))
def fee(rid, d):
    q = urllib.parse.urlencode({"resourceId": rid, "startDate": d, "boatLength": 0, "bookingCategoryId": 0,
                                "entryPointResourceId": 0, "exitPointResourceId": 0})
    req = urllib.request.Request(f"{base}/api/resource/feeDetails?{q}", data=b"[]", method="POST",
                                 headers={"Content-Type": "application/json"})
    time.sleep(0.4)
    try:
        dd = json.load(op.open(req, timeout=60))
    except Exception as e:
        return {"error": str(e)}
    return dd
locs = {r["resourceLocationId"]: (r["localizedValues"][0].get("fullName") or "") for r in get("/api/resourceLocation")}
cats = {c["resourceCategoryId"]: c["localizedValues"][0]["name"] for c in get("/api/resourcecategory")}
subs = {}
for c in get("/api/equipment"):
    for s in c.get("subEquipmentCategories", []):
        subs[s["subEquipmentCategoryId"]] = s["localizedValues"][0]["name"]
try:
    attrs = {int(k): a for k, a in get("/api/attribute/filterable").items()}
except Exception:
    attrs = {}
SERVICE = re.compile(r"(?i)electric|water service|sewer|service type")


def services(r):
    """The site's hookup attributes as 'Name=Label' pairs (enum attributes whose name looks like a hookup)."""
    out = []
    for a in r.get("definedAttributes") or []:
        d = attrs.get(a.get("attributeDefinitionId"))
        if not d or not SERVICE.search(d["localizedValues"][0]["displayName"]):
            continue
        labels = {v["enumValue"]: v["localizedValues"][0]["displayName"] for v in d.get("values") or []}
        vals = a.get("values") or ([a["value"]] if a.get("value") is not None else [])
        out.append(d["localizedValues"][0]["displayName"] + "=" + "/".join(str(labels.get(v, v)) for v in vals))
    return ", ".join(sorted(out))
result = {"host": host, "dates": dates, "read": time.strftime("%Y-%m-%d"), "categories": cats, "equipment": subs, "parks": []}
for lid, pname in locs.items():
    if only and not any(o in pname.lower() for o in only):
        continue
    maps = get(f"/api/maps?resourceLocationId={lid}")
    res = get(f"/api/resourcelocation/resources?resourceLocationId={lid}")
    mapof = {}
    for m in maps:
        for r in m.get("mapResources") or []:
            mapof.setdefault(r["resourceId"], m["localizedValues"][0]["title"])
    groups = {}
    for k, r in res.items():
        cat = cats.get(r.get("resourceCategoryId"))
        if not cat or not re.search(CATRE, cat):
            continue
        groups.setdefault(r.get("feeScheduleId"), []).append(r)
    park = {"park": pname, "id": lid, "schedules": []}
    for fs, rs in groups.items():
        r = rs[0]
        eq = sorted({subs.get(x.get("subEquipmentCategoryId"), str(x.get("subEquipmentCategoryId"))) for rr in rs for x in rr.get("allowedEquipment") or []})
        maps_ = sorted({mapof.get(rr["resourceId"], "?") for rr in rs})
        fees = {}
        for d in dates:
            dd = fee(r["resourceId"], d)
            if "error" in dd:
                fees[d] = dd
            else:
                fees[d] = [(f.get("feeTotal"), f.get("feeCategoryId"), (f.get("localizedValues") or [{}])[0].get("name") if f.get("localizedValues") else f.get("name")) for f in dd.get("resourceFeeDetails") or []]
        combos = {}
        for rr in rs:
            k = services(rr)
            combos[k] = combos.get(k, 0) + 1
        sch = {"feeScheduleId": fs, "n": len(rs), "category": cats.get(r.get("resourceCategoryId")),
               "example": r["localizedValues"][0]["name"], "maps": maps_, "equipment": eq, "services": combos,
               "fees": fees}
        park["schedules"].append(sch)
        print(pname, "|", fs, "|", len(rs), sch["category"], "|", maps_[:4], "|", eq[:6], "|", combos, "|", fees, flush=True)
    result["parks"].append(park)
json.dump(result, open(out, "w"), ensure_ascii=False, indent=1)
