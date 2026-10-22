# nb.py OUT URL DATE(Tue 10 Nov 2026) NIGHTS : fill NewBook online form (equipment 23 ft, no slides) and dump text
import sys, os
from playwright.sync_api import sync_playwright
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
out,u,d,n=sys.argv[1:5]
with sync_playwright() as p:
    ex='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None
    b=p.chromium.launch(); pg=b.new_page(user_agent=UA)
    pg.goto(u,timeout=60000,wait_until='domcontentloaded'); pg.wait_for_timeout(4000)
    pg.evaluate(f"""()=>{{const f=document.getElementById('available_from'); f.removeAttribute('readonly'); f.value='{d}';
      if(window.jQuery){{try{{jQuery('#available_from').datepicker('setDate', new Date('{d}'));}}catch(e){{}}}}
      const nn=document.getElementById('nights'); if(nn){{nn.value='{n}'; nn.dispatchEvent(new Event('change',{{bubbles:true}}));}}
      f.dispatchEvent(new Event('change',{{bubbles:true}}));}}""")
    pg.fill('#equipment_length','23'); pg.select_option('#equipment_type','2')
    pg.dispatch_event('#equipment_length','change'); pg.dispatch_event('#equipment_type','change')
    pg.wait_for_timeout(9000)
    open(out,'w').write(pg.evaluate("document.body.innerText"))
    b.close()
