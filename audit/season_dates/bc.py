#!/usr/bin/env python3
"""BC Parks: season from BC Parks' own operating dates (2026-10-20).

    python3 -I audit/season_dates/bc.py [--apply]

bcparks.ca's park pages and its "Park operating dates" page are drawn from the BC Parks API
(bcparks.api.gov.bc.ca/api/park-features): each frontcountry campground, or each block of
sites within one, carries its "Operation" dates per year plus an off-season note.
bc_parks_features_2026-10-20.json is the snapshot this script reads: for each entry, the park
(its bcparks.ca slug), which campground areas were taken, and their latest posted Operation
dates (2026; 2025 or 2024 where that is the latest posted, which the note says).

An entry named for one campground takes that campground; a park-level entry with several
campgrounds takes all of them. Any part open Jan 1 - Dec 31 makes the entry year-round; else
the season runs from the earliest opening to the latest closing, and the note gives each
part's dates when they differ. Off-season notes that say camping goes on (walk-in access,
winter camping in the day-use lot, "until the lake freezes") are kept; "the gate is closed"
boilerplate is not.

Not written: Kilby, Goldpan, Yard Creek and the two Heather-Dina Lakes entries, which have
no frontcountry campground in the API.
"""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = json.load(open(os.path.join(HERE, "bc_parks_features_2026-10-20.json"), encoding="utf-8"))
SRC = ("https://bcparks.api.gov.bc.ca/api/park-features (Operation dates for {}, the data behind "
       "https://bcparks.ca/{}/ and bcparks.ca/plan-your-trip/park-operating-dates/), read 2026-10-20")
MON = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
KEEP_OFF = re.compile(r"(?i)winter|until the|first snow|sites? \d|self-sufficient|walk|camping is allowed|may be open|might be open")
DROP_OFF = re.compile(r"(?i)not permitted|day-use only|closed in the off-season|^the gates? (are|is) closed (during|in) the winter")


def md(s):
    return f"{MON[int(s[:2]) - 1]} {int(s[3:])}"


def label(sub, multi_area):
    feat = sub["feat"]
    if feat in ("All sites",) or feat == sub["area"]:
        return sub["area"].strip()
    return f"{sub['area'].strip()} {feat}" if multi_area else feat


def part(s, multi_area):
    y = s["ranges"]["year"]
    tag = f" ({y})" if y != 2026 else ""
    return f"{label(s, multi_area)} {', '.join(md(a) + ' - ' + md(b) for a, b in s['ranges']['ranges'])}{tag}"


def decide(v):
    subs = [s for s in v["subs"] if s["ranges"]["ranges"]]
    if not subs:
        return None
    multi_area = len({s["area"] for s in subs}) > 1
    full = [s for s in subs if any(a == "01-01" and b == "12-31" for a, b in s["ranges"]["ranges"])]
    years = sorted({s["ranges"]["year"] for s in subs})
    mixed = len(years) > 1
    notes = []
    if full:
        season = {"year_round": True}
        rest = [s for s in subs if s not in full]
        if rest:
            notes.append("; ".join(part(s, multi_area) for s in rest)
                         + f"; {', '.join(label(s, multi_area) for s in full)} all year.")
    else:
        starts = [a for s in subs for a, b in s["ranges"]["ranges"]]
        ends = [b for s in subs for a, b in s["ranges"]["ranges"]]
        season = {"year_round": False, "opens": min(starts), "closes": max(ends)}
        spans = {tuple(map(tuple, s["ranges"]["ranges"])) for s in subs}
        if mixed or len(spans) > 1 or any(len(s["ranges"]["ranges"]) > 1 for s in subs):
            notes.append("; ".join(part(s, multi_area) for s in subs) + ".")
    if mixed:
        notes.append("BC Parks has not posted 2026 dates for the parts marked with an earlier year.")
    elif years != [2026]:
        notes.append(f"BC Parks has posted no 2026 dates; these are {years[0]}'s.")
    seen = set()
    for s in subs:
        for t in (s.get("opn"), s.get("off")):
            t = html.unescape(t or "").replace("\xa0", " ").strip()
            if t and KEEP_OFF.search(t) and not DROP_OFF.search(t) and t not in seen:
                seen.add(t)
                notes.append(t if t.endswith(".") else t + ".")
    if notes:
        season["note"] = " ".join(notes)
    return season


DECISIONS = {}
for i, v in SNAP.items():
    s = decide(v)
    if s:
        DECISIONS[int(i)] = (s, SRC.format(", ".join(sorted({x["id"] for x in v["subs"]})), v["slug"]))

if __name__ == "__main__":
    run(DECISIONS)
