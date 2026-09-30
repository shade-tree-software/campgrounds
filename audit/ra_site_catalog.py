'''Summarise a ReserveAmerica park's campsite catalog: site category, access and
"Max Vehicle Length" per site - the size gate for state parks booked on RA.

    python3 audit/ra_site_catalog.py <parkId> [...] [--contract NY] [--host newyorkstateparks.reserveamerica.com]

Writes ra_<parkId>.json in the current directory. Paging needs the cookie that
campgroundDetails.do sets, then campsitePaging.do?startIdx=N (25 per page).
NY's lengths are real per-site data (Fahnestock 15-30, Green Lakes to 60), so a
catalog capped at 20 ft is a genuine size-gate fail, not a default.'''
import argparse
import re,html,sys,urllib.request,http.cookiejar,collections,json,time
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36'
H='https://newyorkstateparks.reserveamerica.com'
def run(park,contract='NY',host=H):
    op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    g=lambda u: op.open(urllib.request.Request(u,headers={'User-Agent':UA}),timeout=60).read().decode('utf-8','ignore')
    g(f'{host}/campgroundDetails.do?contractCode={contract}&parkId={park}')
    ids=[];start=0
    g(f'{host}/campsiteSearch.do?contractCode={contract}&parkId={park}')
    while start<1200:
        t=g(f'{host}/campsitePaging.do?contractCode={contract}&parkId={park}&startIdx={start}')
        new=[i for i in dict.fromkeys(re.findall(r'siteId=(\d+)',t)) if i not in ids]
        if not new: break
        ids+=new; start+=25
    res=[]
    for sid in ids:
        t=g(f'{host}/campsiteDetails.do?siteId={sid}&contractCode={contract}&parkId={park}')
        t=re.sub(r'<(script|style)\b.*?</\1>','',t,flags=re.S)
        x=' '.join(html.unescape(re.sub(r'<[^>]+>',' ',t)).split())
        f=lambda k: (re.search(k+r':\s*([^:]*?)\s+(?=[A-Z][A-Za-z ]{2,30}:)',x) or [None,None])[1]
        loop=re.search(r'Site, Loop:\s*(.*?)\s+(?:Add Site|Type:)',x)
        res.append(dict(site=loop.group(1) if loop else sid,cat=f('Looking For Category'),access=f('Site Access'),
          maxlen=f('Max Vehicle Length'),drive=f('Driveway Length'),elec=f('Electricity Hookup'),water=f('Water Hookup'),sewer=f('Sewer Hookup'),
          wf=f('Waterfront'),type=f('Type')))
    return res
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('parks',nargs='+')
    ap.add_argument('--contract',default='NY'); ap.add_argument('--host',default='newyorkstateparks.reserveamerica.com')
    a=ap.parse_args()
    for p in a.parks:
        r=run(p,a.contract,'https://'+a.host); json.dump(r,open(f'ra_{p}.json','w'),indent=0)
        print('== park',p,len(r),'sites')
        for k in ('cat','access','maxlen','drive','elec','wf'):
            print('  ',k,collections.Counter(s[k] for s in r).most_common(8))
