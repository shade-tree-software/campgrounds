# rnx.py URL OUTNAME : render a ResNexus page once and save innerText
import sys, os
sys.path.insert(0, os.path.expanduser('~/.cache/ekko-pw'))
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    ex=next((c for c in ('/opt/pw-browsers/chromium-1194/chrome-linux/chrome','/usr/bin/google-chrome') if os.path.exists(c)),None)
    b=p.chromium.launch(executable_path=ex)
    pg=b.new_page(user_agent="Mozilla/5.0")
    try:
        r=pg.goto(sys.argv[1],timeout=60000,wait_until='domcontentloaded'); print('status',r.status if r else None)
        pg.wait_for_timeout(10000)
        t=pg.evaluate("document.body.innerText"); open('dl/'+sys.argv[2]+'.txt','w').write(t); print(len(t)); print(t[:3000])
    except Exception as x: print('ERR',str(x)[:300])
    b.close()
