"""The Firefly pass (2026-10-14): python3 -I firefly_apply.py [--apply]

The 55 tier-only entries that link a Firefly Reservations page. Firefly sits behind reCAPTCHA, so each is priced
from the operator's own pages (ops_read.py output in pages.jsonl), under AWH's rules of 2026-10-14: #3-#8 and the
answers of that evening (an RV Life $ or $$ keeps a park that posts no rate; a Google listing, open with a phone
and 25+ reviews, stands in for a website; the long-stay rule). decisions.py holds the per-entry calls, with the
same keys as roverpass_ops_2026-10-14/decisions.py. Copied from roverpass_ops_apply.py; the RoverPass-specific
link stripping applies only where decisions.py says drop_web.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import campground_schema as cs  # noqa: E402
import trips  # noqa: E402
from decisions import D as DECISIONS  # noqa: E402

D = "2026-10-14"
READ = f"read {D}"
LIVE = (f"AWH 2026-09-08: no working site and no active booking listing means exclude; AWH {D} #5: 'keep if "
        "(published prices on regular website and phone number) or active booking site, drop otherwise'")
RULES = {
    "LIVE": LIVE,
    "OVER": (f"AWH {D}: over the price limit, drop unless we have an exception in place or they are near major "
             "gateway points"),
    "SEASONAL": ("not a real transient campground: no nightly RV site for the public, only seasonal, monthly or "
                 "residential stays (docs/campground-curation.md)"),
    "EVENT": "fairgrounds that only allow camping during events are never added (docs/campground-curation.md)",
    "MEMBERSHIP": "membership and club parks are not a real transient campground (docs/campground-curation.md)",
    "NORV": ("an entry must be a drive-in RV campground, and its own site no longer offers RV sites (precedent Red "
             "Pine Lodge, AWH 2026-10-11)"),
    "LONGSTAY": ("a long-stay park that also sells nights must pass AWH's five tests of 2026-10-14 "
                 "(docs/campground-curation.md)"),
    "CLOSED": ("closed for good: a permanent closure leaves the database, only a temporary one is recorded "
               "(docs/campground-schema.md §4.5)"),
}
PRIVATE_ONLY = {"LIVE", "OVER"}       # town and county parks are exempt from these two
TAIL = "(Firefly pass, read 2026-10-14; {})"
IE = f"re-check {D} (Firefly pass)"
HUMAN = {"manual", "reported"}
# the quotes of a fees page that also speak to booking, when a booking change has no page of its own
BOOKISH = r"(?i)minim|reserv|\bmin\b|book|deposit"


def q(quotes):
    return "; ".join(f"'{x}'" for x in quotes)


def src_text(s, keep=None):
    """A provenance source: a plain string verbatim, or (url, [quotes]) as 'url ('q1'; 'q2'), read D'."""
    if isinstance(s, str):
        return s
    url, quotes = s
    if keep:
        quotes = [x for x in quotes if re.search(keep, x)]
    return f"{url} ({q(quotes)}), {READ}" if quotes else f"{url}, {READ}"


def links_of(e):
    return [x for x in (e.get("website") or "").split("\n") if x.strip()]


def as_list(x):
    return [] if x is None else [x] if isinstance(x, str) else list(x)


def add_ie(e, line):
    ie = e.get("inclusion_evidence") or ""
    if line in ie:
        return
    e["inclusion_evidence"] = f"{ie}; {line}" if ie else line


def money(lo, hi):
    if hi is None:
        return f"from ${lo:g}"
    return f"${lo:g}" if hi == lo else f"${lo:g}-{hi:g}"


def merged(old, upd, prov_old, src, what):
    """Merge `upd` (None deletes a key) into a group a machine wrote; the provenance names what was kept and
    replaced. Returns (group, provenance) or None when a person verified the group."""
    if (prov_old or {}).get("method") in HUMAN:
        return None
    new = dict(old)
    for k, v in upd.items():
        if v is None:
            new.pop(k, None)
        else:
            new[k] = v
    bits = [src] if src else []
    if old:
        kept = {k: v for k, v in old.items() if k not in upd}
        repl = {k: old[k] for k, v in upd.items() if k in old and old[k] != v}
        if kept:
            bits.append(f"kept from the {what}: " + json.dumps(kept))
        if repl:
            bits.append(f"replaces the {what}'s " + json.dumps(repl))
    return new, {"source": "; ".join(bits), "checked": D}


def origin(prov):
    s = (prov or {}).get("source") or ""
    if s.startswith("note prose"):
        return "note"
    if s.startswith("Good Sam"):
        return f"{s} ({(prov or {}).get('checked')})"
    return None


def apply_entry(e, v, warn):
    """Everything but a drop; returns the list of things changed, for the dry-run print."""
    i = e["id"]
    did = []
    ie = []
    prov = dict(e.get(cs.PROVENANCE) or {})
    upd = {}
    # name and phone (#8, #6)
    if v.get("name") and v["name"] != e["name"]:
        ie.append(f"renamed from '{e['name']}' to the name it publishes now (#8)")
        did.append(f"name {e['name']!r} -> {v['name']!r}")
        e["name"] = v["name"]
    if v.get("phone") and v["phone"] != e.get("phone"):
        if e.get("phone"):
            ie.append(f"phone {e['phone']} replaced by {v['phone']}, the number the park publishes (#6)")
        did.append(f"phone {e.get('phone')} -> {v['phone']}")
        e["phone"] = v["phone"]
    # links: the unclaimed RoverPass listing goes unless a town or county park has no page of its own
    links = links_of(e)
    rp = [x for x in links if "roverpass.com" in x]
    drop = set(as_list(v.get("drop_web")))
    for x in drop:
        assert x in links, (i, "drop_web not on the entry", x)
    keep = [x for x in links if x not in drop]
    for x in as_list(v.get("add_web")):
        if x not in keep:
            keep.append(x)
    if keep != links:
        assert keep, (i, "no link left")
        did.append(f"links {len(links)} -> {len(keep)}")
        e["website"] = "\n".join(keep)
    # note
    old_note = e.get("note") or ""
    if v.get("note") and v["note"] != old_note:
        if "AWH" in old_note:
            assert "AWH" in v["note"], (i, "the note's --AWH text would be lost")
        e["note"] = v["note"]
        did.append("note")
    if v.get("note_add") and v["note_add"] not in e.get("note", ""):
        e["note"] = f"{e.get('note', '').rstrip()} {v['note_add']}".strip()
        did.append("note_add")
    # fees
    if v.get("fees"):
        f = v["fees"]
        lo, hi, text = f[0], f[1], f[2]
        cur = f[3] if len(f) > 3 else "USD"
        chk = f[4] if len(f) > 4 else "2026"
        assert not e.get("fees"), (i, "already priced", e.get("fees"))
        assert (prov.get("fees") or {}).get("method") not in HUMAN, i
        if isinstance(v["src"], str):
            assert e.get("ownership") == "local", (i, "a camper report prices a local entry only")
        fees = {"nightly_low": lo}
        if hi is not None:
            fees["nightly_high"] = hi
        fees["currency"] = cur
        if v.get("rf"):
            fees["reservation_fee"] = v["rf"]
        fees.update(checked=chk, note=text)
        upd["fees"] = fees
        source = src_text(v["src"]) + (f"; {v['src2']}" if v.get("src2") else "")
        prov["fees"] = {"source": source, "checked": D}
        did.append(f"fees {money(lo, hi)}")
    # booking
    bupd = dict(v.get("booking") or {})
    if v.get("min_stay"):
        bupd["min_stay"] = v["min_stay"]
    if v.get("booking_note"):
        bupd["note"] = v["booking_note"]
    if bupd:
        old = e.get("booking") or {}
        what = origin(prov.get("booking")) if old else "note"
        if old and what is None:
            warn.append(f"{i}: booking left alone, written by {(prov.get('booking') or {}).get('source')!r}")
        else:
            bsrc = (src_text(v["booking_src"]) if v.get("booking_src")
                    else src_text(v["src"], keep=BOOKISH) if v.get("src") else None)
            m = merged(old, bupd, prov.get("booking"), bsrc, what)
            if m is None:
                warn.append(f"{i}: booking verified by a person, left alone")
            else:
                new, p = m
                if new:
                    assert bsrc, (i, "a booking change needs a source")
                    upd["booking"] = dict(new, **{k: None for k in old if k not in new})
                    prov["booking"] = p
                else:
                    upd["booking"] = None
                    prov["booking"] = None
                did.append(f"booking {json.dumps(old)} -> {json.dumps(new) if new else 'removed'}")
    # discounts
    if v.get("disc"):
        dupd, dsrc = v["disc"]
        old = e.get("discounts") or {}
        what = origin(prov.get("discounts")) if old else "note"
        if old and what is None:
            warn.append(f"{i}: discounts left alone, written by {(prov.get('discounts') or {}).get('source')!r}")
        else:
            m = merged(old, dupd, prov.get("discounts"), src_text(dsrc), what)
            if m is None:
                warn.append(f"{i}: discounts verified by a person, left alone")
            else:
                new, p = m
                upd["discounts"] = new
                prov["discounts"] = p
                did.append(f"discounts {json.dumps(old)} -> {json.dumps(new)}")
    if upd:
        payload = dict(upd)
        payload[cs.PROVENANCE] = {g: prov.get(g) for g in upd}
        cs.apply_update(e, payload)
        if not e.get(cs.PROVENANCE):
            e.pop(cs.PROVENANCE, None)
    # inclusion_evidence
    act = v["act"]
    if act == "price":
        how = ("a camper-reported rate (the operator posts none)" if isinstance(v["src"], str)
               else f"priced from {v['src'][0]}")
        ie.append(f"{how}, {money(v['fees'][0], v['fees'][1])} a night")
        if v.get("hold") == "2":
            ie.append("a long-stay park with nightly sites, held for AWH's #2 criteria"
                      + (f" ({v['why']})" if v.get("why") else ""))
    elif act == "hold":
        ie.append("held: live site and phone, but no published rate and no booking site (AWH question (b))"
                  if v["hold"] == "b" else
                  "held: a long-stay park with nightly sites and no published rate, for AWH's #2 criteria"
                  + (f" ({v['why']})" if v.get("why") else ""))
    elif act == "keep":
        ie.append("kept" + (f": {v['why']}" if v.get("why") else ""))
    if ie:
        add_ie(e, f"{IE}: " + "; ".join(ie))
    if v.get("ie"):
        add_ie(e, v["ie"])
    return did


def main():
    apply = "--apply" in sys.argv
    amend_only = "--amend-only" in sys.argv
    no_amend = "--no-amend" in sys.argv
    assert not (amend_only and no_amend)
    path = os.path.join(ROOT, "campgrounds.json")
    rows = json.load(open(path, encoding="utf-8"))
    by = {r["id"]: r for r in rows}
    warn, log, edited = [], [], []
    for i, v in sorted(DECISIONS.items()):
        e = by.get(i)
        if e is None:
            print(i, "not in campgrounds.json (already applied?)")
            continue
        if v["act"] == "drop":
            if (amend_only and not v.get("amend")) or (no_amend and v.get("amend")):
                continue
            if v["rule"] in PRIVATE_ONLY:
                assert e.get("ownership") == "private", (i, e.get("ownership"), v["rule"])
            assert not trips.campground_references(i), (i, "referenced by a trip")
            log.append({"id": i, "name": e["name"], "state": e["state"], "ownership": e.get("ownership"),
                        "action": "removed", "why": f"{v['why']} {TAIL.format(RULES[v['rule']])}"})
            continue
        if amend_only:
            continue
        before = (e.get("note") or "")
        did = apply_entry(e, v, warn)
        if (e.get("note") or "") != before:
            edited.append(i)
        print(i, v["act"], e["name"], "|", "; ".join(did) or "ie only")
    gone = {x["id"] for x in log}
    rows[:] = [r for r in rows if r["id"] not in gone]
    for x in log:
        print("drop", x["id"], x["state"], x["ownership"], x["name"])
    for r in rows:                        # a final check of every touched entry
        if r["id"] in DECISIONS and DECISIONS[r["id"]]["act"] != "drop":
            cs.validate_row(r, f"id {r['id']}")
    for w in warn:
        print("WARN", w)
    print(f"{len(log)} drops; {len(edited)} notes edited:", ",".join(map(str, edited)))
    if apply:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)
        with open(os.path.join(os.path.dirname(HERE), "dropped_2026-10-11.jsonl"), "a", encoding="utf-8") as fh:
            for x in log:
                fh.write(json.dumps(x, ensure_ascii=False) + "\n")
        with open(os.path.join(HERE, "edited_notes.txt"), "a", encoding="utf-8") as fh:
            fh.write("\n".join(map(str, edited)) + ("\n" if edited else ""))
        print("written")
    else:
        print("(dry run)")


if __name__ == "__main__":
    main()
