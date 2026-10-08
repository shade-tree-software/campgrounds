# satpx.py LAT LNG ZOOM X Y [X Y ...] -> lat,lng of pixel (X,Y) in the frame satz.py/wb.py
# stitched for LAT LNG at ZOOM (3x3 tiles whose top-left is the tile left of and above the
# point's tile - the crosshair is NOT at the frame centre). Use it to pin a campground on the
# loops seen in a satellite frame, and to measure: prints the distance from the frame's point.
import math, sys

lat, lng, z = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
n = 2 ** z
x = (lng + 180) / 360 * n
y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
ox, oy = int(x) - 1, int(y) - 1
px = sys.argv[4:]
for i in range(0, len(px), 2):
    gx = ox + float(px[i]) / 256
    gy = oy + float(px[i + 1]) / 256
    plng = gx / n * 360 - 180
    plat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * gy / n))))
    dy = (plat - lat) * 111320
    dx = (plng - lng) * 111320 * math.cos(math.radians(lat))
    print('%.5f,%.5f  (%+.0f m E, %+.0f m N of the point)' % (plat, plng, dx, dy))
