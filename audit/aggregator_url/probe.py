import json,subprocess,re,concurrent.futures as cf
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
def go(r):
    u=r['website'][0]
    out=subprocess.run(['curl','-sSL','-A',UA,'--max-time','25','-o','-','-w','\n__M__%{http_code} %{url_effective}',u],capture_output=True,text=True,errors='ignore').stdout
    body,_,m=out.rpartition('\n__M__'); code,_,fin=m.partition(' ')
    t=re.search(r'<title>(.*?)</title>',body,re.S)
    return dict(id=r['id'],url=u,code=code,final=fin,title=(t.group(1).strip()[:90] if t else ''),
        instant=body.count('Instant Book'),booknow=len(re.findall(r'Book Now|Check Availability|Reserve Now',body)),
        updated=(re.search(r'Last Updated: ([\d/]+)',body) or [None,None])[1],
        closed=bool(re.search(r'permanently closed|is closed',body,re.I)))
rows=json.load(open('candidates.json'))
with cf.ThreadPoolExecutor(8) as ex: res=list(ex.map(go,rows))
json.dump(res,open('probe.json','w'),indent=1)
import collections
print(collections.Counter((('rp' if 'roverpass' in x['url'] else 'other'),x['code'],x['instant']>0) for x in res))
