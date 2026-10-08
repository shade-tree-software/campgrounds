# rpro.py URL [YYYY-MM-DD] [NIGHTS]
# RéservPro (reservationquebec.net or embedded on an operator site; "Propulsé par RéservPro").
# URL is either a camp listing page (reservationquebec.net/reservation-en-ligne/camping/<slug>.html,
# or an operator page carrying a.rp-service-action links such as .../reservation/?service=<slug>)
# or one service page. For every service type it prints the nights options the engine offers
# and the JSON of its availability call (action=check-disponibilite_service):
#   Prix = nightly price for the stay length, Frais = booking fee, NbrDispo = sites free
#   (= the traveller inventory for that type), Erreur/Message = e.g.
#   "Erreur de date. Le nombre de nuits minimum est de 2 nuits." or
#   "La réservation en ligne n'est pas encore activé pour 2027" (season not open).
# Minimums are per service type AND date (Camping Larochelle: 2-service needs 2 nights,
# 3-service sells one). The engine defaults to today / the next open date when no date is
# given. Needs drv_server.py (one browser).
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
date = sys.argv[2] if len(sys.argv) > 2 else ''
nights = sys.argv[3] if len(sys.argv) > 3 else '1'

SERVICE_PAGE = r'service=|/reservation-en-ligne/[^/]+/[^/.]+/?$'
if re.search(SERVICE_PAGE, url):
    services = [url]          # one service page: quote just that type
else:
    call(cmd='goto', url=url, wait='8000')
    svc = call(cmd='eval', js="JSON.stringify([...new Set([...document.querySelectorAll('a.rp-service-action')].map(a=>a.href))])")
    try:
        services = json.loads(svc)
    except Exception:
        services = []
    if not services:
        services = [url]
for s in services:
    if not re.search(SERVICE_PAGE, s) and s != url:
        continue
    call(cmd='goto', url=s, wait='8000')
    if date:
        call(cmd='eval', js="(()=>{const d=document.getElementById('dtdebut')||document.getElementById('dt-arrivee');"
                            "if(!d)return 'no date input';d.value='%s';d.dispatchEvent(new Event('input',{bubbles:true}));"
                            "d.dispatchEvent(new Event('change',{bubbles:true}));if(window.jQuery){jQuery(d).trigger('change');}"
                            "const n=document.querySelector('select[name=duree]')||document.getElementById('nb-nuits');"
                            "if(n&&[...n.options].some(o=>o.value=='%s')){n.value='%s';n.dispatchEvent(new Event('change',{bubbles:true}));"
                            "if(window.jQuery){jQuery(n).trigger('change');}}return d.value})()" % (date, nights, nights))
        call(cmd='wait', wait='6000')
    opts = call(cmd='eval', js="(()=>{const n=document.querySelector('select[name=duree]')||document.getElementById('nb-nuits');"
                              "return n?[...n.options].slice(0,3).map(o=>o.text).join(', '):'-'})()")
    ids = re.findall(r'^\[(\d+)\].*application/json', call(cmd='net', xhr='1', grep='json', last='12'), re.M)
    body = ''
    for i in reversed(ids):
        b = call(cmd='body', i=i, max='400000')
        if '"services"' in b:
            body = b
            break
    print('==', s)
    print('   nights offered:', opts)
    if not body:
        print('   availability: (no check-disponibilite_service response captured)')
        continue
    try:
        d = json.loads(body)
    except Exception:
        print('   availability (raw):', body[:600])
        continue
    print('   availability %s -> %s' % (d.get('debut'), d.get('fin')))
    for k in ('Erreur', 'Message', 'erreur', 'message'):
        if d.get(k):
            print('   %s: %s' % (k, str(d[k])[:300]))
    for v in d.get('services', []):
        msg = v.get('Erreur') or v.get('Message') or ''
        print('   - %s | Prix %s | Frais %s | NbrDispo %s | %s %s' % (
            v.get('Titre'), v.get('Prix'), v.get('Frais'), v.get('NbrDispo'),
            v.get('BadgeLabel') or v.get('Statut') or '', str(msg)[:200]))
