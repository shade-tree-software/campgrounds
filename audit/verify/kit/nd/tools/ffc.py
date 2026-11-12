import sys, os, json
sys.path.insert(0, os.path.expanduser('~/.cache/ekko-pw'))
from playwright.sync_api import sync_playwright
UA="Mozilla/5.0"
U=os.environ["FFURL"]
with sync_playwright() as p:
    ex=next((c for c in ('/opt/pw-browsers/chromium-1194/chrome-linux/chrome','/usr/bin/google-chrome') if os.path.exists(c)),None)
    b=p.chromium.launch(executable_path=ex, channel=(None if ex else 'chromium'))
    pg=b.new_page(ignore_https_errors=True,user_agent=UA)
    pg.goto(U,timeout=60000,wait_until='networkidle'); pg.wait_for_timeout(2000)
    for m in sys.argv[1:]:
        r=pg.evaluate("""async (m)=>{var s=$('#unit-type select'); s.val('RV');
          var sp={PropertyGUID:$('#property-guid').val(),ReservationGUID:$('#reservation-guid').val(),ReservationType:'S',ArrivalDate:m,DepartureDate:m,Adults:2,Children:0,Pets:0,UnitType:'RV',RVSlides:'N',RVLength:'23',RVEquipmentType:'MHC',RVManufactureYear:'2020',RequiredAmenities:'',DurationMode:'NIGHTLY'};
          return await new Promise(res=>$.ajax({type:'POST',url:'/Reserve/GetPropertyAvailabilityCalendar',data:{searchParams:sp,firstDayOfMonth:m},success:h=>res(typeof h=='string'?h:JSON.stringify(h)),error:x=>res('ERR '+x.status)}))}""",m)
        open("ffc_"+m.replace('/','')+".html","w").write(r); print(m,len(r))
    b.close()
