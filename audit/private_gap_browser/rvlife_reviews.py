"""rvlife_reviews.py PARKID [PARKID...]: every RV Life review of a park, as text lines under a '##### <reviews api url>' header:
month/year of stay, nightly price paid and discount, site type and hookups, headline, review and tip. Without a login
the API answers every page with page 1, so it stops at the first page that brings no new review."""
import gzip, json, sys, time, urllib.request
def get(u):
    r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/140.0", "Accept": "application/x.rvparkreviews.v3+json", "Accept-Encoding": "gzip"}), timeout=30)
    d = r.read(); d = gzip.decompress(d) if r.headers.get("Content-Encoding") == "gzip" else d
    return json.loads(d)
for pid in sys.argv[1:]:
    u = f"https://campgrounds.rvlife.com/api/reviews/park/{pid}"
    print(f"##### {u}")
    page, seen = 1, set()
    while True:
        j = get(f"{u}?page={page}")
        new = [rv for rv in j["data"] if rv["id"] not in seen]
        seen.update(rv["id"] for rv in new)
        for rv in new:
            print(f"RV Life review ({rv['park']['name']}): stayed {rv.get('month')}/{rv.get('year')} | price ${rv.get('price')} {rv.get('currency')} a night, discount {rv.get('discount')} | {rv.get('camper')} | site {rv.get('site_number')} {rv.get('site_type')} | power {rv.get('power')} water {rv.get('water')} sewer {rv.get('sewer')} | no_stay {rv.get('no_stay')} | rating {rv.get('rating')}")
            print(f"   {rv.get('headline')}: {rv.get('review')} | tip: {rv.get('tip')}")
        if not new or page >= j["meta"]["last_page"]:
            break
        page += 1
        time.sleep(1)
