# ov.py lat lng hw out.jpg ptsfile... -> sat image with unit points labelled
import sys, math, urllib.request, io
from PIL import Image, ImageDraw
lat, lng, hw, out = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
dlat = hw/111320; dlng = hw/(111320*math.cos(math.radians(lat)))
u = ("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?"
     f"bbox={lng-dlng},{lat-dlat},{lng+dlng},{lat+dlat}&bboxSR=4326&imageSR=3857&size=900,900&format=jpg&f=image")
im = Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"}), timeout=60).read())).convert("RGB")
d = ImageDraw.Draw(im)
def my(la): return math.log(math.tan(math.pi/4+math.radians(la)/2))
y0,y1=my(lat-dlat),my(lat+dlat)
cols=[(255,255,0),(0,255,255),(255,0,255),(255,128,0),(128,255,0)]
for i,f in enumerate(sys.argv[5:]):
    for line in open(f):
        p=line.split()
        if len(p)<3 or p[1] in ("0.0","None"): continue
        la,lo=float(p[1]),float(p[2])
        x=(lo-(lng-dlng))/(2*dlng)*900; y=(y1-my(la))/(y1-y0)*900
        if 0<=x<900 and 0<=y<900:
            d.ellipse((x-3,y-3,x+3,y+3),fill=cols[i%5]); d.text((x+4,y-6),p[0].lstrip("0") or "0",fill=cols[i%5])
im.save(out); print(out)
