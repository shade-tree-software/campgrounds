"""One site's 1-night price on a date: python3 ra_price.py HOST CONTRACT PARKID SITEID M/D/YYYY"""
import html, re, sys, urllib.request, http.cookiejar
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
def price(host, cc, pid, sid, d, op=None):
    if op is None:
        op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())); op.addheaders = [("User-Agent", UA)]
        op.open(f"{host}/campgroundDetails.do?contractCode={cc}&parkId={pid}", timeout=60).read()
    t = op.open(f"{host}/campsiteDetails.do?contractCode={cc}&parkId={pid}&siteId={sid}&arvdate={d}&lengthOfStay=1", timeout=60).read().decode("utf-8", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S | re.I)
    t = re.sub(r"<(br|p|li|tr|td|th|h\d|div)[^>]*>", "\n", t, flags=re.I)
    L = [re.sub(r"\s+", " ", l).strip() for l in html.unescape(re.sub(r"<[^>]+>", " ", t)).split("\n") if l.strip()]
    k = next((j for j, l in enumerate(L) if l in ("Camping Fees (1 night)", "Use Fees (1 night)")
              or (l in ("Camping Fees", "Use Fees") and j + 1 < len(L) and L[j + 1] == "(1 night)")), None)
    if k is None:
        # Newer hosts (Delaware, 2026) print 'Price Breakdown: / Residents Pay / Non-Residents Pay / $46.00 /
        # Price Details ... / $58.00 ...'; return the first amount (the resident's) and leave L whole.
        j = next((j for j, l in enumerate(L) if l.startswith("Price Breakdown")), None)
        if j is None: return None, L
        m = next((re.search(r"\$[\d,]+\.\d\d", l) for l in L[j + 1:j + 8] if re.search(r"\$[\d,]+\.\d\d", l)), None)
        return (m.group(0) + " Per Night (Price Breakdown)" if m else None), L
    return next((l for l in L[k + 1:k + 4] if "$" in l), None), L
if __name__ == "__main__":
    p, L = price(*sys.argv[1:6]); print(p)
    if p is None: print(' / '.join(L[8:60])[:1500])
