---
name: reference-hidden-rates-playbook
description: How to find a private campground's real nightly rate, minimum stay and seasonal share when the static crawl says "no rate" - browser driver + booking-engine helpers + Wayback imagery + Bonjour Quebec; full recipes in audit/private_gap_browser/README.md
metadata:
  type: reference
---

Built 2026-10-08 during [[project-canada-no-rate-followup]]; of 72 Quebec "no_rate" parks, most turned out to post a rate. Full recipes, commands and examples: `audit/private_gap_browser/README.md` (sections "Interactive driver and booking-engine recipes" and the two playbooks). Setup is the same as the other helpers there (`PYTHONPATH=~/.cache/ekko-pw`, Playwright Chromium).

**Tools (all in audit/private_gap_browser/, one browser only - [[feedback-limit-headless-browsers]]):**
- `drv_server.py` + `drv.py` - ONE persistent Chromium driven step by step over `~/.cache/ekko-drv.sock`: goto/click/xy/fill/select/shot (Read the PNG)/eval/net+body (read a booking engine's XHR JSON directly).
- `scan.py URL` - first look at any park: rate/booking/plan links, ENGINE hosts, every `$` line.
- `rpa.sh` reservationpleinair.ca · `rc1night.sh` reservationcamping.ca · `rpro.py` RéservPro · `rms.sh` RMS Cloud (Parkbridge) · `wb.py` Esri Wayback capture dates + tiles · `bqread.py` Bonjour Quebec listing.

**Non-obvious things that cost time to learn:**
- Rates hide in hidden tabs/accordions (read `document.body.textContent`, not innerText), in images (Wix "tarifs 2026.jpg"), lazy-loaded sections, separate policy/reservation pages, or only in the engine.
- reservationcamping.ca shows the minimum stay ONLY on each site's "Voir ce site" page; the nights select proves nothing. RéservPro minimums are per service type and date; its `check-disponibilite_service` JSON gives Prix and NbrDispo (= traveller sites free).
- RMS Rates page opens directly by URL (no picker); "From CAD" is tax-included, the daily grid is pre-tax.
- Wayback CDX recovers last season's rate table when the page now says "prix à venir".
- Bonjour Quebec's "prix maximum" bounds every site and reveals whether operator prices include tax; it also shows current-season operation.
- QC tax: /1.14975 (GST+QST); campsites are exempt from the 3.5% lodging tax.
- wordpress.com "I am human" pages: curl with a browser UA reads them. campingquebec.com Cloudflare: don't bypass.
- Seasonal share: operator map legend counts > engine NbrDispo > pre-opening/post-closing Wayback frames (stored trailers on nearly every pad = seasonal). Summer leaf-on imagery can't decide it; Thanksgiving-weekend captures are still in season.
- 2027 booking was mostly not open in October 2026: use the posted current-season table or any open date.
