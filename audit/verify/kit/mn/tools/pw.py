# pw.py URL [click=TEXT | wait=MS | scroll | more=TEXT]... -> body innerText after the actions (one-shot browser)
import sys, os
from playwright.sync_api import sync_playwright
UA = "Mozilla/5.0"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None)
    pg = b.new_page(user_agent=UA, locale='en-US', viewport={'width': 1400, 'height': 1000})
    pg.goto(sys.argv[1], timeout=60000, wait_until='domcontentloaded'); pg.wait_for_timeout(9000)
    for a in sys.argv[2:]:
        k, _, v = a.partition('=')
        try:
            if k == 'click': pg.get_by_text(v, exact=True).first.click(timeout=15000); pg.wait_for_timeout(5000)
            elif k == 'wait': pg.wait_for_timeout(int(v))
            elif k == 'scroll':
                for i in range(15): pg.mouse.wheel(0, 3000); pg.wait_for_timeout(700)
            elif k == 'js': print('JS>', pg.evaluate(v))
        except Exception as e: print('ERR', a, str(e)[:120])
    print(pg.inner_text('body'))
    b.close()
