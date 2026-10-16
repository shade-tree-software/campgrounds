# dp.sh URL [grep] - driver page: $ lines + fee/rate links
DRV=/home/andrew/Dev/campgrounds/audit/private_gap_browser/drv.py
python3 $DRV goto "url=$1" "wait=${WAIT:-6000}" timeout=40000 | head -1
python3 $DRV text "grep=${2:-\\\$\\s?\\d}" ctx=0 max=${MAX:-4000}
echo "-- links"; python3 $DRV links 'grep=fee|rate|pric|camp' max=1500 | head -${NL:-25}
