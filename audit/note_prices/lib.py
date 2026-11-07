"""Shared pieces of the note-price cleanup (AWH 2026-11-07).

AWH: "remove the extra person charge info from the note wherever this has been recorded in the new
field ... remove the base price if it has been recorded in the price field. This includes --AWH notes
too." Example of why: Low Water Bridge 12's --AWH note still said $50/night after fees took the 2026
rate page ($35-60). The structured fees are the record; a note repeating them goes stale.

Every edit is DELETION ONLY: the cleaned note may add no word the old note lacked beyond a few
joining words (JOIN), so it can carry no new fact, and an --AWH segment that survives is still AWH's
words. That is also why a matching note_scan sig is re-stamped: everything left was already scanned.
"""
import collections, hashlib, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

CG = os.path.join(ROOT, "campgrounds.json")
REG = os.path.join(ROOT, "campground_policies.json")
PRICE = re.compile(r"(C?\$|CAD|US\$)\s?\d|\b\d+\s?(dollars|/night|a night|per night)\b|\bfree\b|no fee|no charge", re.I)
XP = re.compile(r"(extra|additional|each other) (adults?|persons?|guests?|people|campers?|child(ren)?|kids?)"
                r"|(adults?|persons?|people|guests?) (beyond|over|above|after)", re.I)
JOIN = {"and", "a", "an", "the", "with", "or", "but", "also", "is", "are", "has", "have", "of", "to",
        "in", "on", "for", "at", "its", "it", "sites", "site"}
WORD = re.compile(r"[a-z0-9]+")

def sig(note): return hashlib.sha256((note or "").encode("utf-8")).hexdigest()[:16]

def load():
    raw = open(CG, encoding="utf-8").read(); cg = json.loads(raw)
    assert json.dumps(cg, ensure_ascii=False, indent=2) + "\n" == raw
    return cg, json.load(open(REG, encoding="utf-8"))

def fees(e, reg): return cs.resolve(e, reg).get("fees", {}).get("values", {})

def in_scope(e, reg):
    n = e.get("note") or ""
    f = fees(e, reg)
    base = ("nightly_low" in f or "nightly_high" in f) and bool(PRICE.search(n))
    xp = "extra_person" in f and bool(XP.search(n))
    return base or xp

def added_words(old, new):
    extra = collections.Counter(WORD.findall(new.lower())) - collections.Counter(WORD.findall(old.lower()))
    return sorted(w for w in extra if w not in JOIN)

def dump(cg):
    tmp = CG + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(cg, ensure_ascii=False, indent=2) + "\n")
    os.replace(tmp, CG)

def land(cg, items, today, apply):
    """items: [{id, was, note, awh_dropped?}] -> writes notes, re-tags note-prose provenance,
    re-stamps a note_scan sig that matched the old note. Returns (done, refused)."""
    by = {e["id"]: e for e in cg}; done = []; refused = []
    tag = f"note prose (cleaned out of the note {today})"
    for it in items:
        e = by[it["id"]]; old = e.get("note") or ""
        why = None
        if old != it["was"]: why = "note changed since it was read"
        elif added_words(old, it["note"]): why = "adds words " + ",".join(added_words(old, it["note"]))
        elif old.count("--AWH") > it["note"].count("--AWH") and not it.get("awh_dropped"): why = "loses an --AWH marker"
        elif it["note"] == old: why = "unchanged"
        if why: refused.append((e["id"], why)); continue
        for g, p in (e.get("provenance") or {}).items():
            if isinstance(p, dict) and p.get("source") == "note prose": p["source"] = tag
        ns = e.get("note_scan")
        if isinstance(ns, dict) and ns.get("sig") == sig(old): ns["sig"] = sig(it["note"])
        if it["note"].strip(): e["note"] = it["note"]
        else: e.pop("note", None)
        done.append(e["id"])
    if apply and done: dump(cg)
    return done, refused
