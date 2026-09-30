# usage: gsr.py ST "name" ["name" ...]  -> Good Sam ratings (facility/restroom/appeal, overall) by name
import sys, json, uuid, urllib.request, urllib.parse
def post(url, body, headers):
    r = urllib.request.Request(url, json.dumps(body).encode(), {"content-type": "application/json", **headers})
    return json.load(urllib.request.urlopen(r, timeout=30))
key = post("https://llx3tsxl2jaarct3rynyyaci3e.appsync-api.us-east-1.amazonaws.com/graphql",
           {"query": "query($t:String!){getCampgroundSearchAuthSecret(userToken:$t){secret}}", "variables": {"t": str(uuid.uuid4())}},
           {"x-api-key": "da2-oeeljcqa6rcljmmook5my3iuv4"})["data"]["getCampgroundSearchAuthSecret"]["secret"]
st = sys.argv[1]
for q in sys.argv[2:]:
    res = post("https://VT01MNVCP5-dsn.algolia.net/1/indexes/gs-ml-cb-assets-prod/query",
               {"query": q, "filters": f"campground.address.stateCode:{st}", "hitsPerPage": 8},
               {"X-Algolia-Application-Id": "VT01MNVCP5", "X-Algolia-API-Key": key})
    seen = set()
    for h in res["hits"]:
        c = h.get("campground", {})
        if c.get("id") in seen: continue
        seen.add(c.get("id"))
        r = {k: (v or {}).get("value") for k, v in (c.get("ratings") or {}).items()} if isinstance(c.get("ratings"), dict) else c.get("ratings")
        print(f"{q!r:32} -> {c.get('name')} ({(c.get('address') or {}).get('city')}) gs={c.get('isGsPark')} ratings={r}")
        break
