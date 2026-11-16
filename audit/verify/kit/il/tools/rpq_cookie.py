import sys,re,json,http.cookiejar,urllib.request
slug=sys.argv[1]
cj=http.cookiejar.CookieJar();op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
UA="Mozilla/5.0"
page=f"https://www.roverpass.com/c/{slug}/booking/"
h=op.open(urllib.request.Request(page,headers={"User-Agent":UA}),timeout=60).read().decode("utf-8","replace")
csrf=re.search(r'name="csrf-token" content="([^"]+)"',h).group(1)
q=sys.argv[2]; v=json.loads(sys.argv[3])
hd={"User-Agent":UA,"Content-Type":"application/json","Accept":"*/*","apollo-require-preflight":"true","x-csrf-token":csrf,"Origin":"https://www.roverpass.com","Referer":page}
try:
  r=op.open(urllib.request.Request("https://www.roverpass.com/api/queries/",data=json.dumps({"query":q,"variables":v}).encode(),headers=hd),timeout=60)
  print(r.read().decode()[:6000])
except urllib.error.HTTPError as e: print(e.code,e.read()[:500])
