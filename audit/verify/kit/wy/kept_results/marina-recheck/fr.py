# fr.py LAT LNG HALF_M OUTPREFIX W THRESH_M[,THRESH2...]  -> Esri image + 3DEP DEM, same 3857 square; contours drawn (red, then cyan, ...)
import sys,math,json,urllib.request,io,numpy as np
from PIL import Image,ImageDraw
R=6378137.0
def merc(lat,lng): return (math.radians(lng)*R, math.log(math.tan(math.pi/4+math.radians(lat)/2))*R)
lat,lng,hw,pre=float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3]),sys.argv[4]
W=int(sys.argv[5]); th=[float(x) for x in sys.argv[6].split(',')] if len(sys.argv)>6 else []
k=1/math.cos(math.radians(lat)); cx,cy=merc(lat,lng); h=hw*k
bb=f"{cx-h},{cy-h},{cx+h},{cy+h}"
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=120).read()
im=Image.open(io.BytesIO(get("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?"
   f"bbox={bb}&bboxSR=3857&imageSR=3857&size={W},{W}&format=jpg&f=image"))).convert('RGB')
im.save(pre+'_raw.jpg')
dj=json.loads(get("https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage?"
   f"bbox={bb}&bboxSR=3857&imageSR=3857&size={W},{W}&format=tiff&pixelType=F32&interpolation=RSP_BilinearInterpolation&f=json"))
a=np.array(Image.open(io.BytesIO(get(dj['href'])))); np.save(pre+'_dem.npy',a)
A=np.array(im); cols=[(255,0,0),(0,255,255),(255,255,0),(255,0,255)]
for i,t in enumerate(th):
    fp=a<=t; e=(fp ^ np.roll(fp,1,0)) | (fp ^ np.roll(fp,1,1)); e[0,:]=e[:,0]=False; A[e]=cols[i%4]
im2=Image.fromarray(A); d=ImageDraw.Draw(im2)
# 50 m scale bar
px50=50/(2*hw)*W; d.line((10,W-15,10+px50,W-15),fill=(255,255,255),width=3); d.text((12,W-30),'50 m',fill=(255,255,255))
im2.save(pre+'_ov.jpg'); print('m/px',2*hw/W,'dem min/max',float(a.min()),float(a.max()))
