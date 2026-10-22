import json,sys,re,collections
A={'123':'wifi','502':'lakeview','503':'lakefront','535':'pet','544':'pull','545':'30A','546':'50A','547':'20A','553':'40-50','554':'30-40','555':'20-30','556':'50-60','557':'60-70','603':'ADA','736':'riverview','737':'riverfront','738':'full','739':'water','740':'sewer','769':'ev'}
d=json.load(open('wvt.json'))
for sid in sys.argv[1:]:
    r=d[sid]; print('##',sid,r['name'])
    for stay,rows in r['stays'].items():
        if not isinstance(rows,list): print(stay,rows); continue
        pr=collections.Counter(x['price'] for x in rows)
        print(' ',stay,len(rows),dict(pr))
    # union of units across stays
    units={}
    for rows in r['stays'].values():
        if isinstance(rows,list):
            for x in rows: units[x['unit']]=x['att']
    for u,a in sorted(units.items()):
        codes=[A.get(c,c) for c in re.findall(r'53,(\d+)',a)] if a else []
        print('   ',u,'|',' '.join(codes) if codes else a[:80])
