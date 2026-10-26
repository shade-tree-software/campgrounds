import sys,re,time,subprocess,html,json
slug,park=sys.argv[1],sys.argv[2]
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
base=f"https://floridastateforests.reserveamerica.com/camping/{slug}/r/"
def get(u):
    return subprocess.run(["curl","-sL","-A",UA,"-c","/tmp/claude-1000/-home-andrew-Dev-campgrounds/d7d0d5a8-aeb2-47df-8eee-5ca5f5df7c93/scratchpad/ck.txt","-b","/tmp/claude-1000/-home-andrew-Dev-campgrounds/d7d0d5a8-aeb2-47df-8eee-5ca5f5df7c93/scratchpad/ck.txt",u],capture_output=True,text=True).stdout
ids={}
for st in (0,25,50,75):
    h=get(base+f"campsiteSearch.do?contractCode=FLFS&parkId={park}&startIdx={st}")
    for sid,lab in re.findall(r"siteId=(\d+)&(?:amp;)?parkId=\d+'\s+aria-label='Site: ([^']*)'",h):
        ids[sid]=lab
    m=re.search(r"(\d+) site\(s\) found",h)
    if m and len(ids)>=int(m.group(1)): break
    time.sleep(1)
out=[]
for sid,lab in ids.items():
    h=get(base+f"campsiteDetails.do?contractCode=FLFS&siteId={sid}&parkId={park}")
    t=html.unescape(re.sub(r'<[^>]+>',' ',h)); t=re.sub(r'\s+',' ',t)
    def f(k):
        m=re.search(re.escape(k)+r':\s*([^:]{0,40}?)\s+(?=[A-Z][A-Za-z /()-]+:|Alerts)',t); return m.group(1).strip() if m else None
    r=dict(site=lab,type=f("Type"),prox=f("Proximity to Water"),view=f("Type of View"),lat=f("GIS Details Latitude"),lng=f("GIS Details Longitude"),wf=f("Waterfront"))
    out.append(r); print(json.dumps(r)); time.sleep(0.7)
json.dump(out,open(sys.argv[3],"w"),indent=0)
