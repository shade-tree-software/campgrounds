# campspot.py SLUG CHECKIN CHECKOUT      (dates YYYY-MM-DD)
# Campspot quote through the ONE persistent driver browser (cs.py / csl.py launch their own
# browser, which breaks the one-browser rule while drv_server.py is up). Opens
# campspot.com/park/<slug>?checkin=&checkout=&guests=2,0,0 and prints each site type with its
# stay total and the availability line ("Only 3 left!", "11 Available Locations"), cheapest
# first. White-label booking sites (e.g. book.summerhillresorts.com) are the same park on
# campspot.com under the same slug. Totals are before tax. Needs drv_server.py.
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


slug, ci, co = sys.argv[1:4]
print(call(cmd='goto', url='https://www.campspot.com/park/%s?checkin=%s&checkout=%s&guests=2,0,0' % (slug, ci, co), wait='10000'))
L = [l.strip() for l in call(cmd='text', max='60000').split('\n') if l.strip()]
rows, title = [], None
for i, l in enumerate(L):
    nxt = L[i + 1] if i + 1 < len(L) else ''
    # the type name is the last short line before its description / amenities / price
    if (len(l) < 90 and not l.startswith('$') and not l.startswith('Site amenities')
            and not re.search(r'(?i)available|left!|total$|avg per night|book now|view availability', l)
            and not re.fullmatch(r'(?i)(/?\s*night|per night|starting at|from|\.\d+|rv|tent|lodging)', l)):
        title = l
    m = re.match(r'^\$([\d,]+(?:\.\d+)?) total$', l)
    if m:
        avail = nxt if re.search(r'(?i)available|left', nxt) else ''
        rows.append((float(m.group(1).replace(',', '')), title, avail))
for t in L:
    if re.search(r'(?i)minimum|no sites|not available for|sold out|closed for', t) and len(t) < 300:
        print('  note:', t)
seen = set()
for total, title, avail in sorted(rows, key=lambda r: r[0]):
    if (title, total) in seen:
        continue
    seen.add((title, total))
    print('  C$%.2f  %s  %s' % (total, title, avail))
if not rows:
    print('  no priced site types on the page')
