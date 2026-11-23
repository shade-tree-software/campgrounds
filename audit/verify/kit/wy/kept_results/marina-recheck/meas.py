# meas.py DEMNPY CLAT CLNG HALF_M W  name:lat,lng ...  -> distance to 1783.84 edge, pad elev, profile
import sys,math,numpy as np
R=6378137.0; T=1783.84
def merc(lat,lng): return (math.radians(lng)*R, math.log(math.tan(math.pi/4+math.radians(lat)/2))*R)
a=np.load(sys.argv[1]); lat,lng,hw,W=map(float,sys.argv[2:6]); W=int(W)
k=1/math.cos(math.radians(lat)); cx,cy=merc(lat,lng); h=hw*k; mpp=2*hw/W
low=np.argwhere(a<=T)
for arg in sys.argv[6:]:
    n,ll=arg.split(':'); pa,pb=map(float,ll.split(','))
    x,y=merc(pa,pb); px=(x-(cx-h))/(2*h)*W; py=((cy+h)-y)/(2*h)*W
    d=np.hypot(low[:,0]-py,low[:,1]-px); i=d.argmin(); ey,ex=low[i]
    r=int(round(1.5/mpp)); iy,ix=int(round(py)),int(round(px))
    pe=float(np.median(a[max(iy-r,0):iy+r+1,max(ix-r,0):ix+r+1]))
    prof=[float(a[int(round(py+(ey-py)*t)),int(round(px+(ex-px)*t))]) for t in np.linspace(0,1,21)]
    print(f"{n:4s} {ll} edge {d[i]*mpp:5.1f} m  pad {pe:7.2f} (+{pe-T:4.2f})  profile max {max(prof):.2f} | "+' '.join(f'{p:.1f}' for p in prof[::2]))
