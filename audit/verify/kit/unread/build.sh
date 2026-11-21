#!/bin/bash
# build.sh S N ST id1,id2,...   -> batches/N.json + S/N_prompt.txt + S/N_agent.txt + S/N/tools
# A retry batch of entries left UNREAD behind bot walls (AWH 2026-11-20 allowed headless browser,
# Wayback and strong secondary sources for these). Uses the state's own kit for brief + template,
# with hard rule 13 (no retry by any route) replaced by kit/unread/retry_rule.txt.
set -e
S=$1; N=$2; ST=$3; IDS=$4; st=$(echo $ST | tr A-Z a-z); K=audit/verify/kit
python3 -I - "$N" "$IDS" <<'PY'
import importlib.util,json,sys
spec=importlib.util.spec_from_file_location('q','audit/verify/queue.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
rows,reg,trips=q.load(); by={e['id']:e for e in rows}
ids=[int(x) for x in sys.argv[2].split(',')]
json.dump([q.dossier(by[i],reg) for i in ids],open(f'audit/verify/batches/{sys.argv[1]}.json','w'),ensure_ascii=False,indent=1)
PY
python3 -I $K/$st/mkpara_$st.py $S $N
python3 -I $K/mkbrief_mo.py $S $N $S/${N}_para.txt >/dev/null
mkdir -p $S/$N; T=$K/il/tools; [ -d $K/$st/tools ] && T=$K/$st/tools; cp -r $T $S/$N/tools
n=$(echo $IDS | tr ',' '\n' | wc -l)
W=(zero ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE TEN ELEVEN TWELVE); w=${W[$n]}; lw=$(echo $w | tr A-Z a-z)
python3 -I - "$K/$st/agent_prompt_template.txt" "$S/${N}_agent.txt" "$S" "$N" "${IDS//,/, }" "$w" "$lw" <<'PY'
import sys
src,dst,S,N,ids,w,lw=sys.argv[1:]
t=open(src,encoding='utf-8').read().replace('SCRATCH',S).replace('p3-NNN',N).replace(': IDS.',': '+ids+'.')
t=t.replace('ELEVEN',w).replace('eleven',lw)
L=t.split('\n'); i=[k for k,l in enumerate(L) if 'is not retried by ANY other route' in l]; assert len(i)==1
L[i[0]]=open('audit/verify/kit/unread/retry_rule.txt',encoding='utf-8').read().strip()
t='\n'.join(L).replace("If an entry's own pages all refuse you, write no result file for it and say so.","If all the allowed routes fail for an entry, write no result file for it and say so.")
open(dst,'w',encoding='utf-8').write(t)
PY
L=$K/$st/lessons.txt; [ -f $L ] && { printf '\n' >> $S/${N}_agent.txt; cat $L >> $S/${N}_agent.txt; }
echo "$N $ST $n ids"
