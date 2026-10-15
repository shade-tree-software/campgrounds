"""python3 -I peek.py URL [REGEX] - fetch a page, print text windows around REGEX (default '$')."""
import re, sys
sys.path.insert(0, "/home/andrew/Dev/campgrounds/audit/price_research")
import local_pages as lp
u, t, pdf = lp.get(sys.argv[1]); x = lp.text(t)
rx = sys.argv[2] if len(sys.argv) > 2 else r"\$\s?\d"
last = -999
for m in re.finditer(rx, x, re.I):
    if m.start() - last < 250: continue
    last = m.start(); print("..", x[max(0, m.start() - 150):m.start() + int(__import__("os").environ.get("W", "250"))])
