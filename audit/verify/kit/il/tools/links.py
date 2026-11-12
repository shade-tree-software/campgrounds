# links.py URL : render page, print anchor hrefs+text and img srcs
import sys, os
sys.path.insert(0, os.path.expanduser('~/.cache/ekko-pw'))
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    ex=next((c for c in ('/opt/pw-browsers/chromium-1194/chrome-linux/chrome','/usr/bin/google-chrome') if os.path.exists(c)),None)
    b=p.chromium.launch(executable_path=ex)
    pg=b.new_page(user_agent="Mozilla/5.0")
    pg.goto(sys.argv[1],timeout=60000,wait_until='domcontentloaded'); pg.wait_for_timeout(8000)
    for h in pg.evaluate("[...document.querySelectorAll('a')].map(a=>a.innerText.trim().slice(0,40)+' | '+a.href)"):
        if any(k in h.lower() for k in ('map','pdf','jpg','png')): print('A',h)
    for s in pg.evaluate("[...document.querySelectorAll('img')].map(i=>i.src)"): print('IMG',s)
    b.close()
