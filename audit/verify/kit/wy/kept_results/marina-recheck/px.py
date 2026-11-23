# px.py CLAT CLNG HALF_M W px,py [px,py ...] -> lat,lng for frame pixels
import sys,math
R=6378137.0
def merc(lat,lng): return (math.radians(lng)*R, math.log(math.tan(math.pi/4+math.radians(lat)/2))*R)
def inv(x,y): return (math.degrees(2*math.atan(math.exp(y/R))-math.pi/2), math.degrees(x/R))
lat,lng,hw,W=map(float,sys.argv[1:5]); k=1/math.cos(math.radians(lat)); cx,cy=merc(lat,lng); h=hw*k
for p in sys.argv[5:]:
    px,py=map(float,p.split(','))
    x=cx-h+px/W*2*h; y=cy+h-py/W*2*h; a,b=inv(x,y); print(p, '%.5f,%.5f'%(a,b))
