#!/usr/bin/env python3
"""Terrain profile between two points (AWS terrain tiles, z15 ~4 m/px):
    python3 -I audit/dam_screen/profile.py lat1,lng1 lat2,lng2 [step_m]
Prints distance and elevation every step (default 15 m) - the berm between a campsite and a
lake shows as a rise above the pool level."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import screen  # noqa: E402

screen.Z = 15
a = tuple(map(float, sys.argv[1].split(",")))
b = tuple(map(float, sys.argv[2].split(",")))
step = float(sys.argv[3]) if len(sys.argv) > 3 else 15
e, (ox, oy), mpp = screen.window([a, b], 60)
L = screen.hav(*a, *b)
n = max(1, int(L // step))
row = []
for i in range(n + 1):
    t = i / n
    la, lo = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
    x, y = screen.to_px(la, lo)
    row.append(f"{L * t:5.0f}m {e[int(y - oy), int(x - ox)]:7.1f}")
print("\n".join(row))
