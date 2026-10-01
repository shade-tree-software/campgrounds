# usage: rates.py URL -> follow an operator site's rate/booking links and print every $ line with
# context, plus the booking ENGINE links (Campspot/ResNexus/Firefly/Staylist/...) and rate PDFs.
# Run many in parallel: xargs -P7 -L1 sh -c 'python3 rates.py "$1" > out/$0.txt' < "name url" list
import sys, re
from playwright.sync_api import sync_playwright
KW=re.compile(r'rate|pric|camp|site|stay|reserv|book|rv|fee',re.I)
ENG=re.compile(r'campspot|resnexus|newbook|firefly|camplife|staylist|campgroundmanager|premiercampground|rezexpert|reserveamerica|hipcamp|roverpass|campsitesoftware|astra|bookingsus|innroad|checkfront|webreserv|campable|eyeonrv|reservationsoft|rmsnorthamerica|ezcampreservations|campgroundbooking|newbook',re.I)
def lines(pg): return [l.strip() for l in pg.inner_text('body').splitlines() if l.strip()]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=('/usr/bin/google-chrome' if __import__('os').path.exists('/usr/bin/google-chrome') else None)); ctx=b.new_context(ignore_https_errors=True,user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36")
    pg=ctx.new_page(); url=sys.argv[1]
    try: pg.goto(url,timeout=45000,wait_until='domcontentloaded'); pg.wait_for_timeout(5000)
    except Exception as e: print('ERR',url,str(e)[:100]); sys.exit()
    host=re.sub(r'^https?://(www\.)?','',pg.url).split('/')[0]
    print('TITLE',pg.title()[:90],'|',pg.url)
    try: al=pg.eval_on_selector_all('a','els=>els.map(e=>[e.href,e.innerText])')
    except Exception: al=[]
    eng=sorted({h for h,t in al if h and ENG.search(h)})
    for e in eng[:5]: print('ENGINE',e[:150])
    links=[]
    for h,t in al:
        if not h or host not in h or h.endswith(('.jpg','.png','.pdf')): continue
        h=h.split('#')[0]
        if KW.search((t or '')+' '+h.split(host)[-1]) and h not in links: links.append(h)
    pdfs=sorted({h for h,t in al if h and h.lower().endswith('.pdf') and re.search(r'rate|price|fee|brochure',h+(t or ''),re.I)})
    for x in pdfs[:3]: print('PDF',x)
    seen=set()
    for u in [pg.url]+links[:15]:
        if u in seen: continue
        seen.add(u)
        try:
            if u!=pg.url: pg.goto(u,timeout=30000,wait_until='domcontentloaded'); pg.wait_for_timeout(3000)
            L=lines(pg)
        except Exception as e: continue
        hits=[i for i,l in enumerate(L) if '$' in l and len(l)<200]
        if hits: print('--',u)
        for i in hits[:20]: print('   ',' | '.join(L[max(0,i-2):i+1])[:230])
    b.close()
