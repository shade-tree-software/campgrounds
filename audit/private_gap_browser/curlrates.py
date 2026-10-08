# usage: curlrates.py LIST (lines: name<TAB>url) - plain urllib: home page + up to 6 rate/booking links, prints $ lines and booking engines
import re,sys,urllib.request,html
from urllib.parse import urljoin, urlparse
ENGINES=r'campspot|resnexus|firefly|newbook|roverpass|staylist|campgroundmaster|parkwith|reserveamerica|camplife|rjourney|checkfront|lodgify|rvparkreservations|campable|letscamp'
def base(u): return '.'.join(urlparse(u).netloc.lower().split('.')[-2:])
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
def get(u):
    try: return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':UA}),timeout=20).read(800000).decode('utf-8','replace')
    except Exception as e: return ''
def text(h):
    h=re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>',' ',h); return [l.strip() for l in html.unescape(re.sub(r'<[^>]+>','\n',h)).split('\n') if l.strip()]
for line in open(sys.argv[1]):
    n,u=line.rstrip('\n').split('\t')
    if not u or 'facebook' in u: print(f"=== {n} | {u} | (no site)"); continue
    h=get(u); pages=[(u,h)]; links=set()
    for m in re.finditer(r'href="([^"#]+)"',h):
        l=m.group(1)
        if re.search(r'rate|price|pricing|reserv|book|rv-?site|rv-park|stay|camp|amenit',l,re.I) and not re.search(r'facebook|instagram|google|twitter|\.(jpg|png|pdf)',l,re.I): 
            L2=urljoin(u,l)
            # only the park's own site or its booking engine: a link to a sister/partner park printed that park's prices under this name
            if base(L2)==base(u) or re.search(ENGINES,urlparse(L2).netloc,re.I): links.add(L2)
    for l in sorted(links)[:6]: pages.append((l,get(l)))
    hits=[];eng=set()
    for pu,ph in pages:
        for e in re.findall(r'(campspot|resnexus|firefly|newbook|roverpass|staylist|campground ?master|parkwith|reserveamerica|camplife|rjourney|checkfront|lodgify|rvparkreservations|campable)',ph,re.I): eng.add(e.lower())
        L=text(ph)
        for i,l in enumerate(L):
            if re.search(r'\$\s?\d|nightly|per night|daily|monthly only|no nightly|long[- ]term only',l,re.I) and len(l)<220: hits.append(' / '.join(L[max(0,i-1):i+2])[:230])
    seen=[];[seen.append(x) for x in hits if x not in seen]
    print(f"=== {n} | {u[:70]} | len={len(h)} engines={sorted(eng)}")
    for x in seen[:10]: print('   ',x)
    sys.stdout.flush()
