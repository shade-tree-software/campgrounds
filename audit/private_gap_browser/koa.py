# koa.py SLUG CHECKIN CHECKOUT      (dates MM/DD/YYYY, as koa.com's form takes them)
# KOA's own booking form (koa.com/campgrounds/<slug>/reserve/) through the ONE persistent driver
# browser. A plain fetch of koa.com gets Cloudflare's "Just a moment..." challenge (403); the
# driver's browser loads it without one (Grove City KOA PA, St. Augustine Beach KOA FL,
# 2026-10-13). Step 1 is filled for RV, 2 adults, no pets, a 23-ft motorhome, no slide-outs and
# no KOA Rewards purchase; step 2 lists every site type with its "$66.99 avg/night" price, which
# is the site rate before tax (the optional "KOA Select My Site (+$20.00)" is not in it).
# Prints one line per site type: price | name. KOA_DUMP=PATH also saves step 2's text, which
# carries each type's description - read it for "buddy" sites: some need two reservations
# (Grove City's patio pair), others are priced per site (St. Augustine's "One RV per site").
# Needs drv_server.py.
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


def setter(pairs):
    return ("(()=>{const set=(id,v)=>{const e=document.getElementById(id);if(!e)return;e.value=v;"
            "e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));};"
            + "".join("set('%s','%s');" % kv for kv in pairs) + "return 'ok'})()")


if __name__ == '__main__':
    slug, ci, co = sys.argv[1:4]
    print(call(cmd='goto', url='https://koa.com/campgrounds/%s/reserve/' % slug, wait='10000').split(' | ')[-1])
    call(cmd='select', sel='#Reservation_SiteCategory', label='RV')
    call(cmd='eval', js=setter([('Reservation_CheckInDate', ci), ('Reservation_CheckOutDate', co),
                                ('Reservation_Adults', '2')]))
    call(cmd='eval', js="""(()=>{const p=document.querySelectorAll('input[name="Reservation.Pets"]');if(p[1])p[1].click();return 'ok'})()""")
    call(cmd='select', sel='#Reservation_EquipmentType', label='Motorhome')
    call(cmd='wait', wait='1500')                       # the length field appears once a type is chosen
    call(cmd='eval', js=setter([('Reservation_EquipmentLength', '23')]))
    call(cmd='eval', js="""(()=>{for(const n of ['Reservation.SlideOuts','Reservation.PurchaseVkr']){
        const r=document.querySelectorAll('input[name="'+n+'"]');if(r[1])r[1].click();}return 'ok'})()""")
    call(cmd='click', sel='#nextButton', wait='12000')
    L = [l.strip() for l in call(cmd='text', max='200000').split('\n') if l.strip()]
    if os.environ.get('KOA_DUMP'):
        open(os.environ['KOA_DUMP'], 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('dates', ci, co, '|', ' '.join(l for l in L if re.search(
        r'(?i)returned \d+ out of|no sites|not available|minimum|closed for the season', l))[:300])
    n = 0
    for i, l in enumerate(L):
        if l == 'VIEW DETAILS' and i > 0:
            price = next((x for x in L[i:i + 8] if 'avg/night' in x), '')
            m = re.match(r'\$([\d,.]+) avg/night', price)
            print('%-10s | %s' % (m.group(1) if m else price, L[i - 1]))
            n += 1
    print(n, 'types')
