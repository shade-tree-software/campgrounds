import json,sys,urllib.request,urllib.parse,time
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
for c in sys.argv[1:]:
    q=f"[out:json][timeout:60];(way(around:120,{c})[highway];relation(around:50,{c})[boundary=protected_area];way(around:50,{c})[boundary=protected_area];nwr(around:300,{c})[tourism=camp_site];);out tags center;"
    for ep in ['https://overpass.kumi.systems/api/interpreter','https://overpass-api.de/api/interpreter']:
        try:
            r=urllib.request.urlopen(urllib.request.Request(ep,data=urllib.parse.urlencode({'data':q}).encode(),headers={'User-Agent':UA}),timeout=90)
            d=json.load(r); break
        except Exception as e: print('err',ep,e); d=None
    print('==',c)
    for e in (d or {}).get('elements',[]):
        t=e['tags']; print(' ',e['type'],e.get('center'),{k:t[k] for k in t if k in ('highway','name','ref','surface','tracktype','boundary','protect_class','tourism','access','4wd_only','smoothness','operator','motor_vehicle')})
    time.sleep(2)
