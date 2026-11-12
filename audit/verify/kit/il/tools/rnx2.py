import sys, os
sys.path.insert(0, os.path.expanduser('~/.cache/ekko-pw'))
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    ex=next((c for c in ('/opt/pw-browsers/chromium-1194/chrome-linux/chrome','/usr/bin/google-chrome') if os.path.exists(c)),None)
    b=p.chromium.launch(executable_path=ex)
    pg=b.new_page(user_agent="Mozilla/5.0")
    for u,name in zip(sys.argv[1::2],sys.argv[2::2]):
        try:
            pg.goto(u,timeout=60000,wait_until='domcontentloaded'); pg.wait_for_timeout(8000)
            try:
                pg.get_by_text('SEARCH',exact=True).first.click(timeout=5000); pg.wait_for_timeout(8000)
            except Exception as x: print('noclick',str(x)[:100])
            t=pg.evaluate("document.body.innerText"); open('dl/'+name+'.txt','w').write(t); print('==',name,len(t))
        except Exception as x: print('ERR',str(x)[:300])
    b.close()
