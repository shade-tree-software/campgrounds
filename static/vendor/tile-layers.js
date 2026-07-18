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
      street: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
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
      return window.protomapsL.leafletLayer(Object.assign(
        { url: t.streetVector, theme: 'light', maxZoom: t.maxZoom,
          attribution: '&copy; OpenStreetMap contributors' }, opts));
    }
    return L.tileLayer(t.street, Object.assign(
      { attribution: '&copy; OpenStreetMap contributors',
        maxZoom: t.maxZoom, maxNativeZoom: t.maxNativeZoom }, opts));
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
