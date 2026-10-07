import sys, re
from playwright.sync_api import sync_playwright
url = sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=('/usr/bin/google-chrome' if __import__('os').path.exists('/usr/bin/google-chrome') else None), channel=(None if __import__('os').path.exists('/usr/bin/google-chrome') else 'chromium')); pg=b.new_page()
    pg.goto(url,wait_until='domcontentloaded',timeout=60000); pg.wait_for_timeout(5000)
    opts = pg.eval_on_selector_all('#equipment_type option','els=>els.map(e=>[e.value,e.textContent])')
    pick = next((o for o in opts if re.search(r'trailer.*30|travel trailer', o[1], re.I)), None) or next((o for o in opts if re.search(r'motorhome|class c|rv', o[1], re.I)), opts[-1])
    pg.fill('#equipment_length','23'); pg.select_option('#equipment_type', pick[0])
    pg.dispatch_event('#equipment_type','change'); pg.dispatch_event('#equipment_length','change')
    pg.wait_for_timeout(8000)
    t = pg.inner_text('body')
    i = t.find('All prices'); 
    print(pick); print('\n'.join(l for l in t.splitlines() if l.strip())[:int(sys.argv[2]) if len(sys.argv)>2 else 5000])
    b.close()
