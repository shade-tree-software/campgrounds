import re,html,sys,json,urllib.request,http.cookiejar
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36'
def directory(contract,host):
    op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    g=lambda u: op.open(urllib.request.Request(u,headers={'User-Agent':UA}),timeout=60).read().decode('utf-8','ignore')
    parks={};start=0
    while start<1500:
        u=f'https://{host}/campgroundDirectoryList.do?contractCode={contract}'+(f'&startIdx={start}' if start else '')
        t=g(u); n=len(parks)
        for m in re.finditer(r"parkId=(\d+)'\s+onclick='showProgressBar\(\"contentProgressBar\",\"Retrieving[^>]*>([^<]+)",t):
            parks.setdefault(m.group(1),{'name':html.unescape(m.group(2)).strip()})
        for m in re.finditer(r"&#39;{c}(\d+)&#39;, &#39;(-?[\d.]+):(-?[\d.]+)&#39;".format(c=contract),t):
            if m.group(1) in parks: parks[m.group(1)].update(lat=float(m.group(3)),lng=float(m.group(2)))
        if len(parks)==n: break
        start+=25
    return parks
if __name__=='__main__':
    c,h,out=sys.argv[1:4]
    p=directory(c,h); json.dump(p,open(out,'w'),indent=0); print(len(p))
