import json,sys,re,collections
A={'123':'wifi','502':'lakeview','503':'lakefront','535':'pet','544':'pull','545':'30A','546':'50A','547':'20A','553':'40-50','554':'30-40','555':'20-30','556':'50-60','557':'60-70','603':'ADA','736':'riverview','737':'riverfront','738':'full','739':'water','740':'sewer','769':'ev'}
d=json.load(open(sys.argv[1]))
for sid in sys.argv[2:]:
    r=d[sid]; print('##',sid,r['name'])
    units={}
    for stay,rows in r['stays'].items():
        if not isinstance(rows,list): print(stay,rows); continue
        print(' ',stay,len(rows),dict(collections.Counter(x['price'] for x in rows)))
        for x in rows: units[x['unit']]=(x['att'],units.get(x['unit'],(None,set()))[1]|{x['price']})
    g=collections.Counter()
    for u,(a,p) in units.items():
        loop=re.sub(r'^Site [^,]*, ','',u)
        codes=tuple(sorted({A.get(c,c) for c in re.findall(r'53,(\d+)',a or '')}-{'wifi','pet','ADA','ev'}))
        g[(loop,codes,tuple(sorted(p)))]+=1
    for k,v in sorted(g.items()): print('   ',v,k)
