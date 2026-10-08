# One persistent headless Chromium driven over a Unix socket, so a booking engine
# can be worked step by step (goto, click, fill a date picker, read the quote)
# across many separate shell calls without relaunching the browser.
# Client: drv.py.  One browser only (feedback: one headless browser at a time).
import json, os, socket, sys, time, traceback, re
from playwright.sync_api import sync_playwright

SOCK = os.environ.get('DRV_SOCK') or os.path.expanduser('~/.cache/ekko-drv.sock')
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

NET = []          # recent responses: dicts {i, url, status, ctype, method}
NET_MAX = 400
net_i = [0]
DIALOGS = []


def main():
    os.makedirs(os.path.dirname(SOCK), exist_ok=True)
    if os.path.exists(SOCK):
        os.unlink(SOCK)
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chromium', headless=True,
                              args=['--disable-blink-features=AutomationControlled'])
        ctx = b.new_context(ignore_https_errors=True, user_agent=UA, locale='en-CA',
                            timezone_id='America/Toronto',
                            viewport={'width': 1400, 'height': 1000},
                            extra_http_headers={'Accept-Language': 'en-CA,en;q=0.9,fr-CA;q=0.8,fr;q=0.7'})
        ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        state = {'pages': [], 'cur': None}

        def on_resp(r):
            try:
                ct = r.headers.get('content-type', '')
                rt = r.request.resource_type
                if rt in ('image', 'font', 'stylesheet', 'media'):
                    return
                net_i[0] += 1
                NET.append({'i': net_i[0], 'url': r.url, 'status': r.status, 'ctype': ct[:40],
                            'method': r.request.method, 'rt': rt, 'resp': r})
                if len(NET) > NET_MAX:
                    del NET[0]
            except Exception:
                pass

        def on_dialog(d):
            DIALOGS.append(f'{d.type}: {d.message}')
            try:
                d.accept()
            except Exception:
                pass

        def add_page(pg):
            pg.on('response', on_resp)
            pg.on('dialog', on_dialog)
            state['pages'].append(pg)
            state['cur'] = pg

        ctx.on('page', add_page)
        ctx.new_page()

        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        srv.bind(SOCK)
        srv.listen(1)
        print('ready', SOCK, flush=True)
        while True:
            conn, _ = srv.accept()
            buf = b''
            while not buf.endswith(b'\n'):
                chunk = conn.recv(65536)
                if not chunk:
                    break
                buf += chunk
            try:
                req = json.loads(buf.decode())
            except Exception as e:
                conn.sendall((json.dumps({'ok': False, 'out': f'bad request {e}'}) + '\n').encode())
                conn.close()
                continue
            if req.get('cmd') == 'quit':
                conn.sendall(b'{"ok": true, "out": "bye"}\n')
                conn.close()
                break
            try:
                out = handle(req, ctx, state)
                res = {'ok': True, 'out': out}
            except Exception as e:
                res = {'ok': False, 'out': f'{type(e).__name__}: {str(e)[:600]}'}
            conn.sendall((json.dumps(res, ensure_ascii=False) + '\n').encode())
            conn.close()
        b.close()


def target(req, state):
    pg = state['cur']
    fr = req.get('frame')
    if fr is None or fr == '':
        return pg, pg
    frames = pg.frames
    if str(fr).isdigit():
        return pg, frames[int(fr)]
    for f in frames:
        if fr in (f.url or '') or fr == f.name:
            return pg, f
    raise Exception(f'no frame matching {fr}')


def clean(t):
    return '\n'.join(l.strip() for l in t.splitlines() if l.strip())


def handle(req, ctx, state):
    cmd = req['cmd']
    pg = state['cur']
    wait = int(req.get('wait', 0) or 0)
    mx = int(req.get('max', 6000) or 6000)
    if cmd == 'goto':
        NET.clear()
        pg.goto(req['url'], timeout=int(req.get('timeout', 45000)), wait_until='domcontentloaded')
        pg.wait_for_timeout(wait or 5000)
        return f'{pg.url} | {pg.title()[:100]}'
    if cmd == 'url':
        return f'{pg.url} | {pg.title()[:100]}'
    if cmd == 'wait':
        pg.wait_for_timeout(wait or 2000)
        return 'ok'
    if cmd == 'text':
        _, t = target(req, state)
        sel = req.get('sel') or 'body'
        if req.get('all'):
            txt = '\n---\n'.join(clean(x) for x in t.locator(sel).all_inner_texts())
        else:
            txt = clean(t.locator(sel).first.inner_text(timeout=15000))
        grep = req.get('grep')
        if grep:
            rx = re.compile(grep, re.I)
            L = txt.splitlines()
            ctxn = int(req.get('ctx', 1))
            keep = set()
            for i, l in enumerate(L):
                if rx.search(l):
                    keep.update(range(max(0, i - ctxn), min(len(L), i + ctxn + 1)))
            txt = '\n'.join(L[i] for i in sorted(keep))
        off = int(req.get('off', 0) or 0)
        return txt[off:off + mx]
    if cmd == 'html':
        _, t = target(req, state)
        sel = req.get('sel') or 'body'
        h = t.locator(sel).first.evaluate('e=>e.outerHTML')
        off = int(req.get('off', 0) or 0)
        return h[off:off + mx]
    if cmd == 'links':
        _, t = target(req, state)
        al = t.eval_on_selector_all('a[href]', 'els=>els.map(e=>[e.href,(e.innerText||e.title||"").trim().slice(0,80)])')
        flt = req.get('grep')
        rx = re.compile(flt, re.I) if flt else None
        seen, out = set(), []
        for h, x in al:
            if h in seen:
                continue
            seen.add(h)
            if rx and not (rx.search(h) or rx.search(x)):
                continue
            out.append(f'{x} -> {h}')
        return '\n'.join(out)[:mx]
    if cmd == 'buttons':
        _, t = target(req, state)
        js = '''els=>els.filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0})
                 .map(e=>[e.tagName.toLowerCase(), (e.innerText||e.value||e.getAttribute('aria-label')||e.title||'').trim().replace(/\\s+/g,' ').slice(0,70), e.id||'', (e.className&&e.className.baseVal===undefined?e.className:'').toString().slice(0,60), e.getAttribute('name')||'', e.getAttribute('type')||''])'''
        sel = req.get('sel') or 'button, input, select, [role=button], a.btn, a.button, textarea'
        al = t.eval_on_selector_all(sel, js)
        flt = req.get('grep')
        rx = re.compile(flt, re.I) if flt else None
        out = []
        for i, a in enumerate(al):
            s = ' | '.join(a)
            if rx and not rx.search(s):
                continue
            out.append(f'[{i}] {s}')
        return '\n'.join(out)[:mx]
    if cmd == 'click':
        _, t = target(req, state)
        n = int(req.get('nth', 0) or 0)
        if req.get('text'):
            loc = t.get_by_text(req['text'], exact=bool(req.get('exact')))
        elif req.get('role'):
            loc = t.get_by_role(req['role'], name=req.get('name'), exact=bool(req.get('exact')))
        else:
            loc = t.locator(req['sel'])
        before = len(state['pages'])
        loc.nth(n).click(timeout=int(req.get('timeout', 15000)), force=bool(req.get('force')))
        pg.wait_for_timeout(wait or 3000)
        extra = ''
        if len(state['pages']) > before:
            extra = ' (new page opened, now current)'
        return f'{state["cur"].url} | {state["cur"].title()[:80]}{extra}'
    if cmd == 'xy':
        pg.mouse.click(float(req['x']), float(req['y']))
        pg.wait_for_timeout(wait or 2000)
        return f'{pg.url}'
    if cmd == 'fill':
        _, t = target(req, state)
        t.locator(req['sel']).nth(int(req.get('nth', 0) or 0)).fill(req['value'], timeout=15000)
        pg.wait_for_timeout(wait or 500)
        return 'ok'
    if cmd == 'type':
        _, t = target(req, state)
        loc = t.locator(req['sel']).nth(int(req.get('nth', 0) or 0))
        loc.click(timeout=15000)
        if req.get('clear'):
            pg.keyboard.press('Control+A')
            pg.keyboard.press('Backspace')
        pg.keyboard.type(req['value'], delay=60)
        pg.wait_for_timeout(wait or 800)
        return 'ok'
    if cmd == 'press':
        pg.keyboard.press(req['key'])
        pg.wait_for_timeout(wait or 800)
        return 'ok'
    if cmd == 'select':
        _, t = target(req, state)
        loc = t.locator(req['sel']).nth(int(req.get('nth', 0) or 0))
        if req.get('label'):
            r = loc.select_option(label=req['label'], timeout=15000)
        else:
            r = loc.select_option(req['value'], timeout=15000)
        pg.wait_for_timeout(wait or 1000)
        return str(r)
    if cmd == 'options':
        _, t = target(req, state)
        loc = t.locator(req['sel']).nth(int(req.get('nth', 0) or 0))
        return '\n'.join(loc.evaluate("e=>[...e.options].map(o=>o.value+' = '+o.text)"))[:mx]
    if cmd == 'shot':
        path = req['path']
        if req.get('sel'):
            _, t = target(req, state)
            t.locator(req['sel']).first.screenshot(path=path, timeout=15000)
        else:
            pg.screenshot(path=path, full_page=bool(req.get('full')), timeout=20000)
        return path
    if cmd == 'eval':
        _, t = target(req, state)
        r = t.evaluate(req['js'])
        s = r if isinstance(r, str) else json.dumps(r, ensure_ascii=False)
        return s[:mx]
    if cmd == 'scroll':
        pg.mouse.wheel(0, int(req.get('dy', 800)))
        pg.wait_for_timeout(wait or 1000)
        return 'ok'
    if cmd == 'frames':
        return '\n'.join(f'[{i}] {f.name} | {f.url[:160]}' for i, f in enumerate(pg.frames))
    if cmd == 'pages':
        return '\n'.join(f'[{i}]{"*" if p is state["cur"] else ""} {p.url[:150]}' for i, p in enumerate(state['pages']))
    if cmd == 'switch':
        state['cur'] = state['pages'][int(req['idx'])]
        state['cur'].bring_to_front()
        return state['cur'].url
    if cmd == 'closeothers':
        keep = state['cur']
        for p in list(state['pages']):
            if p is not keep:
                try:
                    p.close()
                except Exception:
                    pass
        state['pages'] = [keep]
        return 'ok'
    if cmd == 'back':
        pg.go_back(timeout=30000)
        pg.wait_for_timeout(wait or 3000)
        return pg.url
    if cmd == 'net':
        flt = req.get('grep')
        rx = re.compile(flt, re.I) if flt else None
        out = []
        for n in NET:
            s = f"[{n['i']}] {n['status']} {n['method']} {n['rt']} {n['ctype']} {n['url'][:200]}"
            if rx and not rx.search(s):
                continue
            if req.get('xhr') and n['rt'] not in ('xhr', 'fetch'):
                continue
            out.append(s)
        return '\n'.join(out[-int(req.get('last', 60)):])[:mx]
    if cmd == 'body':
        i = int(req['i'])
        for n in NET:
            if n['i'] == i:
                t = n['resp'].text()
                off = int(req.get('off', 0) or 0)
                return t[off:off + mx]
        return 'not found'
    if cmd == 'dialogs':
        out = '\n'.join(DIALOGS)
        DIALOGS.clear()
        return out
    if cmd == 'cookies_clear':
        ctx.clear_cookies()
        return 'ok'
    raise Exception(f'unknown cmd {cmd}')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
