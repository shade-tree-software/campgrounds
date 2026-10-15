"""Read campground fees from mycountyparks.com (the reservation platform Iowa's county conservation boards share,
and a few other counties) for local entries with no fees. Plain HTTP; one request a second.
python3 -I read.py OUT.jsonl [--limit N]   - resumable: ids already in OUT are skipped.
Per entry: the mycountyparks URL in its website field; when that is a park page, its camping facilities (names
with camp/RV/electric/hook-up/site, not shelters/cabins/lodges) - campground-level ones first, else up to 4
site-level ones; each facility page's 'Fees' and 'Hours of Operation & Seasons' blocks as text."""
import html, json, os, re, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
BASE = "https://www.mycountyparks.com"
CAMP = re.compile(r"camp|rv|electric|hook|site|primitive|pad", re.I)
NOT = re.compile(r"shelter|cabin|lodge|yurt|hall|house|pavilion|blind|rookery|cottage|bunk|tent-only|group|equestrian|horse|"
                 r"canoe|kayak|room|center|barn|lodging|gazebo|amphithe", re.I)
SITE = re.compile(r"(^|-)site(-|$)|-\d+(-|$)|\b\d+[a-z]?$", re.I)


def get(u):
    time.sleep(1)
    r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/140"}), timeout=40)
    return r.geturl(), r.read().decode("utf-8", "replace")


def block(t, head):
    m = re.search(r"<h2>\s*(?:" + head + r")\s*</h2>(.*?)(?:<hr\s*/?>|<h2>)", t, re.S | re.I)
    if not m:
        return ""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<br\s*/?>|</p>", " | ", m.group(1)).replace("\r", ""))).strip()


def text(t):
    t = re.sub(r"<br\s*/?>|</p>", " | ", t)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip(" |")


def facility(u):
    url, t = get(u)
    return {"url": url, "name": url.rstrip("/").split("/Facility/")[-1], "fees": text(block(t, "Fees")),
            "hours": text(block(t, r"Hours of Operation &amp; Seasons|Hours of Operation & Seasons"))[:600]}


def main():
    out = sys.argv[1]
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 10 ** 6
    done = set()
    if os.path.exists(out):
        done = {json.loads(l)["id"] for l in open(out) if l.strip()}
    import campground_schema as cs
    reg = json.load(open(os.path.join(ROOT, "campground_policies.json")))
    db = json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))
    todo = [r for r in db if r.get("kind") == "campground" and r["ownership"] == "local" and not r.get("fees")
            and not cs.resolve(r, reg).get("fees") and "mycountyparks.com" in (r.get("website") or "").lower()
            and r["id"] not in done]
    print(len(todo), "to read")
    for r in todo[:limit]:
        u = next(x.strip() for x in r["website"].split("\n") if "mycountyparks.com" in x.lower())
        rec = {"id": r["id"], "name": r["name"], "state": r["state"], "src": u, "read": time.strftime("%Y-%m-%d"),
               "facilities": [], "park_fee_lines": []}
        try:
            if "/facility/" in u.lower() and "/facility/default" not in u.lower():
                rec["facilities"].append(facility(re.sub(r"/Availability/?$", "", u, flags=re.I)))
            else:
                url, t = get(u)
                rec["park_url"] = url
                pt = text(re.sub(r"(?s)<script.*?</script>|<style.*?</style>", "", t))
                rec["park_fees"] = text(block(t, "Fees"))
                rec["park_fee_lines"] = [pt[max(0, m.start() - 120):m.start() + 120] for m in re.finditer(r"\$\s?\d", pt)][:8]
                names = []
                for h in re.findall(r'href="(/County/[^"]+/Facility/([^"/?]+))(?:/Availability)?"', t, re.I):
                    if h[1].lower() in ("default", "search") or h in names:
                        continue
                    names.append(h)
                camp = [h for h in names if CAMP.search(h[1]) and not NOT.search(h[1])]
                top = [h for h in camp if not SITE.search(h[1])]
                pick = top[:6] if top else camp[:4]
                rec["facility_names"] = [h[1] for h in names][:60]
                for h in pick:
                    rec["facilities"].append(facility(BASE + h[0]))
        except Exception as e:
            rec["error"] = repr(e)[:300]
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(r["id"], r["name"][:40], "|", len(rec["facilities"]), "fac |",
              " / ".join(f["fees"][:70] for f in rec["facilities"])[:160], rec.get("error", ""))


if __name__ == "__main__":
    main()
