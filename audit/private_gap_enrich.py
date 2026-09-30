#!/usr/bin/env python3
"""Attach the booking/presence facts a private-gap verdict needs to each candidate.

    python3 audit/private_gap_list.py --state MI --json /tmp/mi.json
    python3 audit/private_gap_enrich.py /tmp/mi.json audit/mi_private/candidates.json \
        [--campspot-sitemap park-sitemap.xml]

For every screen-passing and unrated candidate:
  * `cg_url` - the operator URL RV Life embeds in the park page's JSON (the Algolia
    index does not carry it; see feedback_require_live_web_presence);
  * `probe`  - HTTP status, final URL and <title> of that URL, fetched with browser
    headers, so a dead or resold domain shows up before any research;
  * `campspot` - the park's Campspot marketplace slug, when the park sitemap
    (campspot.com/about/documents/park-sitemap.xml - it 403s curl, fetch it with a
    browser) has a slug whose words contain the candidate's name words and end in
    the state code. Campspot quotes a live price per site type for a given date
    (see audit/README private-gap notes), which is the published base rate.

Nothing here is a verdict: a slug match is a lead to confirm, and a live URL still
has to be read for what it is.
"""
import argparse
import concurrent.futures as cf
import html
import json
import re
import subprocess
import sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
STOP = {"campground", "campgrounds", "rv", "park", "resort", "camp", "camping", "the", "and",
        "of", "at", "family", "llc", "inc", "recreation", "&", "a"}


def fetch(url, timeout=20):
    out = subprocess.run(["curl", "-sSL", "-A", UA, "--max-time", str(timeout), "-o", "-",
                          "-w", "\n__META__%{http_code} %{url_effective}", url],
                         capture_output=True, text=True, errors="ignore").stdout
    body, _, meta = out.rpartition("\n__META__")
    code, _, final = meta.partition(" ")
    return body, code, final


def cg_url(rv_url):
    body, code, _ = fetch(rv_url)
    m = re.search(r'"cg_url":"([^"]*)"', body)
    return m.group(1).replace("\\/", "/") if m and m.group(1) else ""


def probe(url):
    if not url:
        return None
    if not re.match(r"https?://", url):
        url = "http://" + url
    body, code, final = fetch(url, 15)
    title = re.search(r"<title[^>]*>([^<]*)", body, re.I)
    return {"code": code, "final": final,
            "title": html.unescape(title.group(1)).strip()[:90] if title else ""}


def words(text):
    return [w for w in re.sub(r"[^a-z0-9]+", " ", (text or "").lower().replace("'", "")).split()
            if w not in STOP]


def campspot_index(path, state):
    slugs = re.findall(r"campspot\.com/park/([a-z0-9-]+)", open(path, encoding="utf-8").read())
    tail = "-" + state.lower()
    return [s for s in slugs if s.endswith(tail)]


def campspot_match(name, slugs):
    need = set(words(name))
    if not need:
        return ""
    best = ""
    for s in slugs:
        have = set(s.split("-"))
        if need <= have and (not best or len(s) < len(best)):
            best = s
    return best


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("listing")
    ap.add_argument("out")
    ap.add_argument("--campspot-sitemap")
    args = ap.parse_args()
    d = json.load(open(args.listing))
    st = d["state"]
    slugs = campspot_index(args.campspot_sitemap, st) if args.campspot_sitemap else []
    rows = [dict(p, bucket="screen") for p in d["passing"]] + \
           [dict(p, bucket="unrated") for p in d["unrated"]]

    def work(p):
        u = cg_url(p["url"])
        return dict(p, cg_url=u, probe=probe(u), campspot=campspot_match(p["name"], slugs))

    with cf.ThreadPoolExecutor(8) as ex:
        out = list(ex.map(work, rows))
    json.dump({"state": st, "candidates": out}, open(args.out, "w"), indent=1, ensure_ascii=False)
    live = sum(1 for p in out if p["probe"] and p["probe"]["code"] == "200")
    print(f"{st}: {len(out)} candidates, {sum(1 for p in out if p['cg_url'])} with an operator URL "
          f"({live} answering 200), {sum(1 for p in out if p['campspot'])} on Campspot")


if __name__ == "__main__":
    sys.exit(main())
