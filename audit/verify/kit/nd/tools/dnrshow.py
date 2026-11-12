# dnrshow.py file.json -> text of alert, overnight_facilities, amenities, seasonal_update, point
import sys,json,re,html
d=json.load(open(sys.argv[1]))['result']
def t(x):
    if isinstance(x,(dict,list)): x=json.dumps(x,ensure_ascii=False)
    x=re.sub(r'<br ?/?>|</p>|</li>|</h\d>','\n',str(x)); x=re.sub(r'<[^>]+>','',x); return html.unescape(x)
for k in ('point','contact','alert','seasonal_update','overnight_facilities','amenities','recreation_facilities','maps'):
    print('=====',k); print(t(d.get(k))[:int(sys.argv[2]) if len(sys.argv)>2 else 6000])
