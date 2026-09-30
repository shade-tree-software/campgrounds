import sys, re
from playwright.sync_api import sync_playwright
slug, ci, co = sys.argv[1], sys.argv[2], sys.argv[3]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome')
    pg = b.new_page(ignore_https_errors=True)
    pg.goto(f'https://www.campspot.com/park/{slug}?checkin={ci}&checkout={co}&guests=2,0,0', timeout=60000)
    pg.wait_for_timeout(9000)
    t = pg.inner_text('body')
    print(pg.title())
    print(t[:6000] if '-v' in sys.argv else '\n'.join(l for l in t.splitlines() if l.strip())[:4000])
    b.close()
