# pwpdf.py URL OUT : navigate the browser to a document URL and save the download / response body
import sys, os
from playwright.sync_api import sync_playwright
UA="Mozilla/5.0"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None)
    ctx = b.new_context(user_agent=UA, locale='en-US', accept_downloads=True)
    pg = ctx.new_page()
    try:
        with pg.expect_download(timeout=60000) as dl:
            try: pg.goto(sys.argv[1], timeout=60000)
            except Exception as e: print('goto', str(e)[:100])
        dl.value.save_as(sys.argv[2]); print('DOWNLOADED', sys.argv[2])
    except Exception as e:
        print('no download', str(e)[:100]); print(pg.inner_text('body')[:500] if pg.url else '')
    b.close()
