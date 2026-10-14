"""drvtc.py OUTDIR ID=URL[,URL...] ...: like drvfetch.py, but saves the DOM's textContent (block elements split onto
lines), so collapsed accordion panels are kept; Linn County's park pages hide their fees in those (batch 29, 2026-10-14)."""
import os, subprocess, sys
D = ["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "private_gap_browser", "drv.py")]
def drv(*a, t=150):
    try:
        return subprocess.run(D + list(a), capture_output=True, text=True, timeout=t).stdout
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
JS = ("(()=>{const b=document.querySelector('main')||document.body;const c=b.cloneNode(true);"
      "c.querySelectorAll('script,style,noscript').forEach(e=>e.remove());"
      "c.querySelectorAll('p,div,li,tr,h1,h2,h3,h4,h5,h6,br,td,th,section,article,dt,dd').forEach(e=>e.insertAdjacentText('afterend','\\n'));"
      "return c.textContent.split('\\n').map(s=>s.replace(/\\s+/g,' ').trim()).filter(Boolean).join('\\n');})()")
out = sys.argv[1]
for arg in sys.argv[2:]:
    i, urls = arg.split("=", 1)
    for url in urls.split(","):
        g = drv("goto", f"url={url}", "wait=6000").strip()
        final = drv("eval", "js=location.href").strip()
        txt = drv("eval", "js=" + JS, "max=400000", t=120)
        with open(os.path.join(out, f"{i}.txt"), "a", encoding="utf-8") as f:
            f.write(f"\n##### {url} -> {final} (rendered, textContent)\n{txt}\n")
        print("=====", i, url, "->", final, "|", len(txt), "chars")
