# satpts.py lat lng hw out.jpg ptsfile  (ptsfile lines: name lat lng) -> Esri imagery with labelled dots
import sys, math, urllib.request, io
from PIL import Image, ImageDraw
lat,lng,hw=float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3]); out=sys.argv[4]
dlat=hw/111320; dlng=hw/(111320*math.cos(math.radians(lat)))
u=("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?"
   f"bbox={lng-dlng},{lat-dlat},{lng+dlng},{lat+dlat}&bboxSR=4326&imageSR=3857&size=900,900&format=jpg&f=image")
im=Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=60).read())).convert("RGB")
d=ImageDraw.Draw(im)
def merc(la): return math.log(math.tan(math.pi/4+math.radians(la)/2))
y0,y1=merc(lat+dlat),merc(lat-dlat)
for l in open(sys.argv[5]):
    p=l.split()
    if len(p)<3: continue
    try: a,b=float(p[1]),float(p[2])
    except: continue
    x=(b-(lng-dlng))/(2*dlng)*900; y=(y0-merc(a))/(y0-y1)*900
    d.ellipse((x-3,y-3,x+3,y+3),fill=(255,255,0)); d.text((x+4,y-4),p[0],fill=(255,255,0))
im.save(out); print(out)
