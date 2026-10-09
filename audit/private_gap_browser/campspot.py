# campspot.py SLUG CHECKIN CHECKOUT      (dates YYYY-MM-DD)
# Campspot quote through the ONE persistent driver browser (cs.py / csl.py launch their own
# browser, which breaks the one-browser rule while drv_server.py is up).
#
# Campspot has two front ends and a park may be on either or both:
#  - the booking engine campspot.com/book/<slug> (the operator's "Book now" link; many parks
#    are ONLY here - the marketplace says "Campground not found"), and
#  - the marketplace campspot.com/park/<slug> (white-label sites such as
#    book.summerhillresorts.com are marketplace parks under the same slug; the marketplace may
#    redirect a slug to a "-town-st" form).
# Mode 1 (tried first): open /book/<slug>, read the park's guest categories from the guests
# picker - their ORDER varies by park ([Children, Adults, Pets] at one, [Children 0-5,
# Children 6-17, Adults, Pets] at another), so "guests0,2,0" is 2 adults at one park and 2
# children at the next - build the guests string for 2 adults, load the search list view and
# print the park's own availability API answer (api/gator-core/v2/availability/parks/<id>):
# per site type the average nightly price, the AVAILABLE count, the longest rig allowed and
# any failure reason (minimum nights...). The list page itself can say "no sites available"
# while the API lists free sites - trust the API lines.
# Mode 2 (fallback when /book/<slug> has no guests picker): the marketplace page with
# ?guests=2,0,0, parsed from its text (type, stay total, "Only N left!").
# Prices are before tax unless the park says otherwise. Needs drv_server.py.
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


def book_mode(slug, ci, co):
    print(call(cmd='goto', url='https://www.campspot.com/book/%s' % slug, wait='9000'))
    call(cmd='click', sel='button.guests-picker-input', wait='1500')
    raw = call(cmd='eval', js="JSON.stringify([...document.querySelectorAll('.guests-picker-menu-category-label-name')].map(e=>e.innerText.trim()))")
    try:
        cats = json.loads(raw)
    except Exception:
        cats = []
    if not cats:
        return False
    # one stepper per category, pets included (its label has different markup), so size the
    # guests string by the steppers or a remembered pet count rides along (MAX_PET_RULE errors)
    nstep = int(call(cmd='eval', js="document.querySelectorAll('[class*=app-increase-guest-count-button-]').length") or 0)
    counts = ['0'] * max(len(cats), nstep)
    adult = next((i for i, c in enumerate(cats) if c.lower().startswith('adult')), None)
    if adult is None:
        print('  no Adults category in', cats)
        return True
    counts[adult] = '2'
    guests = 'guests' + ','.join(counts)
    print('  guest categories:', cats, '->', guests)
    call(cmd='goto', url='https://www.campspot.com/book/%s/search/%s/%s/%s/list' % (slug, ci, co, guests), wait='10000')
    net = call(cmd='net', xhr='1', last='40')
    ids = re.findall(r'^\[(\d+)\] 200 GET .*availability/parks/\d+\?checkin=%s&checkout=%s' % (ci, co), net, re.M)
    if not ids:
        print('  no availability response captured')
        return True
    types = json.loads(call(cmd='body', i=ids[-1], max='600000'))
    rows = []
    for t in types:
        sites = t.get('campsites') or []
        free = sum(1 for c in sites if c.get('availability') == 'AVAILABLE')
        fr = sorted({str(x) for c in sites for x in (c.get('failureReasons') or [])}
                    | {str(x) for x in (t.get('failureReasons') or [])})
        lens = [c.get('rvInfo', {}).get('rvLengthMax') for c in sites if c.get('rvInfo')]
        rows.append((t.get('averagePricePerNight') or 0, t.get('campsiteCategoryCode') or '', t.get('name') or '',
                     free, len(sites), max([x for x in lens if x] or [0]), '; '.join(fr)[:160]))
    for p, cat, name, free, n, mx, fr in sorted(rows):
        print('  C$%-8.2f %-6s %-50s free %d/%d%s%s' % (p, cat, name[:50], free, n,
                                                     ' (max %d ft)' % mx if mx else '', ('  | ' + fr) if fr else ''))
    return True


def park_mode(slug, ci, co):
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


if __name__ == '__main__':
    slug, ci, co = sys.argv[1:4]
    if not book_mode(slug, ci, co):
        print('  (no /book/ engine page for this slug - marketplace mode)')
        park_mode(slug, ci, co)
