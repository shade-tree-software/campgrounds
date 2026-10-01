# usage: gm.py "query" ... -> Google Maps place name, rating, review count (first place panel)
import sys,re
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=('/usr/bin/google-chrome' if __import__('os').path.exists('/usr/bin/google-chrome') else None)); ctx=b.new_context(locale='en-US',user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36")
    pg=ctx.new_page()
    for q in sys.argv[1:]:
        try:
            pg.goto('https://www.google.com/maps/search/'+q.replace(' ','+')+'?hl=en',timeout=60000); pg.wait_for_timeout(7000)
        except Exception as e:
            print(f"{q} | ERR {str(e)[:60]}", flush=True); continue
        h1=pg.eval_on_selector_all('h1','e=>e.map(x=>x.innerText)')
        if not [h for h in h1 if h.strip() and h.strip()!='Results']:
            # a results list: click the first result
            try: pg.locator('a.hfpxzc').first.click(); pg.wait_for_timeout(6000); h1=pg.eval_on_selector_all('h1','e=>e.map(x=>x.innerText)')
            except Exception: pass
        main=pg.locator('div[role="main"]').last
        t=main.inner_text() if main.count() else ''
        m=re.search(r'^(\d\.\d)\s*$\s*^\(([\d,]+)\)',t,re.M)
        addr=re.search(r'^\d+ [^\n]+, [A-Z]{2} [\dA-Z][^\n]*$',t,re.M)
        site=pg.eval_on_selector_all('a[data-item-id="authority"]','e=>e.map(x=>x.href)')
        import re as _r
        cm=_r.search(r'!3d(-?[\d.]+)!4d(-?[\d.]+)',pg.url) or _r.search(r'@(-?[\d.]+),(-?[\d.]+)',pg.url)
        ph=pg.eval_on_selector_all('button[data-item-id^="phone"]','e=>e.map(x=>x.getAttribute("data-item-id"))')
        print(f"{q} | ll={cm.groups() if cm else None} | ph={ph[:1]} | site={site[:1]} | {[h for h in h1 if h.strip()][:1]} | {m.groups() if m else None} | {addr.group(0) if addr else ''}")
    b.close()
