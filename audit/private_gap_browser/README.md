# Private-gap browser helpers

Headless-Chrome helpers used to read booking engines the plain `curl` path can't
(ResNexus, Open Campground, Campspot availability, Newbook, Wix/script sites).
CampLife still 403s.

Setup (per machine; not a repo dependency):

    pip install --target ~/.cache/ekko-pw playwright
    python3 -m playwright install chromium   # or edit executable_path to a local Chrome
    export PYTHONPATH=~/.cache/ekko-pw

The scripts launch `/usr/bin/google-chrome` when it exists, else Playwright's
bundled Chromium.

- `txt.py URL [--browser] [-l] [-nCHARS] [-wMS]` - page as text (+ links)
- `cs.py SLUG CHECKIN CHECKOUT` - Campspot park page with live per-site prices
- `newbook.py URL` - Newbook engine quote for a 23-ft trailer
- `sat.py LAT LNG HALF_WIDTH_M OUT.jpg` - Esri satellite crop with a crosshair
- `geo.py "ADDRESS"` - Census geocoder
- `gm.py "name town ST" ...` - Google Maps place: coords, phone, website, rating + review count
  (the quality signal for parks RV Life doesn't rate; a lodging-style panel hides the count)
- `gsr.py ST "name" ...` - Good Sam ratings by name (Algolia; the fetch cache has no ratings)
- `v.py <state>_private '<json>'` - append a verdict to audit/<state>_private/verdicts.jsonl
- `curlrates.py LIST` - plain-urllib rate crawl over a `name<TAB>url` list (no browser; reads ~2/3 of operator rates; run several splits in parallel)
- `bq.py LIST OUTDIR` - ONE rendered browser, sequential: each `name<TAB>url` page + up to 3 rate/booking links saved as text (~1 min/park; fixed 7 s / 5 s settle waits; reads `body` text only, so iframe widgets come back empty)
- `csl.py SLUG CHECKIN CHECKOUT` - Campspot park page sorted by price ascending (cheapest site type first; watch for tent/dry-camp rows)
- `rates.py URL` - crawl an operator site for rates: follows rate/booking links, prints every `$` line with context and the booking ENGINE / rate-PDF links (run in parallel over a "name url" list)
- `../private_gap_holds.py` - regenerate `audit/private_gap_holds.md`, the checklist of every candidate still on hold

