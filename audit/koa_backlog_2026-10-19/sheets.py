"""Satellite contact sheets for the KOAs that pass the gate and aren't vetted yet.

Each passing KOA gets a 900x900 Esri crop (sat.py, 500 m half-width, crosshair on RV Life's pin) in sat/;
sheets/sheet_NN.jpg tiles four of them, labelled, for the first read (where is the campground, is any
water near it). A park with water in frame gets a second look at full size before any on-water call.

python3 sheets.py [--slugs a,b,...]"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
SAT = os.path.join(HERE, '..', 'private_gap_browser', 'sat.py')
os.makedirs(os.path.join(HERE, 'sat'), exist_ok=True)
os.makedirs(os.path.join(HERE, 'sheets'), exist_ok=True)
V = [v for v in json.load(open(os.path.join(HERE, 'verdicts.json'))) if v['verdict'].startswith('pass')]
if '--slugs' in sys.argv:
    want = sys.argv[sys.argv.index('--slugs') + 1].split(',')
    V = [v for v in V if v['slug'] in want]
done = set(json.load(open(os.path.join(HERE, 'vetted.json')))) if os.path.exists(os.path.join(HERE, 'vetted.json')) else set()
V = [v for v in V if v['slug'] not in done]
for v in V:
    p = os.path.join(HERE, 'sat', v['slug'] + '.jpg')
    if not os.path.exists(p):
        subprocess.run(['python3', SAT, str(v['lat']), str(v['lng']), '500', p], capture_output=True)
n0 = len([f for f in os.listdir(os.path.join(HERE, 'sheets'))])
for i in range(0, len(V), 4):
    sheet = Image.new('RGB', (1800, 1800), 'white')
    d = ImageDraw.Draw(sheet)
    for j, v in enumerate(V[i:i + 4]):
        p = os.path.join(HERE, 'sat', v['slug'] + '.jpg')
        if not os.path.exists(p):
            continue
        x, y = (j % 2) * 900, (j // 2) * 900
        sheet.paste(Image.open(p), (x, y))
        d.rectangle((x, y, x + 520, y + 26), fill='black')
        d.text((x + 6, y + 6), '%s %s' % (v['slug'], v['state']), fill='yellow')
    out = os.path.join(HERE, 'sheets', 'sheet_%02d.jpg' % (n0 + i // 4))
    sheet.save(out, quality=85)
    print(out, [v['slug'] for v in V[i:i + 4]])
