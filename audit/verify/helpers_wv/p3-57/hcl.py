import re,json,sys
sys.setrecursionlimit(10000)
s=open(sys.argv[1]).read()
d=json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',s,re.S).group(1))
def find_land(o):
    if isinstance(o,dict):
        if isinstance(o.get("sites"),dict) and "edges" in o["sites"]: return o
        for v in o.values():
            r=find_land(v)
            if r: return r
    elif isinstance(o,list):
        for v in o:
            r=find_land(v)
            if r: return r
L=find_land(d)
L=find_land(d)
for k in sys.argv[2:]:
    print(k, json.dumps(L.get(k))[:1800])
