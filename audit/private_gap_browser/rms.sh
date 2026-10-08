#!/bin/sh
# rms.sh CLIENT_ID ARRIVE DEPART [AGENT_ID]      (dates YYYY-MM-DD; agent defaults to 137)
# RMS Cloud quote (Parkbridge resorts and others: the operator's "Réservez/Book now" link is
# bookings.rmscloud.com/Search/Index/<CLIENT_ID>/<AGENT_ID>). Opens the Rates page directly
# for 2 adults + a travel trailer (T=13, L=1) - no date-picker clicking needed - and prints,
# per site type: the "From CAD" figure (tax-INCLUDED in Quebec: GST+QST) and the first
# night of the daily grid (PRE-tax; the daily grid also shows the weekend rate).
# Verified 2026-10-08 on Domaine des Érables (8772/137): From CAD 65.54 = C$57 pre-tax
# weeknight, C$73 Fri/Sat. Needs drv_server.py.
D="$(dirname "$0")"
drv() { python3 "$D/drv.py" "$@"; }
A=$(date -d "$2" +%m/%d/%Y); DD=$(date -d "$3" +%m/%d/%Y); AG=${4:-137}
drv goto url="https://bookings.rmscloud.com/Rates/Index/$1/$AG?A=$A&D=$DD&Rt=1&Ad=2&Mp=0&T=13&L=1&M=0&Y=0&Z=0" wait=12000
drv eval js="(()=>{const t=document.body.innerText.split('\n').map(s=>s.trim()).filter(Boolean);const out=[];for(let i=0;i<t.length;i++){if(/^From CAD/.test(t[i])){const name=t[i+1];let j=i;while(j<t.length&&t[j]!=='Add')j++;const grid=t.slice(j+1,j+13).filter(x=>/^[0-9.]+$/.test(x));out.push(name+' || '+t[i]+' (tax-incl) || nightly pre-tax: '+grid.join(' '));}}return out.length?out.join('\n'):t.slice(0,40).join(' / ')})()" max=3000
