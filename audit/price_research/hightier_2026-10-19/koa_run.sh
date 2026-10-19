#!/bin/bash
cd /home/andrew/Dev/campgrounds
D=audit/price_research/hightier_2026-10-19
for p in 940:tall-pines 1484:houghton-letchworth 4258:murphy 4584:americus 5304:mena 5537:spring-grove 6536:lyman 9122:grande-prairie 11476:salome 11511:yuma 12384:needles 12646:cardinal 12681:owen-sound 12688:renfrew 12707:thunder-bay 12802:drumheller 12804:hinton 12808:lethbridge 12821:winnipeg-west 12941:north-sydney 12957:truro 12991:borden 13041:gros-morne 13127:badlands 13131:mount-rushmore 13132:rapid-city 13140:hill-city 13143:spearfish 13144:deadwood 13145:hot-springs; do
  id=${p%%:*}; slug=${p#*:}
  echo "=== $id $slug" >> $D/koa.txt
  KOA_DUMP=$D/koa_dump_$id.txt PYTHONPATH=~/.cache/ekko-pw timeout 300 python3 audit/private_gap_browser/koa.py $slug 05/18/2027 05/19/2027 >> $D/koa.txt 2>&1
done
echo ALLDONE >> $D/koa.txt
