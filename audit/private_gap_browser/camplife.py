# camplife.py CAMPGROUND_ID ARRIVE DEPART [N]      (dates YYYY-MM-DD)
# CampLife (camplife.com/<id>/reservation/step1, the engine behind many Ontario "Book now"
# buttons; it loads fine in the driver's browser, plain curl gets 403). Sets the two Duet date
# pickers through the host element's value + a duetChange event (typing into them appends to
# the old value), sets 2 adults, opens the Select Site tab, prints the availability notice
# and count, then prices N sites spread across the available list: each site's description and
# length (/api/campground/<id>/site/<siteId>) and the /api/invoice/estimate answer
# (resSubTotal = pre-tax total for the stay; Taxes listed separately). Messages such as
# "2027 RESERVATIONS OPEN TO BOOK MID NOVEMBER" or "No sites available" print as they come.
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


cg, arrive, depart = sys.argv[1], sys.argv[2], sys.argv[3]
n = int(sys.argv[4]) if len(sys.argv) > 4 else 4

call(cmd='goto', url='https://www.camplife.com/%s/reservation/step1' % cg, wait='9000')
print(call(cmd='eval', js="""(()=>{const ps=[...document.querySelectorAll('duet-date-picker')];
  if(ps.length<2) return 'no date pickers';
  const set=(p,v)=>{p.value=v;p.dispatchEvent(new CustomEvent('duetChange',{bubbles:true,
     detail:{component:'duet-date-picker',value:v,valueAsDate:new Date(v+'T00:00:00')}}));};
  set(ps[0],'%s'); set(ps[1],'%s'); return 'dates '+ps.map(p=>p.value).join(' -> ')})()""" % (arrive, depart)))
call(cmd='wait', wait='3000')
call(cmd='eval', js="""(()=>{const a=document.getElementById('filterNumAdults');if(!a)return;
  const s=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;s.call(a,'2');
  a.dispatchEvent(new Event('input',{bubbles:true}));a.dispatchEvent(new Event('change',{bubbles:true}));})()""")
call(cmd='wait', wait='3000')
call(cmd='click', sel='#siteTabButton', wait='6000')
txt = call(cmd='text', max='20000')
for line in txt.split('\n'):
    line = line.strip()
    if re.search(r'Available$|No sites available|RESERVATIONS OPEN|minimum|Minimum|choose dates|Please choose', line):
        print('  ', line[:300])
search = call(cmd='eval', js="(()=>{const i=[...document.querySelectorAll('input.vs__search')].pop();return i?('#'+i.id):''})()")
if not search or search.startswith('ERROR'):
    sys.exit('no site selector')
call(cmd='click', sel=search, wait='1500')
opts = json.loads(call(cmd='eval', js="JSON.stringify([...document.querySelectorAll('.vs__dropdown-option')].map(e=>e.innerText.replace(/\\s+/g,' ').trim()))"))
avail = [i for i, o in enumerate(opts) if 'Available' in o]
print('  sites in the list: %d, available: %d' % (len(opts), len(avail)))
picks = sorted(set(avail[int(k * (len(avail) - 1) / max(1, n - 1))] for k in range(min(n, len(avail))))) if avail else []
call(cmd='press', key='Escape')
for idx in picks:
    call(cmd='click', sel=search, wait='1200')
    call(cmd='click', sel='.vs__dropdown-option', nth=str(idx), wait='6000')
    net = call(cmd='net', xhr='1', last='10', grep='camplife')
    est = re.findall(r'^\[(\d+)\] 200 POST.*invoice/estimate', net, re.M)
    site = re.findall(r'^\[(\d+)\] 200 GET.*/site/\d+', net, re.M)
    info = call(cmd='eval', js="(()=>{const t=document.body.innerText;const i=t.indexOf('Selected Site');const j=t.indexOf('Amenities',i);return t.slice(i,j>0?j:i+500).replace(/\\s+/g,' ')})()")
    m = re.search(r'Site (\S+) Show available dates (.*?) Site size: (\d+ft) long', info)
    desc = ('site %s | %s | %s' % m.groups()) if m else info[:160]
    quote = ''
    if est:
        try:
            e = json.loads(call(cmd='body', i=est[-1], max='20000'))['invoice']
            quote = 'subtotal C$%s, taxes %s, total %s' % (e.get('resSubTotal'), [x.get('subTotal') for x in e.get('items', [])], e.get('total'))
        except Exception as ex:
            quote = 'estimate unreadable: %s' % ex
    print('  - %s || %s || %s' % (opts[idx], desc, quote or 'no estimate'))
