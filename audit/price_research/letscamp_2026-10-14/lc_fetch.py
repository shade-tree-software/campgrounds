"""lc_fetch.py IDS OUT.jsonl - Let's Camp public JSON for each entry's letscamp.ca/camps/<slug> link
(recipe: .claude/memory/reference_small_engine_apis.md)."""
import json, re, sys, time, urllib.request
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/140.0", "Accept": "application/json", "X-Tenant-Type": "camp"}
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
            return json.load(r)
    except Exception as e:
        return {"error": str(e)}
ids = {int(x) for x in open(sys.argv[1]).read().replace("\n", ",").split(",") if x.strip()}
db = {x["id"]: x for x in json.load(open("campgrounds.json", encoding="utf-8"))}
with open(sys.argv[2], "w", encoding="utf-8") as out:
    for i in sorted(ids):
        slugs = re.findall(r"letscamp\.ca/(?:[a-z]{2}/)?camps/([^/?#\s]+)", db[i].get("website") or "")
        for s in dict.fromkeys(slugs):
            j = get(f"https://letscamp.ca/api/camps/{s}?locale=en")
            c = j.get("camp") or {}
            st = get(f"https://letscamp.ca/api/camps/{c['_id']}/status?locale=en") if c.get("_id") else {}
            fut = (j.get("metaData") or {}).get("futureAvailableDates") or []
            rec = {"id": i, "slug": s, "error": j.get("error"), "name": c.get("name"),
                   "minimumPrice": c.get("minimumPrice"), "includeTax": (c.get("info") or {}).get("includeTax"),
                   "minNights": (c.get("settings") or {}).get("minNights"),
                   "maxNights": (c.get("settings") or {}).get("maxNights"),
                   "maxRVLength": (j.get("metaData") or {}).get("maxRVLength"),
                   "open_first": fut[0] if fut else None, "open_last": fut[-1] if fut else None, "open_n": len(fut),
                   "siteTypes": [ (t.get("name") if isinstance(t, dict) else t) for t in (c.get("siteTypes") or [])][:12],
                   "status": st.get("status"), "earliestBookingDate": st.get("earliestBookingDate")}
            out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()
            print(i, s, rec["minimumPrice"], rec["minNights"], rec["status"], rec["error"] or "")
            time.sleep(1)
