import json,sys,collections,re
d=json.load(open('wvt.json')); sid=sys.argv[1]; sub=sys.argv[2] if len(sys.argv)>2 else ''
units=set()
for stay,rows in d[sid]['stays'].items():
    rs=[x for x in rows if sub in x['unit']] if isinstance(rows,list) else []
    units|={x['unit'] for x in rs}
    c=collections.defaultdict(list)
    for x in rs: c[x['price']].append(re.sub(r'\D','',x['unit'].split(',')[0]))
    print(stay,len(rs),{k:(len(v),','.join(sorted(v,key=int))) for k,v in c.items()})
print(len(units),'units')
