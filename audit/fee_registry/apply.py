"""Land fee-registry research rows (BRIEF.md format) on campground_policies.json.

    python3 audit/fee_registry/apply.py out/b01.json            # dry run: prints the changes
    python3 audit/fee_registry/apply.py out/b01.json --apply

Every `set` is validated against the schema (cs.validate_row) before it lands,
and the whole row again after. A key in `set` needs a source quote for it; a
row whose ref is not in the registry is refused unless the research file says
`"create": true` (new federal agency rows). The row's provenance.fees source
gains the add-on sources; its method only drops to "reported" for a key that
was read secondhand, and that is written into the source text.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..", "..")
sys.path.insert(0, REPO)
import campground_schema as cs  # noqa: E402

REG = os.path.join(REPO, "campground_policies.json")
DATE = "2026-11-07"


def main():
    path = sys.argv[1]
    apply = "--apply" in sys.argv
    rows = json.load(open(path))
    reg = json.load(open(REG))
    problems = []
    for r in rows:
        ref = r["ref"]
        if ref not in reg and not r.get("create"):
            problems.append(f"{ref}: not in registry")
            continue
        row = reg.setdefault(ref, {})
        set_ = r.get("set") or {}
        quoted = {s.get("key") for s in r.get("sources") or [] if s.get("quote") and s.get("url")}
        for k in set_:
            if k not in quoted:
                problems.append(f"{ref}: {k} set with no quoted source")
        try:
            staged = cs.validate_row({"fees": set_})["fees"] if set_ else {}
        except cs.SchemaError as ex:
            problems.append(f"{ref}: {ex}")
            continue
        fees = row.setdefault("fees", {})
        before = json.dumps(fees, sort_keys=True)
        changes = []
        for k, v in staged.items():
            if fees.get(k) != v:
                changes.append(f"  {k}: {json.dumps(fees.get(k))} -> {json.dumps(v)}")
            fees[k] = v
        for k in r.get("remove") or []:
            if k in fees:
                changes.append(f"  {k}: {json.dumps(fees[k])} -> (removed)")
                fees.pop(k)
        add = (r.get("note_add") or "").strip()
        if add:
            fees["note"] = ((fees.get("note") or "").rstrip() + " " if fees.get("note") else "") \
                + f"Add-ons ({DATE}): " + add
            changes.append(f"  note += {add[:140]}")
        if json.dumps(fees, sort_keys=True) != before:
            fees["checked"] = DATE[:7]
            prov = row.setdefault("provenance", {}).setdefault("fees", {})
            by_key = r.get("method_by_key") or {}
            srcs = "; ".join(
                f"{s['key']}: {s['url']}" + (" (search summary, not the page)"
                                             if by_key.get(s["key"]) == "reported" else "")
                for s in r.get("sources") or [] if s.get("url"))
            if srcs:
                prov["source"] = ((prov.get("source") or "") + " | " if prov.get("source") else "") \
                    + f"add-ons {DATE}: " + srcs
            prov["checked"] = DATE
            if not prov.get("method") or prov.get("method") == "derived":
                prov["method"] = r.get("method") or "manual"
            if any(v == "reported" for k, v in by_key.items() if k in staged) and not prov.get("method"):
                prov["method"] = "reported"
        try:
            cs.validate_row(row, ref)
        except cs.SchemaError as ex:
            problems.append(f"{ref}: whole row: {ex}")
        print(ref, "—", r.get("summary", ""))
        for c in changes:
            print(c)
        if r.get("unsettled"):
            print("  unsettled:", json.dumps(r["unsettled"], ensure_ascii=False)[:400])
    if problems:
        print("\nPROBLEMS:\n  " + "\n  ".join(problems))
        sys.exit(1)
    if apply:
        with open(REG, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(reg, indent=2, ensure_ascii=False) + "\n")
        print("\napplied", len(rows), "rows")


if __name__ == "__main__":
    main()
