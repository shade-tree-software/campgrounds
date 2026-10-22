# nbm.py OUT FROM TO : NewBook /online/ form, from/to like "Jun 15 2027", 2 adults, Class C 23 ft
import sys, os
from playwright.sync_api import sync_playwright
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
out,a,d=sys.argv[1:4]; u=sys.argv[4] if len(sys.argv)>4 else 'https://bookingsus.newbook.cloud/online/mountain_lake_campground'
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(user_agent=UA)
    pg.goto(u,timeout=60000,wait_until='domcontentloaded'); pg.wait_for_timeout(4000)
    pg.evaluate(f"""()=>{{for (const [id,v] of [['available_from','{a}'],['available_to','{d}']]){{const f=document.getElementById(id); f.removeAttribute('readonly'); f.value=v;
      try{{jQuery('#'+id).datepicker('setDate', new Date(v));}}catch(e){{}} jQuery(f).trigger('change');}}
      const ad=document.getElementById('newbook_adults'); ad.value='2'; jQuery(ad).trigger('change');}}""")
    pg.wait_for_timeout(1500)
    pg.fill('#equipment_length','23'); pg.keyboard.press('Tab')
    try: pg.select_option('#equipment_type',label='Class C')
    except Exception as e: print('sel',e)
    pg.wait_for_timeout(9000)
    open(out,'w').write(pg.evaluate("document.body.innerText"))
    b.close()
