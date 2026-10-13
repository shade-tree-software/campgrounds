# campspot_batch.py OUT.jsonl TUESDAY SATURDAY ID:SLUG [ID:SLUG ...]      (dates YYYY-MM-DD)
# For each Campspot park: list its site types with campspot.py (one night from TUESDAY), then read
# campspot_site.py's price breakdown of every RV type that takes a 23-ft rig (or gives no length)
# for one night from TUESDAY and one from SATURDAY. One JSON line per park: the listing, the guests
# string, each RV type from the availability answer (`avg` = averagePricePerNight, which is the
# Site Total less tax - it includes the park's 'Campground Fees' and Campspot's 'Booking Fee'),
# and the breakdown lines per date. A park with no /book/ engine (marketplace only) is written
# with an error; work it by hand. Used for the family stays and the re-check of the 2026-10-10
# Campspot prices (2026-10-13). Needs drv_server.py; runs one park at a time.
import ast, datetime, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(*a):
    return subprocess.run([sys.executable, *a], capture_output=True, text=True, timeout=900).stdout


def drv(*a):
    return run(os.path.join(HERE, "drv.py"), *a)


def nextday(d):
    return (datetime.date.fromisoformat(d) + datetime.timedelta(days=1)).isoformat()


def main():
    out_path, tue, sat = sys.argv[1:4]
    parks = [a.split(":", 1) for a in sys.argv[4:]]
    with open(out_path, "a") as out:
        for eid, slug in parks:
            listing = run(os.path.join(HERE, "campspot.py"), slug, tue, nextday(tue))
            url = drv("url")
            m = re.search(r"/(guests[\d,]+)/", url)
            net = drv("net", "grep=availability/parks", "last=400")
            ids = re.findall(r"^\[(\d+)\] 200 GET .*availability/parks/\d+\?checkin=%s" % tue, net, re.M)
            rec = {"id": int(eid), "slug": slug, "dates": [tue, sat], "listing": listing.splitlines(),
                   "url": url.strip()}

            def done(msg):
                rec["error"] = msg
                out.write(json.dumps(rec) + "\n")
                out.flush()
                print(eid, slug, "ERROR", msg, flush=True)

            if not m:
                done("no /book/ list page")
                continue
            # 2 adults and nobody else: Campspot fills a category missing from the URL (pets) with the
            # browser's last count, so the string is rebuilt from the categories campspot.py read
            cats = re.search(r"guest categories: (\[.*?\])", listing)
            cats = ast.literal_eval(cats.group(1)) if cats else []
            n = len(m.group(1)[6:].split(","))
            adult = next((i for i, c in enumerate(cats) if c.lower().startswith("adult")), None)
            if adult is None:
                done("no Adults category")
                continue
            guests = "guests" + ",".join("2" if i == adult else "0" for i in range(max(n, len(cats))))
            if guests != m.group(1) or not ids:
                drv("goto", "url=https://www.campspot.com/book/%s/search/%s/%s/%s/list" % (slug, tue, nextday(tue), guests),
                    "wait=10000")
                net = drv("net", "grep=availability/parks", "last=400")
                ids = re.findall(r"^\[(\d+)\] 200 GET .*availability/parks/\d+\?checkin=%s.*guests=%s" % (tue, guests),
                                 net, re.M)
                if not ids:
                    done("no availability for " + guests)
                    continue
            rv = []
            for t in json.loads(drv("body", "i=" + ids[-1], "max=6000000")):
                if t.get("campsiteCategoryCode") != "rv":
                    continue
                lens = [((s.get("rvInfo") or {}).get("rvLengthMax")) for s in t.get("campsites", [])]
                rv.append({"cat": t["id"], "name": t.get("name"), "avg": t.get("averagePricePerNight"),
                           "max_len": max([x for x in lens if x] or [0]), "sites": len(t.get("campsites", [])),
                           "free": sum(s.get("availability") == "AVAILABLE" for s in t.get("campsites", [])),
                           "failure": sorted({str(x) for x in (t.get("failureReasons") or [])})})
            rec.update(guests=guests, rv=rv, breakdown={})
            fit = [t["cat"] for t in rv if not t["max_len"] or t["max_len"] >= 23]
            for d in (tue, sat):
                if fit:
                    rec["breakdown"][d] = run(os.path.join(HERE, "campspot_site.py"), slug, guests, d, nextday(d),
                                              *map(str, fit)).splitlines()
            out.write(json.dumps(rec) + "\n")
            out.flush()
            print(eid, slug, len(rv), "rv types,", len(fit), "fit", flush=True)


if __name__ == "__main__":
    main()
