#!/usr/bin/env python3
"""Season dates read out of the notes (AWH 2026-11-07).

    python3 -I audit/season_dates/notes_pass.py [--apply]

1,781 campgrounds were recorded as seasonal (`year_round: false`) with no dates, so the
map's Dates filter could only fade them. Most notes say WHEN, just not to the day
("open May to October", "Memorial Day to Labor Day"), and the note-scan spec
(extract_fields.py) deliberately leaves a month with no day undated. AWH chose the widest
span, marked: the stored days take the widest reading of the wording, under the
convention common.py documents (bare month = whole month, mid = 15th, early opens 1st /
closes 7th, late opens 20th / closes the last day, holidays at their widest date), and
`season.note` gains "Approximate: <what the note states>" so the popup never passes a
widened day off as a published one. Day-level wording is written as stated, unmarked.

The reading was done by session agents over notes_2026-11-07/chunk_*.json (the inputs)
into out_*.json, under notes_2026-11-07/brief.txt. This script is the only writer:

- every proposal's `quote` must occur verbatim in the entry's note or season note, or it
  is refused (listed under REFUSED);
- dates go through campground_schema.apply_update, which validates MM-DD;
- a season whose provenance is a person (method `manual`) takes dates only from its own
  season note, the text that person wrote from their source; a date read from the entry
  note there would mix a sweep's prose into a sourced group, so it is listed instead;
  its provenance is kept, since the dates restate that source;
- a note-derived season is re-stamped `note prose` / `derived` with today's date;
- `year_round: true` proposals are NOT written here; they are printed for a person.

Dry run unless --apply.
"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

CG = os.path.join(ROOT, "campgrounds.json")
DIR = os.path.join(HERE, "notes_2026-11-07")
DAY = "2026-11-07"
MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def norm(s):
    return re.sub(r"\s+", " ", (s or "").replace("–", "-").replace("—", "-")).strip().lower()


def mmdd_ok(v):
    m = re.fullmatch(r"(\d\d)-(\d\d)", v or "")
    return bool(m) and 1 <= int(m[1]) <= 12 and 1 <= int(m[2]) <= MONTH_DAYS[int(m[1]) - 1]


# Reader calls corrected on review. A one-year extension ("in 2026 it stays open to Nov 15
# with limited services") is not the recurring season: the base months are.
OVERRIDES = {i: {"closes": "09-30"} for i in (2492, 2493, 2554, 2557, 2558, 2559)}
# "Closed November to April": the widest open reading reopens in April, as 1689's
# "closed mid-Jan to Mar" reopens March 1.
OVERRIDES[3687] = {"opens": "04-01"}
# "potable water/vault toilets, mid-June-Sept" may be the water season, not the camping one.
OVERRIDES[6490] = {"skip": "months follow the water/toilets clause"}


def main():
    cg = json.load(open(CG, encoding="utf-8"))
    by = {e["id"]: e for e in cg}
    outs = []
    for path in sorted(glob.glob(os.path.join(DIR, "out_*.json"))):
        outs += json.load(open(path, encoding="utf-8"))
    for r in outs:
        r.update(OVERRIDES.get(r["id"], {}))
    wrote, refused, year_round, skips = [], [], [], 0
    for r in outs:
        if "skip" in r:
            skips += 1
            continue
        e = by.get(r["id"])
        if e is None:
            refused.append((r["id"], "no such entry"))
            continue
        season = e.get("season") or {}
        if season.get("year_round") is True or season.get("opens") or season.get("closes"):
            refused.append((r["id"], "season changed since the dump"))
            continue
        note, snote = norm(e.get("note")), norm(season.get("note"))
        quote = norm(r.get("quote"))
        in_snote, in_note = bool(quote) and quote in snote, bool(quote) and quote in note
        if not (in_snote or in_note):
            refused.append((r["id"], f"quote not found: {r.get('quote')!r}"))
            continue
        if r.get("year_round") is True:
            year_round.append(r)
            continue
        if not (mmdd_ok(r.get("opens")) and mmdd_ok(r.get("closes"))):
            refused.append((r["id"], f"bad dates {r.get('opens')}/{r.get('closes')}"))
            continue
        if r["opens"] == r["closes"]:
            refused.append((r["id"], "opens == closes"))
            continue
        if r.get("exact") and not re.search(r"\d", quote):
            refused.append((r["id"], "exact, but the quote holds no day"))
            continue
        prov = (e.get("provenance") or {}).get("season") or {}
        manual = prov.get("method") == "manual"
        if manual and not in_snote:
            refused.append((r["id"], "manual season; dates only in the entry note"))
            continue
        new = {"year_round": False, "opens": r["opens"], "closes": r["closes"]}
        text = (season.get("note") or "").strip()
        if not r.get("exact"):
            approx = (r.get("approx_text") or "").strip()
            if approx:
                approx = approx[0].upper() + approx[1:]
                if not approx.endswith("."):
                    approx += "."
                text = (text + " " if text else "") + "Approximate: " + approx
            elif not text:
                refused.append((r["id"], "approximate, with no wording to mark it"))
                continue
        if text:
            new["note"] = text
        update = {"season": new}
        if not manual:
            update["provenance"] = {"season": {"source": "note prose", "checked": DAY,
                                               "method": "derived"}}
        order = list(e)  # apply_update re-adds `season` last; keep it where it was
        cs.apply_update(e, {"season": None})
        cs.apply_update(e, update)
        moved = {k: e.pop(k) for k in list(e)}
        e.update({k: moved[k] for k in order if k in moved})
        e.update(moved)
        wrote.append((e["id"], e["name"], new, r.get("exact")))
    for i, name, new, exact in wrote:
        print(f"  {i} {name[:40]:40} {new['opens']}..{new['closes']}"
              f" {'exact' if exact else 'approx'}  {new.get('note', '')[-90:]}")
    print("\nYEAR-ROUND PROPOSALS (not written):")
    for r in year_round:
        print(f"  {r['id']} {by[r['id']]['name'][:40]}: {r.get('quote')!r} -- {r.get('why')}")
    print("\nREFUSED:")
    for i, why in refused:
        print(f"  {i}: {why}")
    exact = sum(1 for w in wrote if w[3])
    print(f"\n{len(outs)} rows: {len(wrote)} dated ({exact} exact, {len(wrote) - exact} approx),"
          f" {len(year_round)} year-round proposals, {len(refused)} refused, {skips} skipped")
    if "--apply" in sys.argv:
        with open(CG, "w", encoding="utf-8") as f:
            json.dump(cg, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("written")


if __name__ == "__main__":
    main()
