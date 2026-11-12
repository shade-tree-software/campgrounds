#!/bin/bash
# rz.sh MM/DD/YYYY MM/DD/YYYY nights out
cd /tmp/claude-1000/-home-andrew-Dev-campgrounds/4dfcd82f-59f6-4dfa-978f-ba76c2044814/scratchpad/p3-437
curl -s -L -m 60 -A Mozilla/5.0 -c dl/rzc.txt -b dl/rzc.txt -o /dev/null "https://guest.rezstream.com/search/akeleycitycampground"
curl -s -L -m 60 -A Mozilla/5.0 -b dl/rzc.txt -c dl/rzc.txt -o dl/$4.html --data-urlencode "Arrival=$1" --data-urlencode "Departure=$2" --data "Nights=$3&BusinessSlug=akeleycitycampground&SearchType=ByIndividualUnit&Locale=en-us&SelectedGuests%5B0%5D.Id=204fe4ce-d1ed-421a-a6a5-c8ee400babf2&SelectedGuests%5B0%5D.NumberOfGuests=2&SelectedGuests%5B1%5D.Id=ea681cd1-c67d-4f95-8e82-a0d6b89af6f2&SelectedGuests%5B1%5D.NumberOfGuests=0&RequestADA=false" "https://guest.rezstream.com/search/akeleycitycampground"
python3 -I tools/h2t.py dl/$4.html | grep -v '^\s*$' | awk '{$1=$1};1' | python3 -I -c "
import sys,re
cur=None;out={}
for l in sys.stdin:
    l=l.strip()
    if re.match(r'^(RV|Tent) Site',l): cur=l; out[cur]=[]
    elif cur and re.search(r'minimum|not permitted|\\\$\d+ / night|Daily|unavailable|not available',l): out[cur].append(l)
for k,v in out.items(): print(k,'|',' ; '.join(dict.fromkeys(v))[:220])
"
