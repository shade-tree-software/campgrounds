import sys, re, html, subprocess
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
url = sys.argv[1]
if '--browser' in sys.argv:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg = b.new_page(ignore_https_errors=True, user_agent=UA)
        pg.goto(url, timeout=60000, wait_until='domcontentloaded'); pg.wait_for_timeout(int(next((a[2:] for a in sys.argv if a.startswith('-w')), 5000)))
        t = pg.inner_text('body'); links = pg.eval_on_selector_all('a', 'els=>els.map(e=>e.href)')
        b.close()
else:
    raw = subprocess.run(["curl","-sSL","-A",UA,"--max-time","30",url],capture_output=True,text=True,errors="ignore").stdout
    links = re.findall(r'href="([^"]+)"', raw)
    raw = re.sub(r'(?is)<(script|style|noscript).*?</\1>', ' ', raw)
    t = html.unescape(re.sub(r'<[^>]+>', '\n', raw))
t = '\n'.join(l.strip() for l in t.splitlines() if l.strip())
n = int(next((a[2:] for a in sys.argv if a.startswith('-n')), 5000))
print(t[:n])
if '-l' in sys.argv:
    print('--LINKS--'); print('\n'.join(sorted(set(l for l in links if not l.startswith('#')))[:150]))
