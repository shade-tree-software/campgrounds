#!/usr/bin/env python3
"""List the entries that still have no nightly rate (2026-10-10).

    python3 audit/price_research/unpriced.py [--state CO] [--ownership federal] [--json OUT]
    python3 audit/price_research/unpriced.py --from-note [--state CO] [--ownership private]

"Priced" means a nightly_low or nightly_high, the entry's own or inherited from
its policy row, or an RV Life price_tier. A fees group alone is NOT a price:
309 entries inherit a row that carries only a note, a surcharge, an entrance or
a reservation fee, and counting those as priced hid them from every pass before
this date.

--from-note lists the other side of the line: entries counted as priced only
because the figure was taken from our own note (provenance.fees method
"derived", source "our note (written DATE): '<quote>'; recheck <url>"), after
the operator stopped showing it (AWH 2026-10-11: accept the note). Each line
ends with the page to re-check; feed the printed ids to site_digest.py --ids,
and land a confirmed figure with apply.py --replace-derived.
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


def from_note(entry):
    """provenance.fees.source when the entry's rate rests only on our own note, else None."""
    p = (entry.get(cs.PROVENANCE) or {}).get("fees") or {}
    src = str(p.get("source") or "")
    return src if p.get("method") == "derived" and src.startswith("our note") else None


def unpriced(rows=None, reg=None):
    rows = rows if rows is not None else json.load(open(os.path.join(ROOT, "campgrounds.json")))
    reg = reg if reg is not None else registry()
    return [r for r in rows if r.get("kind") == "campground" and not has_rate(r, reg)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state")
    ap.add_argument("--ownership")
    ap.add_argument("--json")
    ap.add_argument("--from-note", action="store_true",
                    help="list the entries priced only from our own note (due a re-check)")
    a = ap.parse_args()
    if a.from_note:
        rows = json.load(open(os.path.join(ROOT, "campgrounds.json")))
        todo = [r for r in rows if from_note(r)
                and (not a.state or r.get("state") == a.state) and (not a.ownership or r.get("ownership") == a.ownership)]
        for r in todo:
            recheck = from_note(r).split("; recheck ", 1)[-1]
            print(f"{r['id']:>6} {r.get('ownership') or '-':8} {r.get('state') or '-':3} {r['name']} | {recheck}")
        print(len(todo), "priced from our own note; re-read with site_digest.py --ids",
              ",".join(str(r["id"]) for r in todo))
        return
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
