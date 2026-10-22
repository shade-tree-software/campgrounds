# lcnet.py URL OUT: load page, save JSON API responses (letscamp) + body text
import sys, os, json
from playwright.sync_api import sync_playwright
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
out=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None)
    pg=b.new_page(user_agent=UA)
    def on(r):
        if '/api/' in r.url or 'graphql' in r.url:
            try: out.append({'url':r.url,'post':r.request.post_data,'body':r.text()[:20000]})
            except Exception: pass
    pg.on('response',on)
    pg.goto(sys.argv[1],timeout=60000,wait_until='domcontentloaded'); pg.wait_for_timeout(12000)
    t=pg.evaluate("document.body.innerText")
    json.dump({'text':t,'net':out},open(sys.argv[2],'w'))
    b.close()
print(len(out))
