#!/bin/bash
# f.sh URL OUTNAME -> fetch to dl/OUTNAME.html, print status, write text dl/OUTNAME.txt
cd /tmp/claude-1000/-home-andrew-Dev-campgrounds/4dfcd82f-59f6-4dfa-978f-ba76c2044814/scratchpad/p3-437
code=$(curl -s -L -m 60 -A 'Mozilla/5.0' -o dl/$2.html -w '%{http_code} %{url_effective}' "$1")
echo "$code"
python3 -I tools/h2t.py dl/$2.html > dl/$2.txt; wc -c dl/$2.txt
