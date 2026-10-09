# candidates.py OUT.json: entries whose note may say the CAMPING is free and that record no fees yet.
# Deliberately over-inclusive; every hit is read by hand before anything is written (2026-10-09).
import json, re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rows = json.load(open(os.path.join(ROOT, 'campgrounds.json')))
AMEN = (r'(?:wi-?fi|internet|showers?|hot showers?|dump|sani|water|firewood|museum|admission|parking|ferry|'
        r'shuttle|day[- ]use|boat|launch|ramp|electric|hookups?|cable|tv|breakfast|coffee|ice|laundry|'
        r'pump-?out|paddle|kayak|canoe|bikes?|golf|mini|pool|tours?|ebike|e-bike|dog|pet|rv dump)')
PAT = re.compile(r'(?<!barrier-)(?<!barrier )\b(?:no[- ]fee|no charge|free of charge|fee-free|free\b(?!\s*[-/]?\s*'
                 + AMEN + r'))', re.I)
out = []
for r in rows:
    if r.get('kind') == 'family' or r.get('fees'):
        continue
    n = r.get('note') or ''
    hits = [m for m in PAT.finditer(n)]
    if hits:
        out.append({'id': r['id'], 'name': r['name'], 'own': r.get('ownership'), 'note': n})
json.dump(out, open(sys.argv[1], 'w'), ensure_ascii=False, indent=0)
print(len(out), 'candidates')
