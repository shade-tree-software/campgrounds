# netcap.py URL outprefix [wait_ms] -> body text + JSON XHR responses saved
import sys, os, json
from playwright.sync_api import sync_playwright
url, pre = sys.argv[1], sys.argv[2]; w = int(sys.argv[3]) if len(sys.argv) > 3 else 12000
n = [0]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None)
    pg = b.new_page(user_agent="Mozilla/5.0", locale='en-US', viewport={'width': 1400, 'height': 1000})
    def onr(r):
        try:
            ct = r.headers.get('content-type', '')
            if 'json' in ct:
                n[0] += 1
                fn = f"{pre}_{n[0]}.json"
                open(fn, 'w').write(r.text())
                print('XHR', r.status, r.url[:200], '->', fn, flush=True)
        except Exception as e:
            pass
    pg.on('response', onr)
    pg.goto(url, timeout=60000, wait_until='domcontentloaded'); pg.wait_for_timeout(w)
    open(pre + '_body.txt', 'w').write(pg.inner_text('body'))
    b.close()
