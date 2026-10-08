# bqread.py URL -> key facts from a Bonjour Quebec listing (curl-readable SSR page)
import sys, re, html, subprocess
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
raw = subprocess.run(["curl", "-sSL", "-A", UA, "-H", "Accept-Language: fr-CA,fr;q=0.9", "--max-time", "30", sys.argv[1]],
                     capture_output=True, text=True, errors="ignore").stdout
raw = re.sub(r'(?is)<(script|style|noscript).*?</\1>', ' ', raw)
t = html.unescape(re.sub(r'<[^>]+>', '\n', raw))
L = [l.strip() for l in t.splitlines() if l.strip()]
rx = re.compile(r'saison|ouvert|du \d|au \d|\d{4}-\d\d|prix|\$|unit|emplacement|site à camper|voyageur|saisonnier|enregistrement|établissement|t[ée]l[ée]phone|\(\d{3}\)|\d{3}[ -]\d{3}[ -]\d{4}', re.I)
seen = set()
for i, l in enumerate(L):
    if rx.search(l) and len(l) < 160:
        s = ' | '.join(L[max(0, i - 1):i + 2])
        if s not in seen:
            seen.add(s); print(s[:220])
