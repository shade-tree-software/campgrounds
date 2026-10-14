"""ops_view.py OPS_READ.jsonl [ID ...] - print the per-entry digest of ops_read.py's output that was read by hand:
pages (final URL, title), the phones on them (= marks the entry's own number), booking-engine links, and every
line carrying a money figure with two lines of context before and one after (so a rate keeps its label), merged
into blocks, page by page."""
import json, re, sys
MONEY = re.compile(r"\$\s?\d|\d\s?\$|\bUSD\b")
JUNK = lambda l: sum(1 for c in l if ord(c) > 0x2400 or c == "�") > 3
digits = lambda p: re.sub(r"\D", "", p or "")[-10:]
if sys.argv[2:3] == ["--full"]:   # ops_view.py FILE --full ID PAGE [CHARS]: one page's whole text
    for line in open(sys.argv[1], encoding="utf-8"):
        r = json.loads(line)
        if r["id"] == int(sys.argv[3]):
            p = r["pages"][int(sys.argv[4])]
            print(p["final"]); print(p["text"][:int(sys.argv[5]) if len(sys.argv) > 5 else 6000])
    sys.exit()
want = [int(x) for x in sys.argv[2:]]
NOTES = {e["id"]: e for e in json.load(open(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "../../../campgrounds.json"), encoding="utf-8")) if e["id"] in set(want)} if want else {}
recs = {}
for line in open(sys.argv[1], encoding="utf-8"):
    r = json.loads(line)
    recs[r["id"]] = r
for i in (want or sorted(recs)):
    r = recs[i]
    ours = digits(r.get("phone"))
    print(f"\n=== {r['id']} {r['name']} ({r['state']}, {r['ownership']}) phone {r.get('phone')}"
          + ("  PARKED?" if r.get("parked") else ""))
    if r["id"] in NOTES:
        print("  note:", (NOTES[r["id"]].get("note") or "")[:420])
        print("  web:", (NOTES[r["id"]].get("website") or "").replace("\n", " ; ")[:300])
    for e in r["errors"]:
        print("  ERR", e[:150])
    ph = [("=" if digits(p) == ours else "") + p for p in r["phones"][:6]]
    print("  phones:", ", ".join(ph) or "-", "| ours on site:", "YES" if any(x.startswith("=") for x in ph) else "no")
    if r["engines"]:
        print("  engines:", " ".join(u[:90] for u in r["engines"][:5]))
    seen, budget = set(), 55
    for pi, p in enumerate(r["pages"]):
        if p["final"] in seen:
            continue
        seen.add(p["final"])
        lines = [l for l in p["text"].split("\n") if not JUNK(l)]
        hits = [k for k, l in enumerate(lines) if MONEY.search(l) and len(l) < 400]
        print(f"  p{pi} [{p['final'][:100]}] {p['title'][:60]!r} {len(p['text'])}ch {len(hits)} $")
        if not hits or budget <= 0:
            continue
        show = sorted({j for k in hits for j in range(max(0, k - 2), min(len(lines), k + 2))})
        prev = None
        for j in show:
            if budget <= 0:
                print("      ..."); break
            if prev is not None and j != prev + 1:
                print("      --")
            print("      " + lines[j][:150]); prev = j; budget -= 1
