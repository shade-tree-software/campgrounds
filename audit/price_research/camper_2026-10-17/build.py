#!/usr/bin/env python3
"""Write camper-reported prices (AWH 2026-10-11 rule, feedback_camper_report_rates) from rows.txt.

    python3 -I audit/price_research/camper_2026-10-17/build.py [--apply]

rows.txt lines: id | low | high | CUR | fees note | note sentence
  - fees note: who paid what and when ("A Campendium reviewer paid $40 a night in May 2026.").
  - note sentence: the sentence that goes into the campground note; it must call the rate camper-reported
    and give its month. It is placed before the note's own trailing "--Claude" marker when the note ends
    with one (so the note stays one clean paragraph), else appended with " --Claude".
A row whose id already has fees, or whose fees group is manual/reported, is skipped. provenance.fees.source
is the Campendium URL from cpd.jsonl plus the report dates quoted in the fees note. Dry run unless --apply;
the dry run prints every new note in full for review.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
import extract_fields as ef     # noqa: E402

TODAY = "2026-10-17"
apply = "--apply" in sys.argv
cpd = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(HERE, "cpd.jsonl"))}
rows = ef.load_rows()
by_id = {r["id"]: r for r in rows}
# notefix.txt: id | old text | new text  -- a stale rate in the note that the camper sentence supersedes
fixes = {}
fp = os.path.join(HERE, "notefix.txt")
if os.path.exists(fp):
    for line in open(fp):
        if line.strip() and not line.startswith("#"):
            a, old, new = [x.strip() for x in line.split("|", 2)]
            fixes.setdefault(int(a), []).append((old, new))
wrote, skipped = 0, []
for line in open(os.path.join(HERE, "rows.txt")):
    if not line.strip() or line.startswith("#"):
        continue
    i, lo, hi, cur, fnote, sent = [x.strip() for x in line.split("|", 5)]
    i = int(i)
    e = by_id[i]
    if e.get("fees") or ef.human_verified(e, "fees"):
        skipped.append(i); continue
    assert re.search(r"(?i)camper", sent) and re.search(r"(19|20)\d\d", sent), (i, sent)
    fees = {"nightly_low": float(lo) if "." in lo else int(lo), "nightly_high": float(hi) if "." in hi else int(hi),
            "currency": cur, "note": fnote}
    cs.apply_update({}, {"fees": fees})
    note = (e.get("note") or "").rstrip()
    for old, newt in fixes.get(i, []):
        assert note.count(old) == 1, (i, old)
        note = re.sub(r"  +", " ", note.replace(old, newt)).replace(" .", ".")
    m = re.search(r"\s*--Claude$", note)
    if m:
        new = note[:m.start()].rstrip() + " " + sent + " --Claude"
    elif note:
        new = note + " " + sent + " --Claude"
    else:
        new = sent + " --Claude"
    src = f"{cpd[i]['url']} (camper reports quoted in fees.note; read {TODAY})"
    print(f"## {i} {e['name']}: {lo}-{hi} {cur}\n   {new}\n")
    if apply:
        prov = dict(e.get(cs.PROVENANCE) or {})
        prov["fees"] = {"source": src, "checked": TODAY}
        e["note"] = new
        cs.apply_update(e, {"fees": fees, cs.PROVENANCE: prov})
    wrote += 1
print(f"{wrote} {'written' if apply else 'would write'}, skipped {skipped}")
if apply and wrote:
    tmp = os.path.join(ROOT, "campgrounds.json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False); fh.write("\n")
    os.replace(tmp, os.path.join(ROOT, "campgrounds.json"))
