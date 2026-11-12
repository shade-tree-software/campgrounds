#!/bin/bash
# rzw.sh MM/DD/YYYY MM/DD/YYYY nights out  (Wolf Lake)
cd /tmp/claude-1000/-home-andrew-Dev-campgrounds/4dfcd82f-59f6-4dfa-978f-ba76c2044814/scratchpad/p3-437
B=wolf-lake-park-campground
curl -s -L -m 60 -A Mozilla/5.0 -c dl/rzw.txt -b dl/rzw.txt -o /dev/null "https://guest.rezstream.com/search/$B"
curl -s -L -m 60 -A Mozilla/5.0 -b dl/rzw.txt -c dl/rzw.txt -o dl/$4.html --data-urlencode "Arrival=$1" --data-urlencode "Departure=$2" --data "Nights=$3&BusinessSlug=$B&SearchType=ByIndividualUnit&Locale=en-us&SelectedGuests%5B0%5D.Id=ca08b00f-321c-4ec5-9438-b56fe50788d2&SelectedGuests%5B0%5D.NumberOfGuests=2&SelectedGuests%5B1%5D.Id=b1dc1712-fd75-4f5e-ad3a-c89aeb48c158&SelectedGuests%5B1%5D.NumberOfGuests=0&SelectedGuests%5B2%5D.Id=5d5fcddb-6ceb-4c30-bccf-2313362e5dcf&SelectedGuests%5B2%5D.NumberOfGuests=0&RequestADA=false" "https://guest.rezstream.com/search/$B"
python3 -I tools/h2t.py dl/$4.html | grep -v '^\s*$' | awk '{$1=$1};1' > dl/$4.txt
