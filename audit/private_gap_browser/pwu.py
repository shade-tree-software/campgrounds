# pwu.py URL ARRIVE DEPART - parkwith.us camp page: pick the two days on its react-day-picker
# (td[data-day=YYYY-MM-DD]; steps "Next" until the month shows), fills the prerequisites
# (23-ft rig, 2 adults) and tallies the site list's "$X / night" prices by site row.
# Needs drv_server.py (one browser).
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


url, arrive, depart = sys.argv[1:4]
print(call(cmd='goto', url=url, wait='8000').split('\n')[0])
for day in (arrive, depart):
    for _ in range(14):
        hit = call(cmd='eval', js="(()=>{const b=document.querySelector('td[data-day=\"%s\"] button');if(!b)return 'no';b.click();return 'ok'})()" % day)
        if 'ok' in hit:
            break
        call(cmd='eval', js="(()=>{const n=[...document.querySelectorAll('button')].find(b=>/Next/i.test(b.getAttribute('aria-label')||b.innerText));if(n)n.click()})()")
        call(cmd='wait', wait='800')
    print(' ', day, hit)
    call(cmd='wait', wait='2500')
call(cmd='wait', wait='3000')
# "Next" -> prerequisites (rig length 23 ft, 2 adults) -> "Next" -> the site list with "$X / night".
call(cmd='click', text='Next', exact='1', wait='7000')
if 'prerequisites' in call(cmd='url'):
    call(cmd='type', sel='input[type=number]', value='23', clear='1')
    call(cmd='click', text='Next', exact='1', wait='8000')
print(' ', call(cmd='url').split(' | ')[0])
txt = call(cmd='eval', js="document.body.innerText.replace(/[ \\t]+/g,' ')")
flat = re.sub(r'\s+', ' ', txt)
rows = re.findall(r'Site (\S+) ([^$]*?)\$([\d.,]+) / night', flat)
if rows:
    tally = {}
    for site, desc, price in rows:
        k = (price, re.sub(r'\d+', '#', site), desc.strip()[:40])
        tally[k] = tally.get(k, 0) + 1
    for (price, site, desc), n in sorted(tally.items()):
        print('  $%s x%d  %s  %s' % (price, n, site, desc))
else:
    for m in re.finditer(r'\$\s?\d[\d,.]*', flat):
        print('  ..', flat[max(0, m.start() - 170):m.end() + 70])
    print('  no "$ / night" rows;', flat[:600])
