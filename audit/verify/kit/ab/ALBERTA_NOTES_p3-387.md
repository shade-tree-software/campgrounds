# p3-387 Alberta notes

Results are in audit/verify/results/<id>.json. The apply.py dry run on all 12 is clean (no "!!").

## Per entry
- 9099 Red Deer Lions: base 40 -> 52.50 (the 15-amp sites are for "very small RVs"); C$15 reservation fee; phone -> 403-506-4449; ownership unread; not waterfront.
- 12810 River Grove: Campspot C$60-65 + GST; 98 RV sites; season 04-30..09-19; Google 4.1/625.
- 8935 Rochon Sands: books on Let's Camp, so platform campspot -> operator; potable water -> false; lakeview confirmed; policy_ref none candidate.
- 9088 Ross Creek: C$52 + GST; phone -> 403-581-7975; long-stay passes on the posted daily rate; booking by phone.
- 12811 Runway: DROP CANDIDATE. No rate, RV Life $$$, Google 4.7 from only 21 reviews.
- 9132 Sagitawah: C$39-42; phone -> 780-778-3734; worker wording, but a nightly rate is posted.
- 12812 Sandy Point: C$45-64 + GST on Campspot; lakeview kept with a caveat; PIN ~230 m off -> 52.5053,-114.0065.
- 8954 Saskatoon Island: 84 of 90 sites capped at 21 ft (FIT question); closed through May 19 2027; season conflict with manual provenance.
- 9134 Shaws Point: ResNexus C$52-58; phone -> 780-751-3900; 68 nightly sites among ~400 seasonal; lakefront -> lakeview recommended.
  - The engine's "waterfront" sites (15-36..15-60) back onto the resort beach.
  - Open water is ~70-80 m away across a reedy flat.
- 9112 Silver Creek: C$40-60 confirmed; 62 nightly sites on Campspot; operator WordPress shows injected casino spam.
- 8828 Spray Lakes West: season -> 05-14..09-13; 63 sites; FCFS; operator Cedar & Spruce; lakefront -> lakeview recommended.
  - Reservoir drawdown: the agency map's "Typical Water Line" is ~100-130 m past the pads.
  - On the 2024-06-13 imagery the water is 300-400 m away.
- 12814 Spring Hill: C$70 + GST, C$1 over the gate; the Calgary metro gateway (37 km) passes it.
  - Booking by phone or contact form; the stored /reservation/ URL is only a form.
  - Google 4.1/244.

## Lessons
- ResNexus (Incapsula) blocks curl; bw.py in the headless browser reads the engine fine.
- Esri imagery dates: the World_Imagery MapServer `identify` (layers=all, f=json) returns DATE (YYYYMMDD).
  - Use it to check reservoir drawdown before calling a shore.
- For Alberta reservoir campgrounds, the agency tear sheets mark both "Typical Water Line" and "High Water Line".
