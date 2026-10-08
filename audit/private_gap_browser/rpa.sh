#!/bin/sh
# rpa.sh SLUG ARRIVE DEPART      (dates YYYY-MM-DD)
# reservationpleinair.ca (Manisoft) list view for 2 adults: one line per unit/site type with
# its services, equipment-length range and "À PARTIR DE" price. SLUG is the path segment in
# the operator's Réserver link (reservationpleinair.ca/<slug>/fr/reservation), e.g.
# bsl-resort, pleinbois, parc, soleil, beausoleil, vallee-bleu.
# Notes: a price of "-" means the dates are not priced/open yet (2027 was not, Oct 2026);
# the list is paged (10 per page), so the row count is NOT a site count. Needs drv_server.py.
D="$(dirname "$0")"
drv() { python3 "$D/drv.py" "$@"; }
drv goto url="https://reservationpleinair.ca/$1/fr/choix-unite/CP/liste?typehebergement=CP&arrivee=$2&depart=$3&adultes=2&enfants=0&typeservice=-1&extraid=&extravalue=&include=arriveeDepartTypeUnite,planBase,indisponibilites" wait=9000 >/dev/null
drv eval js="(()=>{const t=document.body.innerText.split('\n').map(s=>s.trim()).filter(Boolean);const out=[];let name='',serv='',eq='';for(let i=0;i<t.length;i++){if(/critères de recherche/.test(t[i])){name=t[i+1];serv=t[i+3];eq=(t.slice(i,i+8).find(x=>/Dimensions d.équipement/.test(x))||'');}if(t[i]==='À PARTIR DE'){out.push(name+' || '+serv.slice(0,70)+' || '+eq+' || '+t[i+1]);}}return out.length+' rows\n'+out.join('\n')})()"
drv text grep='minimum|Minimum|nuitées minimum|séjour minimum' ctx=0 max=400
