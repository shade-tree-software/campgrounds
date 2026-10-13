# campspot_market.py OUT.jsonl TUESDAY SATURDAY [--nights N] [--cats ID,ID] ID:SLUG [ID:SLUG ...]   (YYYY-MM-DD)
# campspot_batch.py for the parks that sell only through the Campspot marketplace (campspot.com/park/<slug>,
# no /book/ engine - the slug's /book/ page is "park-not-found"). For each park: open the marketplace page for
# TUESDAY, take every site type it links (campspot.com/<slug>/site/<id>), drop the ones that are plainly not
# RV sites (tent, cabin, lodging, group, horse - by name, before visiting), and read each site page's price
# breakdown ("$25.00 x 1 night", "Campground Fees $2.00", "Site Total") for N nights (default 1) from TUESDAY
# and from SATURDAY. One JSON line per park in campspot_batch.py's shape, with "market": true, the page's own
# notes ("Park is closed for your dates", "There is a 2 night minimum ...") and "closed" when it says the park
# is closed; with --nights 2 or more the lines go under "two_night" for TUESDAY only, the shape
# campspot_recheck_build.py reads for a fee's per-stay check; --cats limits the reads to those site types.
# Written for the 2026-10-13 re-check of the 2026-10-10 Campspot prices. Needs drv_server.py; one park at a time.
import json, os, re, subprocess, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
NOT_RV = r"(?i)\btent\b(?!.*\brv\b)|cabin|lodg|cottage|motel|room|yurt|bunk|\bgroup\b|horse|equestrian|storage|boat slip|dock"


def drv(*a):
    return subprocess.run([sys.executable, os.path.join(HERE, "drv.py"), *a], capture_output=True, text=True,
                          timeout=600).stdout


def plus(d, n):
    return (datetime.date.fromisoformat(d) + datetime.timedelta(days=n)).isoformat()


def breakdown(text):
    L = [l.strip() for l in text.split("\n") if l.strip()]
    start = next((i for i, l in enumerate(L) if re.match(r"^(?:[A-Z]{1,3})?\$[\d,.]+ x \d+ nights?$", l)), None)
    end = next((i for i, l in enumerate(L) if l == "Site Total"), None)
    if start is None or end is None or end < start:
        notes = [l for l in L if re.search(r"(?i)minimum|not available|unavailable|closed", l) and len(l) < 200]
        return "no breakdown" + (("  | " + " / ".join(dict.fromkeys(notes[:3]))) if notes else "")
    return " | ".join(L[start:end + 2])


def main():
    args = sys.argv[1:]
    nights, cats = 1, None
    if "--cats" in args:
        i = args.index("--cats")
        cats = set(args[i + 1].split(","))
        del args[i:i + 2]
    if "--nights" in args:
        i = args.index("--nights")
        nights = int(args[i + 1])
        del args[i:i + 2]
    out_path, tue, sat = args[:3]
    with open(out_path, "a") as out:
        for eid, slug in (a.split(":", 1) for a in args[3:]):
            page = "https://www.campspot.com/park/%s?checkin=%s&checkout=%s&guests=2,0,0" % (slug, tue, plus(tue, nights))
            drv("goto", "url=" + page, "wait=10000")
            text = drv("text", "max=60000")
            notes = sorted({l.strip() for l in text.split("\n")
                            if re.search(r"(?i)night minimum|closed for your dates|no sites available", l) and len(l) < 200})
            types = {}
            for line in drv("links", "grep=/site/").splitlines():
                m = re.match(r"^(.*?) -> https://www\.campspot\.com/%s/site/(\d+)\?" % re.escape(slug), line.strip())
                if m and m.group(1).strip():
                    types[m.group(2)] = m.group(1).strip()
            rec = {"id": int(eid), "slug": slug, "dates": [tue, sat], "market": True, "url": page, "notes": notes,
                   "closed": any("closed for your dates" in n for n in notes), "types": types}
            rv = {c: n for c, n in types.items() if not re.search(NOT_RV, n) and (not cats or c in cats)}
            key = "two_night" if nights > 1 else "breakdown"
            rec[key] = [] if nights > 1 else {}
            for d in ([tue] if nights > 1 else [tue, sat]):
                got = []
                for cat, name in rv.items():
                    drv("goto", "url=https://www.campspot.com/%s/site/%s?checkin=%s&checkout=%s&guests=2,0,0"
                        % (slug, cat, d, plus(d, nights)), "wait=9000")
                    got.append("%s %s: %s" % (cat, name, breakdown(drv("text", "max=60000"))))
                if nights > 1:
                    rec[key] += got
                else:
                    rec[key][d] = got
            out.write(json.dumps(rec) + "\n")
            out.flush()
            print(eid, slug, len(types), "types,", len(rv), "read", "| " + " / ".join(notes) if notes else "", flush=True)


if __name__ == "__main__":
    main()
