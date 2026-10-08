# satz.py lat lng zoom out.jpg -> 3x3 Esri tiles stitched, crosshair at point
import sys,math,urllib.request,io
from PIL import Image,ImageDraw
lat,lng,z,out=float(sys.argv[1]),float(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
n=2**z; x=(lng+180)/360*n; y=(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n
tx,ty=int(x),int(y); im=Image.new('RGB',(768,768))
for dx in (-1,0,1):
  for dy in (-1,0,1):
    u=f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{ty+dy}/{tx+dx}"
    t=Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=30).read())).convert('RGB')
    im.paste(t,((dx+1)*256,(dy+1)*256))
px=(x-tx+1)*256; py=(y-ty+1)*256; d=ImageDraw.Draw(im)
d.line((px-15,py,px+15,py),fill=(255,0,0),width=2); d.line((px,py-15,px,py+15),fill=(255,0,0),width=2)
im.save(out); print(out)
