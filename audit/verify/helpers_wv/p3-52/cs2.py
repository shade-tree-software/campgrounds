# cs2.py SLUG PID GUESTS TID:CHECKIN:CHECKOUT ... -> type quote pricing
import sys, os, json
from playwright.sync_api import sync_playwright
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
JS="""async (u)=>{const r=await fetch(u,{headers:{'x-client-type':'CONSUMER','accept':'application/json'}});return await r.text();}"""
slug,pid,guests=sys.argv[1:4]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None)
    pg=b.new_page(user_agent=UA)
    pg.goto("https://www.campspot.com/book/"+slug,timeout=60000,wait_until='domcontentloaded'); pg.wait_for_timeout(4000)
    for a in sys.argv[4:]:
        tid,ci,co=a.split(':'); pg.wait_for_timeout(3000)
        t=pg.evaluate(JS,f"https://www.campspot.com/api/gator-core/v2/{pid}/campsite-types/availability/{tid}/?checkin={ci}&checkout={co}&guests={guests}&useCustomParkData=true&includeUnavailable=true")
        open(f"cs_q_{tid}_{ci}_{co}.json","w").write(t); print(a,len(t))
    b.close()
