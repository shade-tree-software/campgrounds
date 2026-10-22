import re,sys,urllib.request,html,concurrent.futures as cf
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
B="https://book.wvstateparks.com/Ecomm/Listings/SupplierTile/7816932/en-US"
def f(sid):
    u=f"{B}?supplierId={sid}&arrivalDate=2027-06-15&departureDate=2027-06-16&adultCount=2&childCount=0"
    try: t=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":UA}),timeout=30).read().decode('utf-8','replace')
    except Exception as e: return sid,'ERR'
    m=re.search(r'id="supplierName_\d+">([^<]*)<',t)
    return sid,(html.unescape(m.group(1)).strip() if m else '')
a,b=int(sys.argv[1]),int(sys.argv[2])
with cf.ThreadPoolExecutor(4) as ex:
    for sid,n in ex.map(f,range(a,b)):
        if n: print(sid,n,flush=True)
