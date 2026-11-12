# ovp.py lat lng radius_m -> named tourism=camp_site / caravan_site within radius (overpass.private.coffee)
import sys,json,urllib.request,urllib.parse
lat,lng,r=sys.argv[1:4]
q=f'[out:json][timeout:60];(nwr(around:{r},{lat},{lng})[tourism~"camp_site|caravan_site|camp_pitch"];);out center tags;'
u=__import__("os").environ.get("OVP","https://overpass.private.coffee/api/interpreter")+'?data='+urllib.parse.quote(q)
d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=90))
for e in d['elements']:
    c=e.get('center') or {'lat':e.get('lat'),'lon':e.get('lon')}
    t=e.get('tags',{})
    print(e['type'],e['id'],t.get('tourism'),round(c['lat'],5),round(c['lon'],5),t.get('name',''),t.get('ref',''))
