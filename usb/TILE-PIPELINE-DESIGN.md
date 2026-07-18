# Offline Map-Tile Pipeline — Design (EKKO USB standalone edition)

Status: **DESIGN** (2026-07-18). Leaflet-local bundling is already DONE (commit
`f3a4d77`). This document specifies the remaining offline-maps work: serving map
tiles from the stick with no internet, using only free + legally-redistributable
sources. Nothing here is built yet.

## Goal & constraints

- The stick's local Flask must render maps with **no internet**: both the **street**
  basemap and the **satellite** layer.
- **Legal only.** Do NOT bulk-scrape OSM's public tile CDN or Esri's ArcGIS tiles —
  both forbid it. Street tiles are **self-rendered from free OSM extracts** (ODbL);
  satellite comes from **USGS/USDA NAIP public-domain aerial imagery**.
- **Stick-only + gitignored.** Tiles must NEVER be committed or reach PythonAnywhere.
  PA keeps using the live OSM/Esri CDNs. The only code that ships to PA is a small,
  **inert-unless-a-local-store-exists** Flask route + a tile-source switch that
  resolves to the CDN URLs online. Online behavior is byte-for-byte unchanged.

## Current tile usage (what the switch must replace)

Six places hardcode tile-layer URLs today (street = OSM `{s}.tile.openstreetmap.org
/{z}/{x}/{y}.png`; satellite = Esri `World_Imagery` + `World_Boundaries_and_Places`
+ `World_Transportation`, all `/{z}/{y}/{x}`):

| File | Layers |
|------|--------|
| `static/trip-detail/map.js` | street + 3 Esri |
| `static/trip-detail/detect-stops.js` | Esri imagery only (mini-map) |
| `static/map-picker.js` | street + 3 Esri |
| `templates/campground_map.html` | street + 3 Esri |
| `templates/trips_map.html` | street + 3 Esri |
| `templates/trips_poster.html` | street only |

The six copies are near-identical — the switch is also a good opportunity to
de-duplicate them into one shared helper.

## Architecture

### 1. One shared tile-source switch (server-decided)

Add `_tile_config()` in `ekko_trips_app.py`, exposed to every template via a context
processor and to JS via a page global:

```python
LOCAL_TILE_DIR = os.path.join(BASE_DIR, "tiles")   # holds *.mbtiles / *.pmtiles

def _tile_config():
    local = bool(os.environ.get("EKKO_LOCAL_TILES")) and os.path.isdir(LOCAL_TILE_DIR)
    if local:
        return {
          "mode": "local",
          "street":    "/tiles/street/{z}/{x}/{y}.png",     # or a pmtiles:// URL (Option A)
          "satellite": ["/tiles/sat/{z}/{x}/{y}.jpg"],       # single baked layer
          "maxZoom": 16,
        }
    return {
      "mode": "online",
      "street": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      "satellite": [ESRI_IMAGERY, ESRI_BOUNDARIES, ESRI_TRANSPORT],
      "maxZoom": 19,
    }
```

- Context processor: `@app.context_processor def inject_tiles(): return {"tile_config": _tile_config()}`.
- `base.html` (and standalone `trips_poster.html`) emit once in `<head>`:
  `<script>window.EKKO_TILES = {{ tile_config|tojson }};</script>`.
- `START-EKKO.sh` gains `export EKKO_LOCAL_TILES=1`. On PA the var is unset → `online`
  branch → identical to today. The gate also requires the dir to exist, so even a
  stray env var can't break a store-less host.

### 2. Shared base-layer helper (kills the 6 copies)

New `static/vendor/tile-layers.js` (loaded on every map page), reading `window.EKKO_TILES`:

```js
function ekkoStreetLayer(opts)   { return L.tileLayer(window.EKKO_TILES.street, {maxZoom: window.EKKO_TILES.maxZoom, ...opts}); }
function ekkoSatelliteLayer(opts){ return L.layerGroup(window.EKKO_TILES.satellite.map(u => L.tileLayer(u, {maxZoom: window.EKKO_TILES.maxZoom, ...opts}))); }
```

Refactor the six sites to call these instead of hardcoding. (Online, satellite is the
3-layer Esri stack; local, it's the single baked NAIP layer — the helper hides that.)

### 3. `/tiles/<layer>/<z>/<x>/<y>.<ext>` Flask route (inert online)

```python
@app.route("/tiles/<layer>/<int:z>/<int:x>/<int:y>.<ext>")
def serve_tile(layer, z, x, y, ext):
    store = _tile_store(layer)          # None if the .mbtiles isn't present
    if store is None: abort(404)         # <-- inert: no local store => 404, PA unaffected
    flipped = (1 << z) - 1 - y           # MBTiles is TMS (y flipped) vs Leaflet XYZ
    row = store.execute(
        "SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?",
        (z, x, flipped)).fetchone()
    if not row: abort(404)               # blank tile at edges; Leaflet tolerates it
    mime = "image/png" if ext == "png" else "image/jpeg"
    return Response(row[0], mimetype=mime, headers={"Cache-Control": "public, max-age=31536000"})
```

- Login-exempt like `/sw.js` (a map tile behind auth would 302 to /login).
- Registered always; **inert without the store** so it's safe on PA.

### 4. Storage format: MBTiles (one sqlite file per raster layer)

`tiles/satellite.mbtiles` (+ `tiles/street.mbtiles` for the raster street option).
MBTiles is the standard, compact single-file z/x/y store (beats millions of loose
files on flash). `tiles/` is gitignored.

## Tile generation

New `usb/build-tiles.py` (+ thin `fetch-tiles.sh` wrapper). Two independent layers:

### Satellite — USGS/USDA NAIP (public domain) — EASY, do first

- Source: USGS **`USGSImageryOnly`** service, public-domain NAIP aerial over CONUS:
  `https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}`
  (a US-government public service; public-domain imagery — legal to download a bounded
  corridor, unlike Esri). Max native ~z16 (NAIP ~1 m). Be polite: rate-limit, only-missing.
- Pipeline: compute the corridor tile set (below) → GET each tile → write JPEG into
  `satellite.mbtiles` (TMS row). Incremental (skip present). ~4 GB for the full corridor.

### Street — self-render from OSM (ODbL) — pick ONE

**Option A — vector `.pmtiles` + client-side render (RECOMMENDED).**
- Build one `street.pmtiles` vector basemap from a Geofabrik `.osm.pbf` extract
  (state/region granularity) with `tilemaker` (single binary, no database) or the
  Protomaps build flow. Render it in Leaflet via the `protomaps-leaflet` plugin
  (bundled locally under `static/vendor/`) with a bundled JSON style.
- Pros: **much smaller** (a whole state's vector basemap is a few hundred MB vs ~4 GB
  raster), crisp at every zoom (no pre-rasterized corridor), trivial to extend for new
  trips (rebuild/append the vector file, no per-tile re-render). Serve the single file
  via a `/tiles/street.pmtiles` range-request route (pmtiles does HTTP range reads) or
  read locally.
- Cons: adds a vector-render JS lib + a style; street becomes a vector layer while
  satellite stays raster (the shared helper hides this). Toolchain = one `tilemaker` binary.

**Option B — raster self-render.**
- `osm2pgsql` → PostGIS → Mapnik + `openstreetmap-carto` → render z0–16 corridor PNGs →
  `street.mbtiles`. Pros: uniform raster, zero frontend change. Cons: heavy toolchain
  (Postgres + Mapnik + carto), ~4 GB, must re-render when new trips add new areas.

**Recommendation: Option A.** Smaller, sharper, far easier to regenerate for new trips;
the only real cost is bundling `protomaps-leaflet` + a style, isolated to the base-layer
helper. Fall back to B only if we want to avoid any vector-render dependency.

### Corridor computation (shared by both layers)

`build-tiles.py` reads `trip_data/trips.json` (cached GPS anchors/track points),
`campgrounds.json` (every pinned coord), and `home.json`; unions their areas; buffers
each by ±1 tile; enumerates z0–16. Measured earlier from the 92 cached tracks (102,032
pts / 55,653 km): **±1 buffer ≈ 198k tiles ≈ ~4 GB per raster layer**; tight/no-buffer
≈ 51k ≈ ~1 GB. This set drives the NAIP fetch (and the Option-B raster render). For the
Option-A vector basemap the corridor only picks which Geofabrik extracts to include.

## Sizing on the 64 GB card

base app 0.55 + photos ~8 (when restored) + satellite NAIP ~4 + street (~0.5–1 vector /
~4 raster) ≈ **~13–17 GB** → comfortable headroom on 56 GB free.

## Integration checklist (when built)

- [ ] `ekko_trips_app.py`: `LOCAL_TILE_DIR`, `_tile_config()`, context processor,
      `/tiles/...` route (login-exempt, inert w/o store), MBTiles reader helper.
- [ ] `base.html` + `trips_poster.html`: inject `window.EKKO_TILES`.
- [ ] `static/vendor/tile-layers.js`: `ekkoStreetLayer()` / `ekkoSatelliteLayer()`; load on all map pages.
- [ ] Refactor the 6 tile sites to the helper.
- [ ] `START-EKKO.sh`: `export EKKO_LOCAL_TILES=1`.
- [ ] `usb/build-tiles.py` + `fetch-tiles.sh`: corridor calc → NAIP fetch → street basemap → MBTiles/pmtiles.
- [ ] `.gitignore`: `tiles/`, `*.mbtiles`, `*.pmtiles`.
- [ ] Option A only: bundle `protomaps-leaflet` + style under `static/vendor/`.
- [ ] Verify PA untouched: with `EKKO_LOCAL_TILES` unset, every page still emits CDN URLs and `/tiles/*` → 404.

## Open decisions for the owner

1. **Street layer: Option A (vector pmtiles, recommended) or B (raster)?** Drives whether
   we add a small vector-render JS lib.
2. **NAIP download etiquette / volume** — confirm we're comfortable pulling ~198k
   public-domain USGS tiles for the corridor (rate-limited, only-missing). Tighten to the
   no-buffer ~51k set (~1 GB) if we want it leaner.
3. **Zoom ceiling** — z16 (NAIP native) offline vs z19 online. Fine for trip overviews;
   detect-stops mini-maps lose a little close-in detail offline.
