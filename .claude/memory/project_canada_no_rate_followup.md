---
name: project-canada-no-rate-followup
description: Re-quoting the 158 Canada private-gap no_rate parks via rate pages, booking engines, Wayback and Bonjour Quebec; QC DONE 2026-10-08 (72 settled, +39 appended as ids 15126-15164, 33 skips); ON (50) and BC (36) next. Workflow + status in audit/canada_no_rate/README.md
metadata:
  type: project
---

The Canada private gap ([[project-private-gap]]) skipped 158 well-rated private parks as `kind_of_no: "no_rate"` (QC 72, ON 50, BC 36): quality passed, but no nightly rate was found while the RV Life tier was over C$55.5 or unrated, and the gate needs a published rate of C$69 or less.

**AWH 2026-10-08:** "work through the effort"; read each site carefully, work through booking engines and date pickers, go slowly (one browser). A park that posts no rate AND books only by phone is a skip (that hassle signals a long-term-renter focus); a genuine posted rate, or one obtained through the booking engine, is wanted.

**Status (2026-10-08):** QC DONE - 72 of 72 settled: 39 adds appended as ids 15126-15164 (commit 'QC no_rate follow-up'), 33 skips. The 15-park pilot was 8 adds; AWH saw the hit rate and the work continued (paused once, resumed the same day). **Next: ON (50 rows), then BC (36)** - `python3 audit/canada_no_rate/info.py ON todo`; next append `--min-id 15165` (check the max id first). The QC add batch is reproducible: `audit/canada_no_rate/build_qc_results.py` (notes + inclusion lines) over `adds_work.json` and `qc_wf_calls.jsonl` (pin, waterfront call, evidence, elevation per add); copy it per province.

**Where the knowledge lives (don't re-derive it):**
- `audit/canada_no_rate/README.md` - files, verdict format (`followup: "no_rate 2026-10-08"`, latest row per name wins), kind_of_no values, status, next steps.
- `audit/private_gap_browser/README.md` - the one-browser driver (drv_server.py/drv.py), scan.py, engine helpers (rpa.sh reservationpleinair, rc1night.sh reservationcamping, rpro.py RéservPro, rms.sh RMS Cloud), wb.py Wayback imagery, bqread.py Bonjour Quebec, manual recipes (campin.ca, Reservit, WP `?item=` engines, Camping Union, Parkbridge), and two playbooks: where a "no rate" park's rate really is, and how to measure the seasonal share. Summary in [[reference-hidden-rates-playbook]].

**Working rules adopted in this pass (judgment calls, tell AWH if they matter):**
- Mostly seasonal = traveller sites under ~10% of the park (extends AWH's Sutter's ~9% precedent). Parkbridge parks are measured, not brand-skipped (Domaine des Érables ~20% added; Royal Papineau 7% / Panoramique 8% skipped).
- The official Bonjour Quebec "prix maximum" (operator-supplied CITQ listing, like the NL newfoundlandlabrador.com precedent) counts as a posted bound: max <= C$69 passes price (Chez Moose, Ensoleillé). Directories/aggregators still never count ([[feedback-note-rate-sourcing]]).
- An engine quote overrules a lower posted list price (Bellerive reversed to a C$75.50 price skip).
- Same-day single nights (Camping Union Nuitée Express, Lac-aux-Sables, phone 48 h ahead at Camping du Parc) are late-booking waivers, not standing minimums ([[feedback-minimum-stay]]). A men-only resort is restricted admission (Plein Bois skipped).
- Lac Libby kept as an add although its engine wanted 2 nights on the only testable date (Thanksgiving week) - caveat goes in the note.
- No holds ([[feedback-canada-no-holds]]).
- Camping au Petit Lac Simon SKIPPED although its official maximum is C$55: no operator rate anywhere and phone/e-mail booking only - AWH's named skip case; Chez Moose/Ensoleillé passed on the BQ maximum because they also book online. Flag if AWH disagrees.
- Waterfront calls in the add batch (judgment, not AWH-confirmed): judged on sites a traveller can book - a seasonal-only shore row doesn't make a park lakefront (Lac Libby -> lakeview); a lane, a public or campground swimming beach, or a car-free road between pads and water = view (Lac-aux-Sables, Lac Frontière, Oasis, Plage des Sables, Mine de Cuivre); canopy hides the stream -> defer to the per-site plan (Sainte-Madeleine creekside); a continuous riparian treeline = not waterfront (Camping Soleil, Lac et Forêt).
- Pins: Google's pin is often the office or the road; `audit/private_gap_browser/satpx.py LAT LNG Z X Y` converts a pixel in a satz.py/wb.py frame to lat/lng (the crosshair is not at the frame centre). Open-Meteo returns 0 m on a shoreline sea cell - take the nearest land cell (du Rivage 3 m).

**Why:** these were the largest pool of plausible adds left in Canada, and most of them do post rates the static crawl couldn't see.
**How to apply:** restart the driver, run `info.py ON todo`, work each row with scan.py then the engine helper its ENGINE line names; record with v.py (`on_private`); then build the ON add batch the way QC's was built, commit, and go on to BC.
