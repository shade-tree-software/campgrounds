# nbq.py NEWBOOK_URL ARRIVE DEPART      (dates YYYY-MM-DD; URL = the operator's .../index.php)
# Newbook quote through the ONE persistent driver browser (newbook.py starts its own browser).
# Newbook ignores dates in the URL; this sets the form fields (available_from / available_to /
# nights as "Mon D YYYY", equipment unit Feet, length 23, type Travel Trailer) with jQuery
# change triggers, waits for the chart to reload, and prints each site category with its
# "From $X / night" standard rate and the availability line ("ONLY 4 SITES AVAILABLE!").
# "There are currently no Sites available for Online Booking" means none for those dates.
# Prices are before tax unless the park says otherwise. Needs drv_server.py.
import datetime, json, os, re, socket, sys

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


url, a, d = sys.argv[1:4]
fa = datetime.date.fromisoformat(a)
fd = datetime.date.fromisoformat(d)
fmt = lambda x: '%s %d %d' % (x.strftime('%b'), x.day, x.year)
print(call(cmd='goto', url=url, wait='10000'))
js = ('(()=>{const J=window.jQuery;const q=s=>document.querySelector(s);'
      'const f=q("input[name=available_from]"),t=q("input[name=available_to]"),n=q("input[name=nights]"),'
      'l=q("input[name=equipment_length]"),u=q("select[name=equipment_measurement_unit]"),e=q("select[name=equipment_type]");'
      'if(!f)return "no newbook form";f.value="%s";if(t)t.value="%s";if(n)n.value="%d";'
      'if(u){const o=[...u.options].find(o=>/feet/i.test(o.text));if(o)u.value=o.value}'
      'if(l)l.value="23";if(e){const o=[...e.options].find(o=>/travel trailer/i.test(o.text));if(o)e.value=o.value}'
      '[f,t,n,u,l,e].filter(Boolean).forEach(x=>{if(J){J(x).trigger("change")}else{x.dispatchEvent(new Event("change",{bubbles:true}))}});'
      'return [f.value,t&&t.value,n&&n.value].join(" / ")})()') % (fmt(fa), fmt(fd), (fd - fa).days)
print('  set:', call(cmd='eval', js=js))
call(cmd='wait', wait='12000')
L = [x.strip() for x in call(cmd='text', max='60000').split('\n') if x.strip()]
try:
    a0 = max(i for i, x in enumerate(L) if x == 'Show hot deals')
    b0 = next(i for i, x in enumerate(L) if i > a0 and x.startswith('All prices shown'))
except (ValueError, StopIteration):
    a0, b0 = 0, len(L)
skip = re.compile(r'^(Next|Prev|\d+|More details|Show availability|English|Book now|Standard|Weekly)$')
for x in L[a0 + 1:b0]:
    if not skip.match(x):
        print('  ' + x[:160])
