#!/bin/sh
# rc1night.sh CAMPING_ID YYYY-MM-DD
# One-night search on reservationcamping.ca (Pixum engine used by many Quebec private
# campgrounds; the operator's "Réserver" link carries camping_id=<hex>) for a 23-ft travel
# trailer on 2- or 3-service sites, then opens the first few result sites and prints each
# one's per-site minimum-stay line. Needs drv_server.py running (one browser).
#
# Why the second step matters: the nights <select> on the search form can start at 1 while
# EVERY site still answers "Ce site nécessite un minimum de 2 nuitées" on its own page
# (Camping Wigwam 2026-10-08). The site page is the only place the minimum shows.
D="$(dirname "$0")"
drv() { python3 "$D/drv.py" "$@"; }
drv goto url="https://secure.reservationcamping.ca/cgi-bin/reservation.cgi?camping_id=$1" wait=6000 >/dev/null
drv eval js="(()=>{const d=document.querySelector('input[name=date_arrivee]');d.value='$2';return d.value})()" >/dev/null
drv select sel='select[name=nuitees]' value=1 >/dev/null
# real clicks, not JS .checked=true: the form's own validator ignores script-set checkboxes
# and raises "Vous devez cocher au moins un type de service voulu"
drv click sel='input[name=type_equip][value="3"]' wait=400 >/dev/null
drv click sel='input[name=deux_service]' wait=400 >/dev/null
drv click sel='input[name=trois_service]' wait=400 >/dev/null
drv select sel='select[name=longueur]' label='23 pi. (7 m.)' >/dev/null
drv click sel='input[name=button]' wait=8000 >/dev/null
drv dialogs
drv text grep='sites disponibles|Aucun|aucun|minimum|/nuitée' ctx=0 max=1500 | head -14
# stop when nothing was found (otherwise "back" walks into an older search's history)
drv text grep='sites disponibles trouv' ctx=0 max=200 | grep -q '^[0-9]' || exit 0
for k in 0 3 7; do
  drv click text='Voir ce site' nth=$k wait=6000 >/dev/null && drv text grep='Réservation du site|minimum|À partir' ctx=0 max=300
  drv back wait=4000 >/dev/null
done
