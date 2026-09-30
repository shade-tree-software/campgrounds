# Private-gap browser helpers

Headless-Chrome helpers used to read booking engines the plain `curl` path can't
(ResNexus, Open Campground, Campspot availability, Newbook, Wix/script sites).
CampLife still 403s.

Setup (per machine; not a repo dependency):

    pip install --target ~/.cache/ekko-pw playwright
    python3 -m playwright install chromium   # or edit executable_path to a local Chrome
    export PYTHONPATH=~/.cache/ekko-pw

The scripts launch `/usr/bin/google-chrome`; change `executable_path` if Chrome
lives elsewhere (or drop it to use Playwright's bundled Chromium).

- `txt.py URL [--browser] [-l] [-nCHARS] [-wMS]` - page as text (+ links)
- `cs.py SLUG CHECKIN CHECKOUT` - Campspot park page with live per-site prices
- `newbook.py URL` - Newbook engine quote for a 23-ft trailer
- `sat.py LAT LNG HALF_WIDTH_M OUT.jpg` - Esri satellite crop with a crosshair
- `geo.py "ADDRESS"` - Census geocoder
- `v.py <state>_private '<json>'` - append a verdict to audit/<state>_private/verdicts.jsonl

