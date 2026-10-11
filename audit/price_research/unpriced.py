#!/usr/bin/env python3
"""List the entries that still have no nightly rate (2026-10-10).

    python3 audit/price_research/unpriced.py [--state CO] [--ownership federal] [--json OUT]

"Priced" means a nightly_low or nightly_high, the entry's own or inherited from
its policy row, or an RV Life price_tier. A fees group alone is NOT a price:
309 entries inherit a row that carries only a note, a surcharge, an entrance or
a reservation fee, and counting those as priced hid them from every pass before
this date.
"""
import argparse, collections, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402


def registry():
    return json.load(open(os.path.join(ROOT, "campground_policies.json")))


def has_rate(entry, reg):
    if (entry.get("rating") or {}).get("price_tier") is not None:
        return True
    fees = (cs.resolve(entry, reg).get("fees") or {}).get("values", {})
    return "nightly_low" in fees or "nightly_high" in fees


def unpriced(rows=None, reg=None):
    rows = rows if rows is not None else json.load(open(os.path.join(ROOT, "campgrounds.json")))
    reg = reg if reg is not None else registry()
    return [r for r in rows if r.get("kind") == "campground" and not has_rate(r, reg)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state")
    ap.add_argument("--ownership")
    ap.add_argument("--json")
    a = ap.parse_args()
    todo = [r for r in unpriced()
            if (not a.state or r.get("state") == a.state) and (not a.ownership or r.get("ownership") == a.ownership)]
    if a.json:
        json.dump([{k: r.get(k) for k in ("id", "name", "state", "ownership", "website", "phone", "note", "status")}
                   for r in todo], open(a.json, "w"), ensure_ascii=False, indent=1)
    for r in todo:
        closed = " [closed]" if (r.get("status") or {}).get("operating") == "temporarily_closed" else ""
        print(f"{r['id']:>6} {r.get('ownership') or '-':8} {r.get('state') or '-':3} {r['name']}{closed}")
    print(len(todo), "unpriced;", dict(collections.Counter(r.get("ownership") for r in todo)))


if __name__ == "__main__":
    main()
