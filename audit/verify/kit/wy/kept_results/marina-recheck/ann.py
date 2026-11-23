# ann.py PREFIX CLAT CLNG HALF_M W OUT x0,y0,x1,y1 SCALE name:lat,lng ...  -> overlay image with pad marks + line to nearest 1783.84 edge
import sys,math,numpy as np
from PIL import Image,ImageDraw
R=6378137.0; T=1783.84
def merc(lat,lng): return (math.radians(lng)*R, math.log(math.tan(math.pi/4+math.radians(lat)/2))*R)
pre=sys.argv[1]; lat,lng,hw,W=map(float,sys.argv[2:6]); W=int(W); out=sys.argv[6]; box=tuple(map(int,sys.argv[7].split(','))); sc=float(sys.argv[8])
a=np.load(pre+'_dem.npy'); im=Image.open(pre+'_ov.jpg').convert('RGB')
k=1/math.cos(math.radians(lat)); cx,cy=merc(lat,lng); h=hw*k; mpp=2*hw/W
low=np.argwhere(a<=T); d=ImageDraw.Draw(im)
for arg in sys.argv[9:]:
    n,ll=arg.split(':'); pa,pb=map(float,ll.split(','))
    x,y=merc(pa,pb); px=(x-(cx-h))/(2*h)*W; py=((cy+h)-y)/(2*h)*W
    dd=np.hypot(low[:,0]-py,low[:,1]-px); i=dd.argmin(); ey,ex=low[i]
    d.line((px,py,ex,ey),fill=(255,255,0),width=1); d.ellipse((px-3,py-3,px+3,py+3),outline=(0,255,255)); d.text((px-14,py-14),n,fill=(0,255,255))
im=im.crop(box); im=im.resize((int(im.width*sc),int(im.height*sc))); im.save(out)
