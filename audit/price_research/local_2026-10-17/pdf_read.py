#!/usr/bin/env python3
"""Read the PDF links the local crawls flagged but never opened (2026-10-17).
    python3 -I pdf_read.py PDFS.json DLDIR OUT.jsonl
PDFS.json = {id: [url, ...]}. Each PDF is downloaded into DLDIR (untrusted data, kept out of the repo),
converted with pdftotext -layout, and every line with a $ figure near camp/RV/site/night/hookup words is kept
with 2 lines of context either side. Resumable; 1 request a second."""
import json, os, re, subprocess, sys, time, hashlib, urllib.request, urllib.parse
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36"
KEY = re.compile(r"(?i)camp|rv\b|r\.v|site|night|daily|per day|hook|electric|trailer|full|primitive|overnight")
pdfs, dl, out = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3]
done = {json.loads(l)["id"] for l in open(out)} if os.path.exists(out) else set()
for i, urls in pdfs.items():
    if int(i) in done:
        continue
    rec = {"id": int(i), "docs": []}
    for u in urls:
        d = {"url": u}
        try:
            time.sleep(1)
            q = urllib.parse.quote(u, safe=":/?&=%#+,;@!$~*'()[]")
            b = urllib.request.urlopen(urllib.request.Request(q, headers={"User-Agent": UA}), timeout=60).read(30_000_000)
            p = os.path.join(dl, hashlib.md5(u.encode()).hexdigest() + ".pdf")
            open(p, "wb").write(b)
            t = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True, timeout=120).stdout
            L = [x.rstrip() for x in t.split("\n")]
            hits = []
            for k, x in enumerate(L):
                if "$" in x and re.search(r"\$\s?\d", x) and KEY.search(" ".join(L[max(0, k - 2):k + 3])):
                    hits.append("\n".join(L[max(0, k - 2):k + 3]))
            d["chars"], d["hits"] = len(t), hits[:40]
            m = re.findall(r"(?i)(?:effective|fy|fiscal year|20\d\d)[^\n]{0,40}", t[:3000])
            d["head"] = t[:400]
        except Exception as e:
            d["error"] = repr(e)[:120]
        rec["docs"].append(d)
    with open(out, "a") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(i, [(len(d.get("hits", [])), d.get("error", "")[:40]) for d in rec["docs"]], flush=True)
