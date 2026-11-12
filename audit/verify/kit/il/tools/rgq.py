# rgq.py arr dep -> rguest Grand Hinckley RV offer: click the RV SITES offer's Select, print body text
import sys, os
from playwright.sync_api import sync_playwright
UA="Mozilla/5.0"
arr, dep = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None)
    pg = b.new_page(user_agent=UA, locale='en-US', viewport={'width': 1400, 'height': 1000})
    pg.goto(f"https://book.rguest.com/onecart/wbe/offers/1025/Grand-Hinckley-Book?arrivalDate={arr}&departureDate={dep}&adults=2", timeout=60000)
    pg.wait_for_timeout(9000)
    pg.get_by_text('Select', exact=True).nth(6).click(timeout=15000)
    pg.wait_for_timeout(9000)
    print(pg.url); print(pg.inner_text('body'))
    b.close()
