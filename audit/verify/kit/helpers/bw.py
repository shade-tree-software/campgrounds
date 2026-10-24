# bw.py OUTPREFIX URL [URL...]: one browser, each page's body text + links saved to OUTPREFIX_N.txt
import sys, os
sys.path.insert(0, os.path.expanduser('~/.cache/ekko-pw'))  # local playwright install, if any
from playwright.sync_api import sync_playwright
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
pre=sys.argv[1]
with sync_playwright() as p:
    ex=next((c for c in ('/opt/pw-browsers/chromium-1194/chrome-linux/chrome','/usr/bin/google-chrome') if os.path.exists(c)),None)
    b=p.chromium.launch(executable_path=ex, channel=(None if ex else 'chromium'))
    pg=b.new_page(ignore_https_errors=True,user_agent=UA)
    for i,u in enumerate(sys.argv[2:]):
        try:
            pg.goto(u,timeout=60000,wait_until='domcontentloaded'); pg.wait_for_timeout(int(os.environ.get("BW_WAIT","5000")))
            t=pg.evaluate("document.body.innerText"); L=pg.eval_on_selector_all('a','els=>els.map(e=>e.href)')
        except Exception as x:
            t=f"ERR {x}"; L=[]
        open(f"{pre}_{i}.txt","w").write(u+"\n"+t+"\n--LINKS--\n"+"\n".join(sorted(set(L))))
        print(i,u,len(t))
    b.close()
