---
name: project_mn_sweep_handoff
description: "Minnesota campground sweep COMPLETE — all 4 buckets added + inclusion- & waterfront-audited (350 entries, ids 5359-5708)"
metadata: 
  node_type: memory
  type: project
  originSessionId: ec43cc73-21a2-4522-bc59-2c1b15c728da
---

**COMPLETE (2026-06-30).** Minnesota state-by-state sweep: all 4 buckets added,
inclusion-vetted at add-time, and waterfront-audited; committed + pushed. MN went
from 1 to 351 entries (350 added, ids 5359-5708). Every new entry carries BOTH
`inclusion_evidence` and `waterfront_evidence` (fully audited). By ownership:
local 134, state 93, federal 62, private 61. Waterfront: 255 not-waterfront, 42
lakefront, 32 lakeview, 11 riverview, 8 riverfront, 1 creekside, 1 bayview.

Detection via RV Life Algolia (app `H0LPZK92QJ`, key inline in any rvlife park
page HTML, index `park`, MN bbox `43.4,-97.4,49.45,-89.4` → 632 MN hits).

- **State** (5359-5451, 93): MN state parks/SRAs (67, reservable via ReserveMN —
  US eDirect: API base `https://mnrdr.usedirect.com/minnesotardr/rdr/fd/citypark`,
  frontend deep link `https://reservemn.usedirect.com/MinnesotaWeb/#!park/<PlaceId>`)
  + 26 DNR state-forest rustic FCFS campgrounds (+1 county). Skipped Afton/Crosby
  Manitou/Lake Maria (backpack), Glendalough (cart-in), Graceville Gun Club, Zumbro
  Bottoms (horse), St Croix SP dup.
- **Federal** (5452-5511, 60): Superior NF (Gunflint/Tofte/Kawishiwi/LaCroix/
  Laurentian, incl. rustic >21-ft loops kept w/ marginal notes), Chippewa NF
  (Cass Lake/Norway Beach, Lake Winnibigoshish + Cut Foot Sioux), USACE St. Paul
  Mississippi-headwaters dams (Cross/Gull/Leech/Pokegama/Sandy/Winnie). Skipped
  Knutson Dam (closed thru 2029), Cass Lake Loop (walk-in), Noma (carry-in), dups.
- **Private** (commercial, 5512-5595): gated price_level<=2 AND star>=4, membership/
  seasonal/casino-dry-lot vetted out. 60 private + 21 reclassified-local + 2 federal
  (North Star, Stony Point) + 1 state (Kruger) caught in this bucket.
- **Local** (county/city park_type + gov-name-scan of commercial; NO star/price gate,
  5596-5708, 113): county/city/township/regional + a few off-season fairgrounds.
  Deduped the 22 local-gov already added via private reclassification.

**KEY REUSABLE PLUMBING built this sweep:**
- `audit/add_research_instructions.md` — the reusable ADD-stage research subagent
  prompt (vet inclusion + pin loop + elevation + emit inclusion_evidence + capture
  waterfront lead; outputs ready-to-append JSON). Used for every bucket.
- `/tmp/append_mn.py` — appender that assigns ids, writes entries in CLAUDE.md field
  order preserving 2-space indent, html.unescapes agent `&gt;`/`&amp;`, validates
  with json.load, and stashes each entry's waterfront `lead` to `/tmp/mn_leads.json`
  keyed by id for the later audit. (Regenerate from this repo's commit if gone.)
- Per-bucket flow: research agent (SEQUENTIAL per [[feedback_sequential_sweep_agents]],
  batches of ~14-18) → append+commit → waterfront-audit subagents over the new ids
  (carry each entry's `lead` from the leads file into the batch) → apply with
  `audit/apply_waterfront_audit.py` → commit. Auto-marked the 35 inland (empty
  water_body lead) private/local entries not-waterfront WITHOUT an agent to cut load.
- **Watch:** audit agents occasionally swap id/name pairs (Big Bog/Moose Lake did)
  or garble a name — ALWAYS run the id/name-match validation before apply (norm name
  vs DB name); apply is by id so a swapped id silently mis-writes.

Also fixed unrelated **service-worker map-tile caching** (commit "cache map tiles via
CORS"): opaque no-cors tile responses were quota-padded so the tile cache never
persisted; now the SW re-fetches tiles in CORS mode. See [[feedback_waterfront_evidence_in_json]],
[[reference_inclusion_audit]], [[reference_usedirect_deep_reservation_links]],
[[reference_rvlife_price]], [[reference_local_campground_method]].
