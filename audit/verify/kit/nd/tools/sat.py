# sat.py lat lng [half_width_m] out.jpg  -> Esri World_Imagery crop with a red crosshair at centre
import sys, math, urllib.request, io
lat, lng = float(sys.argv[1]), float(sys.argv[2]); hw = float(sys.argv[3]); out = sys.argv[4]
dlat = hw/111320; dlng = hw/(111320*math.cos(math.radians(lat)))
u = ("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?"
     f"bbox={lng-dlng},{lat-dlat},{lng+dlng},{lat+dlat}&bboxSR=4326&imageSR=3857&size=900,900&format=jpg&f=image")
data = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"}), timeout=60).read()
from PIL import Image, ImageDraw
im = Image.open(io.BytesIO(data)).convert("RGB"); d = ImageDraw.Draw(im); c = 450
d.line((c-20,c,c+20,c), fill=(255,0,0), width=2); d.line((c,c-20,c,c+20), fill=(255,0,0), width=2)
im.save(out); print(out, im.size)
