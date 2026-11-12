# dnr.py spkNNNNN out.json -> MN DNR park feature_detail JSON
import sys,json,urllib.request,re
u="https://maps.dnr.state.mn.us/cgi-bin/compass/feature_detail.cgi?callback=foo&id="+sys.argv[1]
t=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=60).read().decode()
t=t[t.index('(')+1:t.rindex(')')]
d=json.loads(t); json.dump(d,open(sys.argv[2],'w'),indent=1); print(list(d.get('result',d).keys())[:60] if isinstance(d.get('result',d),dict) else type(d))
