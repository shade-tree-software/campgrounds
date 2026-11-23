# median over 5 parallel transects (offsets -2..2 m): max 3-m grade, and steep-part height (sum of drops where 2-m grade > 33%)
import sys,math,numpy as np
def map_coordinates(a,yx,order=1):
    yy,xx=np.asarray(yx[0],float),np.asarray(yx[1],float)
    y0=np.clip(np.floor(yy).astype(int),0,a.shape[0]-2); x0=np.clip(np.floor(xx).astype(int),0,a.shape[1]-2)
    fy=yy-y0; fx=xx-x0
    return a[y0,x0]*(1-fy)*(1-fx)+a[y0+1,x0]*fy*(1-fx)+a[y0,x0+1]*(1-fy)*fx+a[y0+1,x0+1]*fy*fx
R=6378137.0; T=1783.84
def merc(lat,lng): return (math.radians(lng)*R, math.log(math.tan(math.pi/4+math.radians(lat)/2))*R)
a=np.load(sys.argv[1]); lat,lng,hw,W=map(float,sys.argv[2:6]); W=int(W)
k=1/math.cos(math.radians(lat)); cx,cy=merc(lat,lng); h=hw*k; mpp=2*hw/W
low=np.argwhere(a<=T)
for arg in sys.argv[6:]:
    n,ll=arg.split(':'); pa,pb=map(float,ll.split(','))
    x,y=merc(pa,pb); px=(x-(cx-h))/(2*h)*W; py=((cy+h)-y)/(2*h)*W
    dd=np.hypot(low[:,0]-py,low[:,1]-px); i=dd.argmin(); ey,ex=low[i]; L=dd[i]*mpp
    uy,ux=(ey-py)/dd[i],(ex-px)/dd[i]; ny,nx=-ux,uy
    gs=[];hs=[]
    for off in (-2,-1,0,1,2):
        o=off/mpp; s=np.arange(0,dd[i]+1e-9,0.25/mpp)
        prof=map_coordinates(a,[py+ny*o+uy*s, px+nx*o+ux*s],order=1); dist=s*mpp
        w=int(round(3/0.25)); g=max((prof[j]-prof[j+w])/3 for j in range(len(prof)-w)) if len(prof)>w else 0
        w2=8; st=sum(max(prof[j]-prof[j+w2],0) for j in range(0,len(prof)-w2,w2) if (prof[j]-prof[j+w2])/2>0.33)
        gs.append(g); hs.append(st)
    print(f"{n:4s} L={L:5.1f} pad+{a[int(round(py)),int(round(px))]-T:4.2f} max3m grade median {np.median(gs)*100:3.0f}% (range {min(gs)*100:.0f}-{max(gs)*100:.0f})  steep(>33%) height median {np.median(hs):.2f} m")
