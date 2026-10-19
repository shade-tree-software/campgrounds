"""Find booking-engine links on each target's own site (plain HTTP, 1 req/s, resumable).
    python3 -I engines.py targets.json engines.jsonl"""
import json, os, re, sys, time, urllib.parse, urllib.request, html
ENG = re.compile(r"https?://[^\"'\s<>]*(campspot\.com|newbook\.cloud|rmscloud\.com|rmsnorth|resnexus\.com|staylist\.com|"
                 r"fireflyreservations\.com|camplife\.com|letscamp\.ca|roverpass\.com|reserveamerica|campgroundviews|"
                 r"webreserv|checkfront\.com|cloudbeds\.com|lodgify\.com|innroad|bookingcenter|reservemyrv|"
                 r"parkwith\.us|campreservations|reservationpleinair|reservationcamping|rezexpert|"
                 r"secure\.campground|campground-reservations|reserve\.koa|koa\.com/campgrounds|sunoutdoors\.com|"
                 r"thousandtrails\.com|newbook|ezresortsoftware|aspira|camping\.bc|ireserve|reservations\.|booking\.|book\.)"
                 r"[^\"'\s<>]*", re.I)
LINK = re.compile(r"rate|pric|reserv|book|camp|rv-?site", re.I)
SKIP = re.compile(r"facebook|instagram|twitter|youtube|tripadvisor|google\.|rvlife|goodsam|pinterest", re.I)
def get(u):
    time.sleep(1)
    u = urllib.parse.quote(u, safe=":/?&=%#+,;@!$~*'()[]")
    r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36"}), timeout=25)
    return r.geturl(), r.read(2_000_000).decode("utf-8", "replace")
T = json.load(open(sys.argv[1])); out = sys.argv[2]
done = {json.loads(l)["id"] for l in open(out)} if os.path.exists(out) else set()
for t in T:
    if t["id"] in done: continue
    rec = {"id": t["id"], "engines": [], "pages": [], "err": []}
    urls = [u for u in re.split(r"\s+", t["web"]) if u and not SKIP.search(u)]
    seen = set()
    for u in urls[:2]:
        try:
            fu, h = get(u)
        except Exception as ex:
            rec["err"].append(f"{u}: {ex}"[:150]); continue
        rec["pages"].append(fu)
        rec["engines"] += ENG.findall(h) and [m.group(0) for m in ENG.finditer(h)]
        host = urllib.parse.urlparse(fu).netloc
        subs = []
        for href in re.findall(r'href=["\']([^"\'#]+)', h):
            a = urllib.parse.urljoin(fu, html.unescape(href))
            if urllib.parse.urlparse(a).netloc == host and LINK.search(a) and a not in seen and not re.search(r"\.(jpg|png|pdf|css|js)$", a, re.I):
                seen.add(a); subs.append(a)
        for a in subs[:5]:
            try:
                fa, ha = get(a)
                rec["pages"].append(fa); rec["engines"] += [m.group(0) for m in ENG.finditer(ha)]
            except Exception as ex:
                rec["err"].append(f"{a}: {ex}"[:150])
    rec["engines"] = sorted(set(e.rstrip("\\);,.") for e in rec["engines"]))[:25]
    with open(out, "a") as f: f.write(json.dumps(rec) + "\n")
    print(t["id"], len(rec["engines"]), flush=True)
