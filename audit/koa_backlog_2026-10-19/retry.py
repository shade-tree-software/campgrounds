"""Re-quote the no-quote KOAs on a night their booking calendar actually covers (quote.py tried May/June
2027, past most calendars' last bookable date). Dates per slug were chosen from each page's own
"latest date you can make a reservation" line: a Tuesday inside the window, the winter peak for the
southern winter parks. Progress is the data (quotes_retry.jsonl), so a killed run resumes."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quote import quote, HERE
OUT = os.path.join(HERE, 'quotes_retry.jsonl')
PLAN = {
 '10/27/2026': ['colorado-river', 'batesville', 'brown-county', 'milford-lake', 'cooperstown', 'watkins-glen',
                'mount-gilead', 'sandusky', 'mallorytown', 'lake-conroe'],
 '11/10/2026': ['harrison', 'royal-gorge', 'indianapolis-west', 'dodge-city', 'joplin', 'starkville', 'boone',
                'canton', 'cave-junction', 'montreal-south', 'lubbock', 'beaver', 'fillmore', 'lynden',
                'starbuck', 'flatwoods', 'topeka', 'bristol'],
 '01/19/2027': ['kerrville'],
 '02/16/2027': ['mesa', 'parkerstrip', 'bradenton'],
 '04/27/2027': ['carbondale'],
}
done = {json.loads(l)['slug'] for l in open(OUT)} if os.path.exists(OUT) else set()
for ci, slugs in PLAN.items():
    m, d, y = ci.split('/')
    import datetime
    co = (datetime.date(int(y), int(m), int(d)) + datetime.timedelta(days=1)).strftime('%m/%d/%Y')
    for s in slugs:
        if s in done:
            continue
        q = quote(s, ci, co)
        with open(OUT, 'a') as fh:
            fh.write(json.dumps({'slug': s, 'tries': [q]}, ensure_ascii=False) + '\n')
        ps = [t['price'] for t in q['types'] if t['price']]
        print('%-22s %s %s %s' % (s, ci, min(ps) if ps else '-', q.get('info', '')[:90]), flush=True)
