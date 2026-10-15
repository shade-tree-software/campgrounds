"""Parse the 'Areas' blocks of the saved KDWP park pages: python3 -I areas.py PARKS_DIR -> {park: {area: {kind: n}}}."""
import json, os, re, sys


def parse(text):
    lines = [x.strip() for x in text.splitlines()]
    out, cur = {}, None
    for i, x in enumerate(lines):
        if i + 1 < len(lines) and lines[i + 1].startswith("Camping Available:"):
            cur = x
            out[cur] = {}
            continue
        m = re.match(r"^(Primitive Camping|Water, Sewer, Electric|Water, Electric|Electric|Water|Sewer, Electric|"
                     r"Water, Sewer|Cabins?|Reservable Sites|Camping Available)[^:]*:\s*(\S+)$", x)
        if cur and m:
            v = m.group(2)
            out[cur][m.group(1)] = int(v) if v.isdigit() else v
        elif cur and x in ("Trails", "Amenities", "Related Links"):
            cur = None
    return out


if __name__ == "__main__":
    d = sys.argv[1]
    res = {f[:-4]: parse(open(os.path.join(d, f), encoding="utf-8").read()) for f in sorted(os.listdir(d))}
    print(json.dumps(res, indent=1))
