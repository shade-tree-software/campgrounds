import sys,re
from playwright.sync_api import sync_playwright
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    pg=b.new_page(user_agent=UA,locale='en-US')
    for u in sys.argv[1:]:
        print('=====',u)
        try:
            pg.goto(u,timeout=60000,wait_until='domcontentloaded'); pg.wait_for_timeout(5000)
            pg.get_by_role('tab',name=re.compile('Reviews')).first.click(timeout=8000); pg.wait_for_timeout(3000)
            try:
                pg.get_by_role('button',name=re.compile('Sort')).first.click(timeout=5000); pg.wait_for_timeout(1000)
                pg.get_by_role('menuitemradio',name=re.compile('Newest')).first.click(timeout=5000); pg.wait_for_timeout(3000)
            except Exception as x: print('nosort',str(x)[:80])
            t=pg.evaluate("document.body.innerText")
            for m in re.finditer(r'\n([^\n]{0,40}(?:ago|20\d\d))\n([^\n]{0,220})',t): print(' ',m.group(1),'|',m.group(2)[:200])
        except Exception as x: print('ERR',str(x)[:150])
    b.close()
