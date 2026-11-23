# frame.py LAT LNG HALF_M OUTPREFIX [W]  -> Esri image + 3DEP DEM in identical 3857 square frame; overlays units + full-pool line
import sys,math,json,urllib.request,io,numpy as np
from PIL import Image,ImageDraw
R=6378137.0
def merc(lat,lng): return (math.radians(lng)*R, math.log(math.tan(math.pi/4+math.radians(lat)/2))*R)
lat,lng,hw,pre=float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3]),sys.argv[4]
W=int(sys.argv[5]) if len(sys.argv)>5 else 1000
k=1/math.cos(math.radians(lat))  # mercator scale
cx,cy=merc(lat,lng); h=hw*k
bb=f"{cx-h},{cy-h},{cx+h},{cy+h}"
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=120).read()
im=Image.open(io.BytesIO(get("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?"
   f"bbox={bb}&bboxSR=3857&imageSR=3857&size={W},{W}&format=jpg&f=image"))).convert('RGB')
j=json.loads(get("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?"
   f"bbox={bb}&bboxSR=3857&imageSR=3857&size={W},{W}&format=jpg&f=json")); print('esri extent',j['extent'],j['width'],j['height'])
dj=json.loads(get("https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage?"
   f"bbox={bb}&bboxSR=3857&imageSR=3857&size={W},{W}&format=tiff&pixelType=F32&interpolation=RSP_BilinearInterpolation&f=json"))
print('dem extent',dj['extent'],dj['width'],dj['height'])
a=np.array(Image.open(io.BytesIO(get(dj['href']))))
np.save(pre+'_dem.npy',a)
fp=a<=1413.51
edge=(fp ^ np.roll(fp,1,0)) | (fp ^ np.roll(fp,1,1))
A=np.array(im); im.save(pre+'_raw.jpg')
A[edge]=[255,0,0]
im2=Image.fromarray(A); d=ImageDraw.Draw(im2)
g=json.load(open('grid_340_2027-07-12.json'))
pts=[(u['ShortName'],u['MapInfo']['Latitude'],u['MapInfo']['Longitude']) for u in g['Facility']['Units'].values()]+[('FAC',42.50308333,-104.96624444)]
for n,pa,pb in pts:
    x,y=merc(pa,pb); px=(x-(cx-h))/(2*h)*W; py=((cy+h)-y)/(2*h)*W
    if 0<=px<W and 0<=py<W:
        d.ellipse((px-4,py-4,px+4,py+4),outline=(255,255,0),width=2); d.text((px+6,py-6),n,fill=(255,255,0))
        print(n,round(float(a[int(py),int(px)]),2))
im2.save(pre+'_ov.jpg'); print('m/px',2*hw/W)
