# usage: csl.py CAMPSPOT_SLUG CHECKIN CHECKOUT - Campspot park page sorted price-ascending (cheapest site first)
import sys,re
from playwright.sync_api import sync_playwright
slug,ci,co=sys.argv[1:4]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=('/usr/bin/google-chrome' if __import__('os').path.exists('/usr/bin/google-chrome') else None), channel=(None if __import__('os').path.exists('/usr/bin/google-chrome') else 'chromium')); pg=b.new_page(ignore_https_errors=True)
    pg.goto(f'https://www.campspot.com/park/{slug}?checkin={ci}&checkout={co}&guests=2,0,0',timeout=60000); pg.wait_for_timeout(9000)
    try:
        pg.locator('select:has(option[value=PRICE_ASCENDING])').first.select_option('PRICE_ASCENDING'); pg.wait_for_timeout(4000)
    except Exception as e: print('nosort',e)
    for _ in range(6): pg.mouse.wheel(0,4000); pg.wait_for_timeout(800)
    t=pg.inner_text('body')
    i=t.find('Available Sites'); print(t[i:i+5000])
    b.close()
