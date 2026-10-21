---
name: project-family-home-rescreen
description: "DONE 2026-10-21 - re-screened price-rejected, never-added private parks within 40 km of a family home: +22 (ids 15531-15552), 12 skips, 1 held, 3 Sun-brand parks waiting on AWH; method and lessons inside"
metadata:
  node_type: memory
  type: project
  originSessionId: 5a2365fc-fe6c-4508-9059-5f9b77057f7c
  modified: 2026-10-21T23:30:00.000Z
---

**DONE 2026-10-21.** AWH made family homes gateways ([[feedback_price_gate_proximity_exceptions]]). Every never-added private park near a family home that had been rejected on price was re-screened under the full gate, except for price.

**Result:** 34 candidates; 4 commits (5b22273e, c16b3dba, bc01c4b1, 6f2679cb), NOT pushed.
- **+22 adds**, ids 15531-15552 (FL 5, NY 1, PA 12, WI 4). Next id is 15553.
- **12 skips:**
  - Viking Village WI: seasonal only.
  - Sarasota Sunny South FL: sells lots.
  - Windward Isle FL: 55+ shareholder community.
  - Lakeside NY: ~7% nightly, an inferred count.
  - Adventure Bound Oak Creek PA: ~3.5% nightly.
  - Erie KOA PA: no rate, 2026 calendar closed. Re-quote with `koa.py erie` in 2027.
  - Sparrow Pond PA: a 3-night minimum on every 2027 date, though the operator page says holidays only. A phone call could reverse it.
  - Uncle Johns Elk Creek PA: shut down in 2026.
  - The other skips are recorded in verdicts.jsonl.
- **1 held:** Cedar Hills WI. It passes every gate but is adults-only and clothing-optional, so it's in verdicts.jsonl as decision "hold" for AWH.
- **3 Sun-brand parks were never researched:** Sun Outdoors Sarasota FL, Lake San Marino FL and Sun Retreats Lancaster County PA. They wait on AWH deciding whether the family-home gateway lifts the Sun pre-skip ([[feedback_skip_sun_koa_brands]]).

**Where it lives:** `audit/family_rescreen_2026-10-21/`. It holds:
- candidates.json and queue.json;
- instructions.md, the agent brief, reusable for any gateway re-screen;
- add_results.py: dry run by default, `--apply` writes. It refuses a duplicate name or a pin within 300 m.
- verdicts.jsonl;
- results/<slug>.json.

**Lesson: where the price-rejected parks really were.** The bulk were not in the verdicts.jsonl price skips. They were RV Life's `price_only` buckets: 4-star-and-up parks dropped at the list stage on a `$$$`+ tier alone, never researched. They sit in each `audit/<st>_private/list.json` and in `audit/pa_private/candidates.json`. Any future gateway change should scan those buckets too. Canada had nothing in range.

**Privacy:** the tracked evidence says only "within 40 km of a family home (gateways.py)". It never gives distances, names or addresses.
