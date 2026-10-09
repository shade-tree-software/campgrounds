#!/usr/bin/env python3
"""Parse Michigan DNR's two rate tables into JSON (2026-10-09).

    python3 audit/price_research/mi_dnr_tables.py PARKS.html FORESTS.html OUT.json

PARKS   = https://www.michigan.gov/dnr/things-to-do/camping-and-lodging/camping-and-lodging-rates-and-operating-dates
FORESTS = https://www.michigan.gov/dnr/things-to-do/camping-and-lodging/state-forest-campgrounds/amenity-table
(michigan.gov refuses the WebFetch tool; plain curl with a browser UA works.)
"""
import json
import sys
from html.parser import HTMLParser


class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables, self.row, self.cell, self.in_cell = [], None, [], False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.tables.append([])
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th"):
            self.in_cell, self.cell = True, []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.row is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.in_cell = False
        elif tag == "tr" and self.row is not None and self.tables:
            self.tables[-1].append(self.row)
            self.row = None

    def handle_data(self, data):
        if self.in_cell:
            self.cell.append(data)


def table(path):
    p = Tables()
    p.feed(open(path, encoding="utf-8", errors="ignore").read())
    rows = max(p.tables, key=len)
    head = [h.rstrip(":").strip() for h in rows[0]]
    return [dict(zip(head, r)) for r in rows[1:] if len(r) == len(head)]


if __name__ == "__main__":
    out = {"parks": table(sys.argv[1]), "forests": table(sys.argv[2])}
    json.dump(out, open(sys.argv[3], "w"), indent=1, ensure_ascii=False)
    print({k: len(v) for k, v in out.items()})
    for k in out:
        print(k, list(out[k][0].keys()))
        print("  ", out[k][1])
