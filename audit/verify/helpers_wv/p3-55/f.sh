#!/bin/bash
# f.sh URL out.txt
curl -sL -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36' --max-time 40 "$1" -o "$2.html"; python3 -I /tmp/claude-1000/-home-andrew-Dev-campgrounds/5a2365fc-fe6c-4508-9059-5f9b77057f7c/scratchpad/p3-55/h2t.py "$2.html" > "$2"; wc -c "$2"
