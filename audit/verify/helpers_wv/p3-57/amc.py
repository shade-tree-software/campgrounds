import sys,os
from playwright.sync_api import sync_playwright
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
with sync_playwright() as p:
    ex='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None
    b=p.chromium.launch(executable_path=ex, channel=(None if ex else 'chromium'))
    pg=b.new_page(user_agent=UA)
    for name in sys.argv[1:]:
        pg.goto("https://app.amilia.com/store/en/monongalia-county-parks--recreation/shop/facilitybookings",timeout=60000); pg.wait_for_timeout(6000)
        pg.get_by_text(name,exact=True).first.click(); pg.wait_for_timeout(6000)
        t=pg.evaluate("document.body.innerText")
        open('amc_'+name.replace(' ','_')+'.txt','w').write(pg.url+'\n'+t); print(name,pg.url,len(t))
    b.close()
