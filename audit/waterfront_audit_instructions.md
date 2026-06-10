# Waterfront designation audit — agent instructions

You are auditing `waterfront` designations for campgrounds in a personal campground database. Your batch file (path given in your prompt) is a JSON array of entries: `{id, name, location: "lat,lng", waterfront, ownership, website}`. The `waterfront` value describes **RV-accessible sites only** and must survive a strict evidence gate. Audit every entry and return a structured verdict for each.

## Vocabulary
- On-water values: `lakefront`, `riverfront`, `creekside`, `pond`, `bayfront`, `coastal woods`, `coastal dunes`
- View-only values: `lakeview`, `riverview`, `bayview`
- Default: `not waterfront`

## The evidence gate (follow exactly)
- **Default down.** A value stays on-water only if positive, named evidence supports it. "Couldn't confirm" always resolves DOWN (to `*view` or `not waterfront`), never up.
- **Evidence that COUNTS** (any one suffices for on-water): official per-site campground map/PDF showing pads at the shoreline; rec.gov per-site SHORELINE SITE flag; **legible satellite imagery showing RV pads within ~1 pad-depth (~15–25 m) of the waterline**; dated firsthand photo of an RV site on the water.
- **FORBIDDEN as sole basis:** marketing prose ("on the lake"); aggregator boilerplate or review snippets; brochure *overview* maps; the campground's NAME ("Lakeview"/"Creekside"); mere presence of lake access / boat ramp / marina. A marina park whose pads sit uphill is `lakeview` or `not waterfront`.
- **Satellite look is MANDATORY but ASYMMETRIC:** (a) when imagery is *legible*, it is decisive and overrides prose/brochure maps — pads visibly set back from the water → downgrade; (b) when imagery is *illegible* (dense canopy, low-res/old tiles, deep shade), it can neither confirm nor deny — "I couldn't see pads" is NOT grounds to downgrade. In that case defer to the higher authority: an **official per-site campground map** or per-site reservation data. For established agency campgrounds (state park / DNR / COE / USFS / NPS) that per-site map almost always exists and is the authority. If NO qualifying source confirms shoreline RV sites, default down.
- **`*view` needs the same rigor:** keep/assign `lakeview`/`riverview` only if RV sites plausibly have a real view of water (e.g. pads across a road from shore, on an open slope above the water, set back ~30–150 m with open line of sight). Pads behind a tree buffer or far from water → `not waterfront`.
- Waterfront cabins, tent-only areas, boat ramps, day-use beaches do NOT count — only RV-drivable sites.

## Workflow per entry
1. Parse `lat,lng` from `location`. Fetch satellite imagery (GET only; curl works):
   `curl -s "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=<lng-d>,<lat-d>,<lng+d>,<lat+d>&bboxSR=4326&size=1000,1000&format=jpg&f=image" -o /tmp/sat_<id>_a.jpg`
   with d=0.0035 (~700 m frame). Then **Read** the jpg (it renders as an image). Zoom with d=0.0012 for pad-level detail; orient with d=0.01 if lost; pan by shifting the center. Use as many frames as you need.
2. Locate the campground (loops, pads, parked RVs) and judge the pad-to-water relationship.
3. **Mis-pin handling:** if the pin clearly isn't the campground (subdivision, empty field, park HQ), find the real campground: sweep nearby frames and/or consult the official website / campground map (load WebFetch via ToolSearch if needed). If found, report `coord_fix: "lat,lng"` (4 decimals, pinned on the campground loop itself) and fetch elevation for the fixed coord: `https://api.open-meteo.com/v1/elevation?latitude=<lat>&longitude=<lng>` → report `elevation_meters`. Judge waterfront at the corrected location. If you cannot find the campground at all, say so in `evidence` and set `final` to the current value with `confidence: "low"` (do NOT guess a downgrade from a wrong pin).
4. **Canopy case:** if imagery is illegible at the campground, consult the entry's `website` URLs and official per-site campground maps (recreation.gov campground pages have per-site lists/maps; state-park sites have campground map PDFs). Decide from that authority. If nothing qualifying confirms shoreline RV sites, default down.
5. Decide `final` and write a one-line `evidence` string **naming the artifact**, e.g. `satellite at 41.2345,-89.4567: pads at waterline on east loop` / `satellite: pads ~150m from lake behind treeline` / `rec.gov site map: sites 12-15 on shore; canopy-blind satellite` / `IL DNR campground map: all loops inland`.

## Output
Do NOT edit any files in the repository. Your final message must be ONLY a JSON array (no prose, no code fences), one object per entry, same order as the batch:
```
{"id": <int>, "name": "<name>", "current": "<current value>", "final": "<final value>", "coord_fix": null | "lat,lng", "elevation_meters": null | <number>, "evidence": "<one line>", "confidence": "high" | "low"}
```
`final` may equal `current` (confirmed) or be a downgrade/correction (e.g. lakefront→lakeview, riverfront→not waterfront). Upgrades (e.g. lakeview→lakefront) are allowed only with counting evidence. Every object must have a non-empty `evidence` string.
