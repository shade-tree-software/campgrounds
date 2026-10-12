#!/usr/bin/env python3
"""Fetch each target entry's agency page and keep what it says about hookups (2026-10-12).

    python3 -I audit/hookups_recheck/pages.py ID [ID ...] [--url ID=URL ...]

Companion to scan.py for what RIDB doesn't answer: a Forest Service, NPS, BLM, state or county
page. Fetches the entry's first website URL that isn't recreation.gov (or the URL given with
--url), and keeps the Forest Service "Facility and Amenity Information" block when there is one
plus every sentence naming hookups, electricity, water, sewer or utilities. Written per entry to
pages_2026-10-12.json; raw pages are not kept. Nothing here writes campgrounds.json.
"""
import html
import json
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "pages_2026-10-12.json")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
TOPIC = re.compile(r"hook[\s-]*up|electric|amp\b|water|sewer|utilit|dump|full[\s-]*service|"
                   r"generator|power", re.I)


def page_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    raw = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
    raw = re.sub(r"<(script|style|noscript)\b.*?</\1>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<(nav|header|footer)\b.*?</\1>", " ", raw, flags=re.S | re.I)
    t = html.unescape(re.sub(r"<[^>]+>", " | ", raw))
    t = re.sub(r"\s+", " ", t)
    return re.sub(r"(\s*\|\s*)+", " | ", t)


def digest(t):
    out = {}
    i = t.find("Facility and Amenity Information")
    if i >= 0:
        j = t.find("Recreation Opportunities", i)
        out["amenity_block"] = t[i:j if j > i else i + 1500][:1500]
    snips = []
    for part in re.split(r"(?<=[.!?])\s+|\s\|\s", t):
        part = part.strip(" |")
        if 15 < len(part) < 400 and TOPIC.search(part) and part not in snips:
            snips.append(part)
    out["snippets"] = snips[:40]
    return out


def main():
    args = sys.argv[1:]
    urls = {}
    if "--url" in args:
        k = args.index("--url")
        for pair in args[k + 1:]:
            i, u = pair.split("=", 1)
            urls[int(i)] = u
        args = args[:k]
    ids = [int(a) for a in args] + [i for i in urls if str(i) not in args]
    rows = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
    try:
        out = json.load(open(OUT, encoding="utf-8"))
    except FileNotFoundError:
        out = {}
    for i in ids:
        url = urls.get(i)
        if not url:
            cands = [u for u in re.findall(r"https?://\S+", rows[i].get("website") or "")
                     if "recreation.gov" not in u]
            url = cands[0] if cands else None
        rec = {"name": rows[i]["name"], "url": url}
        if url:
            try:
                rec.update(digest(page_text(url)))
            except Exception as e:  # noqa: BLE001 - recorded, not fatal
                rec["error"] = f"{type(e).__name__}: {e}"
        out[str(i)] = rec
        tmp = OUT + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, OUT)
        print(i, rows[i]["name"][:40], url, rec.get("error") or len(rec.get("snippets", [])), flush=True)
        time.sleep(2)


if __name__ == "__main__":
    main()
