"""Read Arkansas State Parks' parkwide campsite calendars (reserve.arkansasstateparks.com, the same vendor as the SC/AL/TN
reserve.*parks sites) through the one-browser driver: python3 -I ar_calendar.py OUT.json SLUG [SLUG ...]

For each park: open /<slug>/camping, switch to Calendar View (two weeks from today), read the table, then submit the
page's own form from 06/15/27 and read again. Every row of the table carries its site's attributes (data-usetype rv-tent
or tent, data-maxrv, data-water, data-sewer, data-amps, data-access) and each night a cell 'avail' with the price or
'sold' without one ('The quoted rate for each night does not include taxes or the reservation fee')."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DRV = os.path.join(HERE, "..", "private_gap_browser", "drv.py")
READ = """(function(){
  const hdr = Array.from(document.querySelectorAll('thead th')).map(t => t.innerText.replace(/\\s+/g, ' ').trim());
  const rows = Array.from(document.querySelectorAll('tr[data-usetype]')).map(tr => {
    const d = tr.dataset;
    const cells = Array.from(tr.querySelectorAll('td')).slice(1).map(td => [td.className.trim(), td.innerText.trim()]);
    return {site: d.description, usetype: d.usetype, maxrv: d.maxrv, water: d.water, sewer: d.sewer, amps: d.amps,
            access: d.access, cells: cells};
  });
  return JSON.stringify({hdr: hdr, rows: rows});
})()"""


def d(*args):
    return subprocess.run([sys.executable, DRV, *args], capture_output=True, text=True).stdout


out = {}
for slug in sys.argv[2:]:
    d("goto", f"url=https://reserve.arkansasstateparks.com/{slug}/camping", "wait=7000")
    d("click", "text=Calendar View")
    d("wait", "wait=8000")
    now = json.loads(d("eval", "js=" + READ, "max=20000000") or "{}")
    r = d("eval", "js=(()=>{const f=jQuery('#resForm'); if(!f.length) return 'no form'; jQuery('#pwFromDate').val('06/15/27');"
                  "f.find('input[name=processing]').val('true'); f.submit(); return 'ok'})()")
    d("wait", "wait=9000")
    summer = json.loads(d("eval", "js=" + READ, "max=20000000") or "{}")
    out[slug] = {"now": now, "2027-06-15": summer}
    print(slug, len(now.get("rows", [])), "rows now,", len(summer.get("rows", [])), "rows from 2027-06-15", r.strip(), flush=True)
json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False)
