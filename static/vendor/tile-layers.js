// Shared Leaflet base-layer factory, driven by the server-decided
// window.EKKO_TILES config (online CDN vs the offline stick's local /tiles).
// One place so the map surfaces don't each hardcode OSM/Esri URLs, and so the
// online->local switch (USB standalone edition) is centralized. See
// usb/TILE-PIPELINE-DESIGN.md. Functions reference L (and protomapsL) at call
// time, so this can load before Leaflet.
(function () {
  function cfg() {
    // Fallback mirrors the server's online config, so the helper still works if
    // a page somehow renders without the injected window.EKKO_TILES.
    return window.EKKO_TILES || {
      mode: 'online',
      // No {s} sharding — see the matching comment on the server's online
      // config in ekko_trips_app.py; OSM's policy names this exact URL.
      street: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
      streetVector: null,
      satellite: [
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
        'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}',
      ],
      maxZoom: 19, maxNativeZoom: 19,
    };
  }

  // Street basemap. Online (and the raster fallback) => OSM/raster tiles. Local
  // Option A => a vector .pmtiles rendered by protomaps-leaflet, which overzooms
  // crisply to any level (no per-zoom storage). If protomaps-leaflet isn't
  // loaded yet, fall back to the raster street URL so nothing breaks.
  window.ekkoStreetLayer = function (opts) {
    var t = cfg(); opts = opts || {};
    if (t.mode === 'local' && t.streetVector && window.protomapsL) {
      // The .pmtiles uses the OpenMapTiles schema (planetiler default), NOT the
      // Protomaps basemap schema that protomapsL's built-in 'light' theme paints
      // — so we supply explicit OMT paint/label rules (see omt-style.js). Without
      // them the map draws water but no roads. Fall back to 'light' if the rule
      // builder is somehow absent, so the layer still appears.
      // maxDataZoom MUST match the .pmtiles data max zoom, else protomaps-leaflet
      // (which defaults it to 15) requests deeper tiles that don't exist and the
      // map goes BLANK above that zoom instead of overzooming. The server reads it
      // from the pmtiles header (streetVectorMaxDataZoom) so it's correct for a
      // z14 corridor or a z15 merged build alike; fall back to 14.
      var base = { url: t.streetVector, maxZoom: t.maxZoom,
                   maxDataZoom: t.streetVectorMaxDataZoom || 14,
                   attribution: '&copy; OpenStreetMap contributors' };
      try {
        if (window.ekkoOmtStyle) {
          var s = window.ekkoOmtStyle(window.protomapsL);
          base.paintRules = s.paintRules;
          base.labelRules = s.labelRules;
          base.backgroundColor = s.backgroundColor;
        } else {
          base.theme = 'light';
        }
      } catch (e) { base.theme = 'light'; }
      return window.protomapsL.leafletLayer(Object.assign(base, opts));
    }
    // Offline with no street store installed yet (the server nulls both street
    // fields when neither file exists). Show satellite imagery rather than a
    // blank grid — every caller does ekkoStreetLayer().addTo(map), so returning
    // nothing would leave a white map. Install tiles/street.pmtiles and this
    // path stops being taken automatically.
    if (!t.street) return window.ekkoSatelliteLayer(Object.assign({ baseOnly: true }, opts));
    return L.tileLayer(t.street, Object.assign(
      { attribution: '&copy; OpenStreetMap contributors',
        maxZoom: t.maxZoom, maxNativeZoom: t.maxNativeZoom }, opts));
  };

  // State/province borders, as an overlay rather than a basemap choice.
  //
  // OSM's raster style draws admin boundaries as a pale dotted line that is
  // effectively invisible at the zooms this app is used at — which matters
  // because the campground database is ORGANIZED by state, so "which state am I
  // looking at" is a question every one of these maps gets asked. The Esri
  // satellite stack already includes a boundary layer; the street basemap had no
  // equivalent, hence this.
  //
  // Drawn from a static Natural Earth extract (window.EKKO_BORDERS, set in
  // base.html) rather than from another tile provider: it is 172 KB for all of
  // the US and Canada, it costs no third-party requests, we control the styling,
  // and — the deciding factor — it works on the offline USB build, where an
  // extra tile source would not.
  //
  // Two deliberate choices in how it draws:
  //   - Its own pane at z-index 350, ABOVE the tiles but BELOW overlayPane (400)
  //     and markerPane (600). Borders are context, so nothing a border crosses —
  //     campground dot, trip route, stay marker — is ever obscured by one.
  //   - interactive: false, so a border line can never eat a marker's click.
  // The GeoJSON is fetched LAZILY on first display, so a map whose borders start
  // switched off pays nothing.
  window.ekkoBordersLayer = function (opts) {
    opts = opts || {};
    var group = L.layerGroup();
    var url = window.EKKO_BORDERS;
    if (!url) return group;   // asset not wired up: an empty layer is fine
    var started = false;
    group.on('add', function () {
      var map = group._map;
      if (map && !map.getPane('bordersPane')) {
        var pane = map.createPane('bordersPane');
        pane.style.zIndex = 350;
        pane.style.pointerEvents = 'none';
      }
      if (started) return;
      started = true;
      fetch(url).then(function (r) { return r.json(); }).then(function (geo) {
        L.geoJSON(geo, {
          pane: 'bordersPane',
          interactive: false,
          attribution: 'Borders: Natural Earth',
          style: function (f) {
            var country = f.properties && f.properties.kind === 'country';
            return {
              color: country ? '#4a148c' : '#7b1fa2',
              weight: country ? 2.5 : 1.6,
              opacity: country ? 0.75 : 0.65,
              // Dashed for state lines, solid for international ones — the
              // long-standing atlas convention, and it keeps a state line from
              // reading as a road on the street basemap.
              dashArray: country ? null : '6,4',
            };
          },
        }).addTo(group);
      }).catch(function () { /* a missing overlay must not break the map */ });
    });
    return group;
  };

  // Satellite. Online => the 3-layer Esri stack (imagery + labels + roads).
  // Local => a single baked NAIP layer (native z16, gracefully upscaled above).
  // Pass { baseOnly: true } for imagery with no label/road overlays (the tiny
  // detect-stops mini-maps). Returns a single layer when there's one URL, else
  // an L.layerGroup — both add/remove and slot into L.control.layers the same.
  window.ekkoSatelliteLayer = function (opts) {
    var t = cfg(); opts = opts || {};
    var urls = t.satellite || [];
    if (opts.baseOnly) urls = urls.slice(0, 1);
    var rest = Object.assign({}, opts); delete rest.baseOnly;
    var layers = urls.map(function (url, i) {
      return L.tileLayer(url, Object.assign(
        { attribution: i === 0 ? '&copy; Esri / USGS' : '',
          maxZoom: t.maxZoom, maxNativeZoom: t.maxNativeZoom }, rest));
    });
    return layers.length === 1 ? layers[0] : L.layerGroup(layers);
  };
})();
