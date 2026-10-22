import json,sys,urllib.request,time
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
def g(u):
    return json.loads(urllib.request.urlopen(urllib.request.Request("https://fareharbor.com"+u,headers={"User-Agent":UA}),timeout=40).read())
item=sys.argv[1]
for ym in sys.argv[2:]:
    y,m=ym.split('-')
    d=g(f"/api/v1/companies/riverriders/items/{item}/calendar/{y}/{m}/")
    days=[(x['at'],[a.get('pk') for a in x['availabilities']]) for w in d['calendar']['weeks'] for x in w['days'] if x['month']=='current' and x['availabilities']]
    print(item,ym,len(days),days[:3])
    time.sleep(0.3)
