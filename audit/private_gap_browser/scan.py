# scan.py URL [maxlinks]  -> through the ONE persistent browser (drv_server.py):
# open the operator site, list its rate/booking links (and any booking-engine hosts),
# print every line with a $ (plus context) on the home page and on the top rate pages.
import json, os, re, socket, sys
SOCK = os.environ.get('DRV_SOCK') or os.path.expanduser('~/.cache/ekko-drv.sock')


def call(**req):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(240)
    s.connect(SOCK)
    s.sendall((json.dumps(req) + '\n').encode())
    buf = b''
    while not buf.endswith(b'\n'):
        c = s.recv(1 << 20)
        if not c:
            break
        buf += c
    r = json.loads(buf.decode())
    return r['out'] if r['ok'] else 'ERROR: ' + str(r['out'])


url = sys.argv[1]
maxl = int(sys.argv[2]) if len(sys.argv) > 2 else 4
print('GOTO', call(cmd='goto', url=url, wait='6000'))
host = re.sub(r'^https?://(www\.)?', '', call(cmd='url').split(' | ')[0]).split('/')[0]
links = call(cmd='eval', js="JSON.stringify([...document.querySelectorAll('a[href]')].map(a=>[a.href,(a.innerText||a.title||'').trim().replace(/\\s+/g,' ').slice(0,60)]))", max='60000')
try:
    links = json.loads(links)
except Exception:
    links = []
KW = re.compile(r'tarif|rate|prix|price|pricing|co[uû]t|r[ée]serv|book|voyageur|passant|transient|nightly|nuit|s[ée]jour|plan|carte|map|saison', re.I)
ENG = re.compile(r'campspot|resnexus|newbook|firefly|camplife|staylist|reservpro|reservationquebec|reservationcamping|reservationpleinair|campin\.ca|cloudbeds|letscamp|goingtocamp|checkfront|innroad|webrez|rezexpert|roverpass|hipcamp|campable|reservationsoft|rmscloud|bookingcenter|asterix|resaweb|lodgify|beds24|sirvoy|campground', re.I)
seen, cand, eng = set(), [], set()
for h, t in links:
    if not h or h.startswith(('mailto:', 'tel:', 'javascript:')):
        continue
    hb = h.split('#')[0]
    if ENG.search(h):
        eng.add(h[:200])
    if host in h and KW.search(t + ' ' + h.split(host, 1)[-1]) and hb not in seen and not re.search(r'\.(jpg|jpeg|png|webp|gif)$', hb, re.I):
        seen.add(hb)
        cand.append((hb, t))
for e in sorted(eng)[:8]:
    print('ENGINE', e)
for h, t in cand[:25]:
    print('LINK', t, '->', h)
pdfs = sorted({h for h, t in links if h and re.search(r'\.pdf', h, re.I)})
for p in pdfs[:6]:
    print('PDF', p)


def dollars(label):
    txt = call(cmd='text', grep=r'\$|[0-9] ?\$|tarif|prix|minimum|saisonn|voyageur|passant|nuit|night', ctx='1', max='4000')
    print('==', label)
    print(txt[:4000])


dollars(url)
order = sorted(cand, key=lambda x: (0 if re.search(r'tarif|rate|prix|price|pricing|co[uû]t', x[0] + x[1], re.I) else 1 if re.search(r'r[ée]serv|book', x[0] + x[1], re.I) else 2))
done = 0
for h, t in order:
    if done >= maxl:
        break
    if h.rstrip('/') == url.rstrip('/'):
        continue
    r = call(cmd='goto', url=h, wait='5000')
    done += 1
    dollars(h + ' [' + t + ']')
