import sys,json,urllib.request,time
base="https://wyordr.usedirect.com/wyomingrdr/rdr/"
def call(p,b=None):
    time.sleep(0.4)
    r=urllib.request.Request(base+p,data=json.dumps(b).encode() if b is not None else None,headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(r,timeout=90).read())
d=sys.argv[1]
g=json.load(open("grid_333_2027-07-12.json"))
out={}
for u in g["Facility"]["Units"].values():
    x=call(f"search/details/{u['UnitId']}/startdate/{d}/nights/1/0/0")
    out[u["Name"]]=x
json.dump(out,open("details.json","w"))
k=list(out)[0]; print(json.dumps(out[k],indent=1)[:5000])
