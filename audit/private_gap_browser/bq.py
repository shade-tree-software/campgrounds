# one browser, sequential: bq2.py listfile outdir  (lines: key<TAB>url) - page + up to 3 rate/booking links, rendered
import sys,re,os
from playwright.sync_api import sync_playwright
lst=[l.rstrip('\n').split('\t') for l in open(sys.argv[1]) if l.strip()]
out=sys.argv[2]; os.makedirs(out,exist_ok=True)
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
RX=re.compile(r'rate|price|pricing|reserv|book|rv-?site|stay|camp',re.I); BAD=re.compile(r'facebook|instagram|google|twitter|youtube|\.(jpg|png|pdf)|mailto|tel:',re.I)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=('/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None))
    ctx=b.new_context(ignore_https_errors=True,user_agent=UA,locale='en-US')
    for k,u in lst:
        fn=f'{out}/{re.sub(r"[^A-Za-z0-9]+","_",k)}.txt'
        if os.path.exists(fn): continue
        pg=ctx.new_page(); txt=[]
        try:
            pg.goto(u,timeout=45000,wait_until='domcontentloaded'); pg.wait_for_timeout(7000)
            txt.append('### '+pg.url+'\n'+pg.inner_text('body'))
            links=pg.eval_on_selector_all('a[href]','e=>e.map(x=>[x.href,x.innerText])')
            seen=set(); fol=[]
            for h,t in links:
                if (RX.search(h) or RX.search(t or '')) and not BAD.search(h) and h.split('#')[0] not in seen and h.split('#')[0]!=pg.url.split('#')[0]:
                    seen.add(h.split('#')[0]); fol.append(h)
            for h in fol[:3]:
                try:
                    pg.goto(h,timeout=30000,wait_until='domcontentloaded'); pg.wait_for_timeout(5000)
                    txt.append('### '+pg.url+'\n'+pg.inner_text('body'))
                except Exception as e: txt.append('### ERR '+h)
        except Exception as e: txt.append('ERR '+str(e)[:200])
        open(fn,'w').write('\n'.join(txt)); pg.close(); print('done',k,flush=True)
    b.close()
