# campspot_site.py SLUG GUESTS CHECKIN CHECKOUT CATEGORY_ID [CATEGORY_ID ...]
# The price breakdown on a Campspot site-type page (campspot.com/book/<slug>/site/<category id>/
# <in>/<out>/<guests>): "$52.92 x 1 night", each fee line ("Campground Fees $6.00") and "Site
# Total". The availability API's averagePricePerNight, which campspot.py prints, is that Site
# Total divided by the nights, so it folds the park's own fees into the rate (Bear Run PA,
# 2026-10-13: $58.92 = $52.92 site + $6.00 campground fees). Run campspot.py first for the
# category ids (the `id` of each type in its availability answer) and the guests string it
# built. Tax is not on this page. Needs drv_server.py.
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


if __name__ == '__main__':
    slug, guests, ci, co = sys.argv[1:5]
    for cat in sys.argv[5:]:
        head = call(cmd='goto', url='https://www.campspot.com/book/%s/site/%s/%s/%s/%s' % (slug, cat, ci, co, guests),
                    wait='9000')
        L = [l.strip() for l in call(cmd='text', max='60000').split('\n') if l.strip()]
        start = next((i for i, l in enumerate(L) if re.match(r'^\$[\d,.]+ x \d+ nights?$', l)), None)
        end = next((i for i, l in enumerate(L) if l == 'Site Total'), None)
        name = head.split(' | ')[1] if ' | ' in head else head
        if start is None or end is None:
            notes = [l for l in L if re.search(r'(?i)minimum|not available|unavailable|closed', l) and len(l) < 200]
            print('%s %s: no breakdown%s' % (cat, name, ('  | ' + ' / '.join(notes[:3])) if notes else ''))
            continue
        print('%s %s: %s' % (cat, name, ' | '.join(L[start:end + 2])))
