import sys,re,os
from playwright.sync_api import sync_playwright
UA="Mozilla/5.0"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None)
    pg=b.new_page(user_agent=UA,locale='en-US')
    for q in sys.argv[1:]:
        u='https://www.google.com/maps/search/'+q.replace(' ','+')+'?hl=en'
        print('=====',q)
        try:
            pg.goto(u,timeout=60000,wait_until='domcontentloaded'); pg.wait_for_timeout(7000)
            if pg.locator('a.hfpxzc').count(): pg.goto(pg.locator('a.hfpxzc').first.get_attribute('href'),timeout=60000); pg.wait_for_timeout(7000)
            pg.get_by_role('tab',name=re.compile('Reviews')).first.click(timeout=8000); pg.wait_for_timeout(3000)
            try:
                pg.get_by_role('button',name=re.compile('Sort')).first.click(timeout=5000); pg.wait_for_timeout(1000)
                pg.get_by_role('menuitemradio',name=re.compile('Newest')).first.click(timeout=5000); pg.wait_for_timeout(3000)
            except Exception as x: print('nosort',str(x)[:80])
            for i in range(6):
                pg.mouse.move(300,600); pg.mouse.wheel(0,3000); pg.wait_for_timeout(1200)
            t=pg.evaluate("document.body.innerText")
            open("dl/rev_"+q[:12].replace(" ","_")+".txt","w").write(t)
        except Exception as x: print('ERR',str(x)[:150])
    b.close()
