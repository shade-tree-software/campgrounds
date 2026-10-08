# wb.py LAT LNG            -> distinct Esri Wayback captures at a point (date, source, release id)
# wb.py LAT LNG REL Z OUT  -> 3x3 stitched tiles from that Wayback release, crosshair at point
#
# The seasonal check for a campground: a PRE-OPENING (Apr-mid May) or POST-CLOSING (after
# Thanksgiving, mid-Oct) capture shows which pads hold winter-stored seasonal trailers. Nearly
# every pad occupied = seasonal park; most pads empty = traveller campground. Summer (leaf-on)
# imagery can't tell the two apart. Caveats learned 2026-10-08:
#  - the live World_Imagery tile at z18/z19 can come from a different source than the
#    metadata names - judge the frame itself (leaf-on canopy = summer);
#  - captures around Canadian Thanksgiving (~Oct 8-14) are still IN season (holiday weekend);
#  - z19 often 404s / "Map data not yet available" outside orthophoto areas - use z17/z18;
#  - Quebec provincial orthophotos (0.15-0.2 m, labelled e.g. "2023_Mauricie_20cm",
#    "geomont orthophoto2020", "Orthoimage 2023") are usually spring captures - ideal.
# Scan cost: ~200 releases, layers 5 then 4 (60/30 cm footprints), 16 threads, ~1 minute.
import sys, json, math, io, os, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
UA = {'User-Agent': 'Mozilla/5.0'}


def get(u, t=30):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t).read()


CFG = os.path.expanduser('~/.cache/ekko-waybackconfig.json')
CFG_URL = 'https://s3-us-west-2.amazonaws.com/config.maptiles.arcgis.com/waybackconfig.json'
# the release list grows ~monthly; refetch when the cached copy is over 30 days old
import time
if not os.path.exists(CFG) or time.time() - os.path.getmtime(CFG) > 30 * 86400:
    os.makedirs(os.path.dirname(CFG), exist_ok=True)
    open(CFG, 'wb').write(get(CFG_URL, 60))
cfg = json.load(open(CFG))
lat, lng = float(sys.argv[1]), float(sys.argv[2])
if len(sys.argv) == 3:
    # newest release first; metadata service names carry the year + release number
    rels = sorted(cfg.items(), key=lambda kv: kv[1]['metadataLayerUrl'], reverse=True)
    import datetime
    from concurrent.futures import ThreadPoolExecutor

    def one(item):
        rid, v = item
        mu = v['metadataLayerUrl']
        q = urllib.parse.urlencode({'geometry': f'{lng},{lat}', 'geometryType': 'esriGeometryPoint',
                                    'inSR': 4326, 'spatialRel': 'esriSpatialRelIntersects',
                                    'outFields': 'SRC_DATE2,SRC_DATE,SRC_DESC,SRC_RES', 'returnGeometry': 'false', 'f': 'json'})
        for layer in (5, 4):
            try:
                r = json.loads(get(f'{mu}/{layer}/query?{q}', 20))
            except Exception:
                continue
            f = r.get('features') or []
            if f:
                d = f[0]['attributes']
                sd = d.get('SRC_DATE2') or d.get('SRC_DATE')
                if isinstance(sd, (int, float)) and sd > 1e10:
                    sd = datetime.datetime.utcfromtimestamp(sd / 1000).strftime('%Y-%m-%d')
                return rid, mu.split('/')[-2], str(sd), d.get('SRC_DESC'), d.get('SRC_RES')
        return None

    with ThreadPoolExecutor(16) as ex:
        res = [r for r in ex.map(one, rels) if r]
    seen = {}
    for rid, svc, sd, desc, resn in res:
        if (sd, desc) not in seen:
            seen[(sd, desc)] = (rid, svc, resn)
    for (sd, desc), (rid, svc, resn) in sorted(seen.items(), reverse=True):
        print(sd, desc, resn, 'release', rid, svc)
else:
    rid, z, out = sys.argv[3], int(sys.argv[4]), sys.argv[5]
    tmpl = cfg[rid]['itemURL']
    from PIL import Image, ImageDraw
    n = 2 ** z
    x = (lng + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    tx, ty = int(x), int(y)
    im = Image.new('RGB', (768, 768))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            u = tmpl.replace('{level}', str(z)).replace('{row}', str(ty + dy)).replace('{col}', str(tx + dx))
            t = Image.open(io.BytesIO(get(u))).convert('RGB')
            im.paste(t, ((dx + 1) * 256, (dy + 1) * 256))
    px, py = (x - tx + 1) * 256, (y - ty + 1) * 256
    dr = ImageDraw.Draw(im)
    dr.line((px - 15, py, px + 15, py), fill=(255, 0, 0), width=2)
    dr.line((px, py - 15, px, py + 15), fill=(255, 0, 0), width=2)
    im.save(out)
    print(out)
