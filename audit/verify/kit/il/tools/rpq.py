import sys,json
sys.path.insert(0,'/home/andrew/Dev/campgrounds/audit/private_gap_browser')
import roverpass_api as R
R.UA="Mozilla/5.0"
slug=sys.argv[1]; d=sys.argv[2]
R.session(slug)
g,err=R.info(slug); print(json.dumps(g)[:2500])
r=R.post(R.DAY,{"slug":slug,"from":d,"to":R.next_day(d),"filters":{}})
c=r["data"]["campground"]; print("avail",c["availability"],c.get("sitesCountByTypeDuring"))
for rt in c["ratesAvailableDuring"]+c["unavailableRatesMinNightsList"]:
    print("RATE",rt["id"],rt["name"],rt["siteTypeName"],rt["maxLength"],rt["minNightsRequired"],rt["nightPrice"],rt["amenities"],(rt.get("description") or "")[:200])
    s=R.post(R.SITES,{"slug":slug,"from":d,"to":R.next_day(d),"rateId":rt["id"]})
    for x in s["data"]["campground"]["sitesAvailableDuring"] or []:
        print("   SITE",x["name"],x["maxLength"],x["amenities"],(x.get("description") or "")[:150])
