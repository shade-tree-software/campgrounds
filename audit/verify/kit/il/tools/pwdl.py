# pwdl.py PAGEURL OUTDIR path1 path2 ... : open PAGEURL in browser, then fetch each same-site path with the page's context; also print buttons/forms
import sys, os
from playwright.sync_api import sync_playwright
UA="Mozilla/5.0"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None)
    ctx = b.new_context(user_agent=UA, locale='en-US')
    pg = ctx.new_page()
    pg.goto(sys.argv[1], timeout=60000, wait_until='domcontentloaded'); pg.wait_for_timeout(8000)
    print('BUTTONS', pg.evaluate("Array.from(document.querySelectorAll('button,input[type=submit],input[type=button],a.button,a.btn,[onclick]')).map(e=>(e.innerText||e.value||'').trim().slice(0,40)+' | '+(e.getAttribute('href')||e.getAttribute('onclick')||'')).join('\\n')"))
    for path in sys.argv[3:]:
        u = path if path.startswith('http') else sys.argv[1].split('/', 3)[0] + '//' + sys.argv[1].split('/', 3)[2] + path
        try:
            r = ctx.request.get(u, timeout=60000)
            fn = os.path.join(sys.argv[2], path.strip('/').replace('/', '_'))
            open(fn, 'wb').write(r.body()); print('GOT', u, r.status, r.headers.get('content-type'), fn)
        except Exception as e: print('ERR', u, str(e)[:120])
    b.close()
