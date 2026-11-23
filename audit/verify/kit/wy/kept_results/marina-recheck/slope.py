import sys,math,numpy as np
R=6378137.0; T=1783.84
def merc(lat,lng): return (math.radians(lng)*R, math.log(math.tan(math.pi/4+math.radians(lat)/2))*R)
a=np.load(sys.argv[1]); lat,lng,hw,W=map(float,sys.argv[2:6]); W=int(W)
k=1/math.cos(math.radians(lat)); cx,cy=merc(lat,lng); h=hw*k; mpp=2*hw/W
low=np.argwhere(a<=T)
for arg in sys.argv[6:]:
    n,ll=arg.split(':'); pa,pb=map(float,ll.split(','))
    x,y=merc(pa,pb); px=(x-(cx-h))/(2*h)*W; py=((cy+h)-y)/(2*h)*W
    d=np.hypot(low[:,0]-py,low[:,1]-px); i=d.argmin(); ey,ex=low[i]; L=d[i]*mpp
    N=int(L/0.5)+1; t=np.linspace(0,1,N)
    prof=np.array([a[int(round(py+(ey-py)*s)),int(round(px+(ex-px)*s))] for s in t]); dist=t*L
    w=int(3/(L/(N-1))) if N>1 else 1; g=max((prof[j]-prof[j+w])/(dist[j+w]-dist[j]) for j in range(N-w)) if N>w else 0
    print(f"{n} L={L:.1f} drop={prof[0]-T:.2f} max3m-grade={g*100:.0f}% avg={(prof[0]-T)/L*100:.0f}%  " + ' '.join(f'{dd:.0f}:{p:.1f}' for dd,p in list(zip(dist,prof))[::max(1,N//12)]))
