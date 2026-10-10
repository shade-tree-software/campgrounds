#!/usr/bin/env python3
"""Read per-site nightly prices off reserve.alapark.com's campsite calendar
(2026-10-10). Drives the shared one-browser driver (audit/private_gap_browser/
drv_server.py must be running): enter an out-of-state zip, open the two-week
Calendar View, read it, then resubmit the form for a second window.

    python3 audit/price_research/al_state_parks_scrape.py SLUG [SLUG ...]

Writes the calendar text for each window to al_scrape/<slug>_<date>.txt.
"""
import os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
DRV = os.path.join(HERE, "..", "private_gap_browser", "drv.py")
WINDOWS = ["2027-06-13"]   # the first read is whatever "next 2 weeks" is today
ZIP = "19087"              # non-resident: the rate an out-of-state visitor pays
SITEKEY = "6LcnNDYoAAAAAH8a0Q2n-xFMeJS_xTnC1mLlmXD0"


def d(*args):
    return subprocess.run([sys.executable, DRV, *args], capture_output=True, text=True).stdout


def resubmit(date):
    js = ("(()=>{$('#pwFromDate').val('%s');$('#resForm input[name=processing]').val(true);"
          "let st=$('#resForm input[name=stage]').val();grecaptcha.execute('%s',{action:st})"
          ".then(t=>{$('#resForm input[name=token]').val(t);$('#resForm').submit()});return st})()"
          % (date, SITEKEY))
    d("eval", "js=" + js)
    d("wait", "wait=9000")


for slug in sys.argv[1:]:
    d("goto", f"url=https://reserve.alapark.com/{slug}/campsites", "wait=7000")
    if "residentZip" in d("buttons"):
        d("type", "sel=#residentZip", f"value={ZIP}")
        d("press", "key=Enter")
        d("wait", "wait=7000")
    d("click", "text=Calendar View")
    d("wait", "wait=8000")
    out = os.path.join(HERE, "al_scrape")
    open(os.path.join(out, f"{slug}_now.txt"), "w").write(d("text", "max=40000"))
    for w in WINDOWS:
        resubmit(w)
        open(os.path.join(out, f"{slug}_{w}.txt"), "w").write(d("text", "max=40000"))
    print(slug, "done", flush=True)
