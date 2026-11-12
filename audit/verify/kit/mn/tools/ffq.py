# ffq.py ARR DEP [ARR DEP ...]  (MM/DD/YYYY) Firefly search quotes for Pine Trails
import sys, os, json
sys.path.insert(0, os.path.expanduser('~/.cache/ekko-pw'))
from playwright.sync_api import sync_playwright
UA="Mozilla/5.0"
U=os.environ["FFURL"]
a=sys.argv[1:]
with sync_playwright() as p:
    ex=next((c for c in ('/opt/pw-browsers/chromium-1194/chrome-linux/chrome','/usr/bin/google-chrome') if os.path.exists(c)),None)
    b=p.chromium.launch(executable_path=ex, channel=(None if ex else 'chromium'))
    pg=b.new_page(ignore_https_errors=True,user_agent=UA)
    for i in range(0,len(a),2):
        arr,dep=a[i],a[i+1]
        try:
            pg.goto(U,timeout=60000,wait_until='networkidle'); pg.wait_for_timeout(3000)
            info=pg.evaluate("""([arr,dep])=>{var s=$('#unit-type select'); var o=s.find('option').map(function(){return this.value+':'+$(this).text().trim()+':'+$(this).data('showrvfields')}).get();
              var v=s.find('option').filter(function(){return this.value}).first().val(); s.val(v).trigger('change');
              $('#arrival-date-value').val(arr); $('#departure-date-value').val(dep);
              $('#rv-length input').val('23'); $('#rv-slides select').prop('disabled',false).val('N'); $('#rv-equipment select').prop('disabled',false).val('MHC'); $('#rv-age input').val('2020');
              return o}""",[arr,dep])
            with pg.expect_response(lambda r:'/Reserve/SearchForAvailable' in r.url,timeout=45000) as ri:
                pg.click('#search-availability-btn')
            t=ri.value.text(); pg.wait_for_timeout(2500)
            body=pg.evaluate("document.body.innerText")
        except Exception as x:
            info='';t=f"ERR {x}";body=''
        fn=f"ff_{arr.replace('/','')}_{dep.replace('/','')}"
        open(fn+".resp","w").write(t); open(fn+".txt","w").write(str(info)+"\n"+body)
        print(arr,dep,len(t),len(body),info)
    b.close()
