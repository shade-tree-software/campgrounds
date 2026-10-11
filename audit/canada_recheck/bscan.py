#!/usr/bin/env python3
"""Browser pass for the entries scan.py could not read (`browser: true`): same patterns, rendered text.

    python3 -I audit/canada_recheck/bscan.py [--ids 1,2,3]

Needs the one-browser driver running (audit/private_gap_browser/README.md):
    PYTHONPATH=~/.cache/ekko-pw python3 -u audit/private_gap_browser/drv_server.py
Opens each website and up to 4 same-site pages whose link mentions FAQ / rates / camping /
sites / booking / rules, reads innerText, and writes the result to bscan_2026-10-11.json
(its own file, so it can run while scan.py is still writing; saved after every entry, and a
rerun skips entries already done).
"""
import argparse, json, os, socket, sys, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scan  # noqa: E402

BOUT = os.path.join(HERE, "bscan_2026-10-11.json")
SOCK = os.environ.get("DRV_SOCK", os.path.expanduser("~/.cache/ekko-drv.sock"))
JS = r"""(()=>{const t=document.body?document.body.innerText:'';
const L=[...document.querySelectorAll('a[href]')].map(a=>[(a.innerText||'').replace(/\s+/g,' ').trim().slice(0,60),a.href]);
return JSON.stringify({title:document.title,url:location.href,text:t.slice(0,300000),links:L.slice(0,500)})})()"""


def call(**req):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(150)
    s.connect(SOCK)
    s.sendall((json.dumps(req) + "\n").encode())
    buf = b""
    while not buf.endswith(b"\n"):
        c = s.recv(1 << 20)
        if not c:
            break
        buf += c
    r = json.loads(buf.decode())
    return r["out"] if r["ok"] else "ERROR: " + str(r["out"])


def read(url):
    g = call(cmd="goto", url=url, wait="7000")
    raw = call(cmd="eval", js=JS)
    try:
        d = json.loads(raw)
    except Exception:
        return {"url": url, "error": (g + " " + raw)[:200]}, [], []
    lines = [l.strip() for l in d["text"].split("\n") if l.strip()]
    return {"url": url, "final": d["url"], "title": d["title"][:120], "lines": len(lines)}, lines, d["links"]


def scan_entry(e):
    res = {"checked": scan.time.strftime("%Y-%m-%d"), "pages": [], "signals": {}, "mentions": {"seasonal": 0, "traveller": 0},
           "engines": [], "chars": 0}
    urls = (e.get("website") or "").split()
    if not urls:
        return res
    rec, lines, links = read(urls[0])
    res["pages"].append(rec)
    res["chars"] += sum(len(l) for l in lines)
    scan.scan_lines(lines, res["signals"], res["mentions"])
    base = rec.get("final") or urls[0]
    cands = []
    for label, u in links:
        if not u.startswith("http") or scan.SKIPLINK.search(u):
            continue
        if scan.ENGINE.search(u) and scan.site_of(u) not in res["engines"]:
            res["engines"].append(scan.site_of(u))
        if scan.site_of(u) != scan.site_of(base) or u.split("#")[0] in (base, urls[0]):
            continue
        score = len(scan.LINKWORD.findall(label + " " + urllib.parse.urlparse(u).path))
        if scan.re.search(r"faq|question|r[èe]gle|rule|polic|politique|tarif|rate|price|prix", label + " " + u, scan.re.I):
            score += 3
        if score:
            cands.append((score, u.split("#")[0]))
    for _, u in sorted(set(cands), key=lambda x: -x[0])[:4]:
        rec, lines, _ = read(u)
        res["pages"].append(rec)
        res["chars"] += sum(len(l) for l in lines)
        scan.scan_lines(lines, res["signals"], res["mentions"])
    res["signals"] = {k: v for k, v in res["signals"].items() if v}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids")
    ap.add_argument("--redo", action="store_true")
    a = ap.parse_args()
    ids = {int(x) for x in a.ids.split(",")} if a.ids else None
    plain = json.load(open(scan.OUT, encoding="utf-8"))
    done = json.load(open(BOUT, encoding="utf-8")) if os.path.exists(BOUT) else {}
    rows = {e["id"]: e for e in scan.worklist()}
    todo = sorted(ids) if ids else sorted(int(k) for k, r in plain.items() if r.get("browser"))
    for i in todo:
        k = str(i)
        if k in done and not a.redo:
            continue
        r = scan_entry(rows[i])
        r.update(id=i, name=rows[i]["name"], state=rows[i]["state"])
        done[k] = r
        tmp = BOUT + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(done, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, BOUT)
        print(k, rows[i]["name"][:40], "chars", r["chars"], sorted(r["signals"]), flush=True)


if __name__ == "__main__":
    main()
