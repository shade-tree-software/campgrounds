# csmap.py URL outprefix -> saves park-maps svg, availability json, a screenshot
import sys, os
from playwright.sync_api import sync_playwright
url, pre = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None)
    pg = b.new_page(user_agent="Mozilla/5.0", locale='en-US', viewport={'width': 1400, 'height': 1100})
    def onr(r):
        try:
            u = r.url
            if 'park-maps.campspot.com' in u:
                open(pre + '_map.svg', 'w').write(r.text()); print('SVG', r.status, u[:120], flush=True)
            elif 'availability/parks' in u:
                open(pre + '_avail.json', 'w').write(r.text()); print('AV', r.status, u[:160], flush=True)
            elif r.status >= 400 and 'campspot' in u:
                print('ERR', r.status, u[:120], flush=True)
        except Exception as e:
            pass
    pg.on('response', onr)
    resp = pg.goto(url, timeout=60000, wait_until='domcontentloaded'); print('MAIN', resp.status if resp else None)
    pg.wait_for_timeout(12000)
    pg.screenshot(path=pre + '_shot.png')
    open(pre + '_body.txt', 'w').write(pg.inner_text('body'))
    b.close()
