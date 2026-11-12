import json,sys,math
c=json.load(open('/home/andrew/Dev/campgrounds/campgrounds.json'))
la,lo,r=float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3])
for e in c:
  try: a,b=map(float,e['location'].split(','))
  except: continue
  d=math.hypot((a-la)*111.32,(b-lo)*111.32*math.cos(math.radians(la)))
  if d<r: print(e['id'],e['name'],e['location'],round(d,1),'km',e.get('ownership'),e.get('waterfront'))
