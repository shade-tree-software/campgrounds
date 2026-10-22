# cs1.py SLUG CHECKIN CHECKOUT [CHECKIN CHECKOUT...] -> park record + availability list via Campspot API in one browser
import sys, os, json
from playwright.sync_api import sync_playwright
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
slug=sys.argv[1]; dates=sys.argv[2:]
JS="""async (u)=>{const r=await fetch(u,{headers:{'x-client-type':'CONSUMER','accept':'application/json'}});return await r.text();}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None)
    pg=b.new_page(user_agent=UA)
    pg.goto("https://www.campspot.com/book/"+slug,timeout=60000,wait_until='domcontentloaded'); pg.wait_for_timeout(4000)
    park=json.loads(pg.evaluate(JS,"https://www.campspot.com/api/gator-core/v2/parks/slug/"+slug)); park=park.get("park",park)
    json.dump(park,open(f"cs_park_{slug}.json","w"))
    cats=park.get('ageCategories') or []
    g=[]
    for c in cats:
        g.append('2' if 'adult' in (c.get('name') or c.get('displayName') or '').lower() and '2' not in g else '0')
    guests='guests'+','.join(g+['0'])
    print('park',park.get('id'),park.get('name'),'cats',[c.get('name') for c in cats],'guests',guests)
    for i in range(0,len(dates),2):
        pg.wait_for_timeout(3000)
        u=f"https://www.campspot.com/api/gator-core/v2/availability/parks/{park['id']}?checkin={dates[i]}&checkout={dates[i+1]}&guests={guests}&useCustomParkData=true&includeUnavailable=true"
        t=pg.evaluate(JS,u); open(f"cs_av_{slug}_{dates[i]}.json","w").write(t); print(dates[i],len(t))
    b.close()
