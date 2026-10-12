"""Read the two-week campsite calendar of a reserve.<state>parks site (the vendor behind
reserve.southcarolinaparks.com, reserve.alapark.com and reserve.tnstateparks.com), now and from a
summer 2027 date, through the one-browser driver (audit/private_gap_browser/drv_server.py).

    python3 vendor_calendar.py HOST OUTDIR [--zip 19087] [--from 2027-06-15] SLUG [SLUG ...]

For each park: open /<slug>/campsites, answer the residency zip prompt if one appears, switch to
Calendar View if the page offers it, save the text, then submit the page's own form with the
summer date (setting the flatpickr value and calling its onChange fails: the handler reads
window.event) and save that text too. OUTDIR/<slug>_now.txt and OUTDIR/<slug>_<date>.txt."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DRV = os.path.join(HERE, "..", "private_gap_browser", "drv.py")


def d(*args):
    return subprocess.run([sys.executable, DRV, *args], capture_output=True, text=True).stdout


args = sys.argv[1:]
host, out = args[0], args[1]
zipc = args[args.index("--zip") + 1] if "--zip" in args else None
when = args[args.index("--from") + 1] if "--from" in args else "2027-06-15"
slugs = [a for a in args[2:] if not a.startswith("--") and a not in (zipc, when)]
os.makedirs(out, exist_ok=True)
for slug in slugs:
    d("goto", f"url=https://{host}/{slug}/campsites", "wait=7000")
    if zipc and "residentZip" in d("buttons"):
        d("type", "sel=#residentZip", f"value={zipc}")
        d("press", "key=Enter")
        d("wait", "wait=7000")
    if "Calendar View" in d("text", "max=20000"):
        d("click", "text=Calendar View")
        d("wait", "wait=8000")
    open(os.path.join(out, f"{slug}_now.txt"), "w").write(d("text", "max=60000"))
    js = ('(()=>{const f=jQuery("#resForm"); if(!f.length) return "no form"; jQuery("#pwFromDate").val("%s");'
          'f.find("input[name=processing]").val("true"); f.submit(); return "ok"})()' % when)
    r = d("eval", "js=" + js)
    d("wait", "wait=10000")
    open(os.path.join(out, f"{slug}_{when}.txt"), "w").write(d("text", "max=60000"))
    print(slug, r.strip(), flush=True)
