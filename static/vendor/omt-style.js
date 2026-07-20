// OpenMapTiles-schema paint + label rules for protomaps-leaflet.
//
// Our offline street basemap (tiles/street.pmtiles) is rendered by planetiler's
// default OpenMapTiles profile, whose layers are named `transportation`, `water`,
// `landcover`, `place`, etc. protomaps-leaflet's built-in themes ('light'/'dark')
// target the DIFFERENT *Protomaps basemap* schema (layers named `roads`, `earth`,
// `landuse`, ...), so `theme:'light'` only paints the coincidentally same-named
// `water` layer and draws NO roads — a gray-land/blue-water map. These rules map
// the OMT schema explicitly so streets actually render. Exposed as
// window.ekkoOmtStyle(P) where P === window.protomapsL.
(function () {
  function lerp(z, stops) {
    if (z <= stops[0][0]) return stops[0][1];
    for (var i = 1; i < stops.length; i++) {
      if (z <= stops[i][0]) {
        var a = stops[i - 1], b = stops[i];
        return a[1] + (b[1] - a[1]) * (z - a[0]) / (b[0] - a[0]);
      }
    }
    return stops[stops.length - 1][1];
  }
  function w(stops) { return function (z) { return lerp(z, stops); }; }
  function cls(field, vals) {
    return function (z, f) { return vals.indexOf(f.props[field]) >= 0; };
  }

  window.ekkoOmtStyle = function (P) {
    var Poly = P.PolygonSymbolizer, Line = P.LineSymbolizer,
        Text = P.CenteredTextSymbolizer, LineLabel = P.LineLabelSymbolizer;

    var major = ['motorway', 'trunk'], primary = ['primary'],
        secondary = ['secondary', 'tertiary'],
        minor = ['minor', 'service', 'unclassified', 'residential', 'living_street'],
        pathish = ['path', 'track', 'footway', 'cycleway', 'pedestrian', 'steps', 'bridleway'],
        railish = ['rail', 'transit', 'light_rail', 'subway', 'tram', 'monorail', 'funicular'];

    var mwW = [[5, 0.5], [8, 1], [11, 2], [13, 4], [15, 7], [18, 20]];
    var prW = [[7, 0.4], [10, 1], [13, 3], [15, 5], [18, 16]];
    var seW = [[9, 0.3], [12, 1.2], [14, 3], [16, 5], [18, 12]];
    var miW = [[12, 0.6], [14, 1.6], [16, 3], [18, 8]];

    var paintRules = [
      // --- land cover / parks (bottom) ---
      { dataLayer: 'landcover', symbolizer: new Poly({ fill: '#d3e3c6', opacity: 0.7 }), filter: cls('class', ['wood', 'forest']) },
      { dataLayer: 'landcover', symbolizer: new Poly({ fill: '#e3ead7', opacity: 0.7 }), filter: cls('class', ['grass', 'meadow', 'heath', 'scrub', 'farmland']) },
      { dataLayer: 'landcover', symbolizer: new Poly({ fill: '#ece6d5' }), filter: cls('class', ['sand', 'beach', 'bare_rock']) },
      { dataLayer: 'landcover', symbolizer: new Poly({ fill: '#e6eef0' }), filter: cls('class', ['ice', 'glacier']) },
      { dataLayer: 'park', symbolizer: new Poly({ fill: '#d3e6c4', opacity: 0.6 }) },
      // --- water ---
      { dataLayer: 'water', symbolizer: new Poly({ fill: '#9fc6e8' }) },
      { dataLayer: 'waterway', symbolizer: new Line({ color: '#9fc6e8', width: w([[7, 0.5], [12, 1.2], [15, 3]]) }) },
      // --- road casings (drawn before fills so fills sit on top) ---
      { dataLayer: 'transportation', minzoom: 6, filter: cls('class', major), symbolizer: new Line({ color: '#d8a24a', width: function (z) { return lerp(z, mwW) + lerp(z, [[8, 1], [14, 2], [18, 4]]); } }) },
      { dataLayer: 'transportation', minzoom: 8, filter: cls('class', primary), symbolizer: new Line({ color: '#d9b96a', width: function (z) { return lerp(z, prW) + lerp(z, [[10, 1], [14, 2], [18, 4]]); } }) },
      { dataLayer: 'transportation', minzoom: 10, filter: cls('class', secondary), symbolizer: new Line({ color: '#cfcabf', width: function (z) { return lerp(z, seW) + 1.5; } }) },
      { dataLayer: 'transportation', minzoom: 13, filter: cls('class', minor), symbolizer: new Line({ color: '#d5d0c6', width: function (z) { return lerp(z, miW) + 1.2; } }) },
      // --- road fills ---
      { dataLayer: 'transportation', minzoom: 6, filter: cls('class', major), symbolizer: new Line({ color: '#f2a860', width: w(mwW) }) },
      { dataLayer: 'transportation', minzoom: 8, filter: cls('class', primary), symbolizer: new Line({ color: '#f7cd80', width: w(prW) }) },
      { dataLayer: 'transportation', minzoom: 10, filter: cls('class', secondary), symbolizer: new Line({ color: '#ffffff', width: w(seW) }) },
      { dataLayer: 'transportation', minzoom: 13, filter: cls('class', minor), symbolizer: new Line({ color: '#ffffff', width: w(miW) }) },
      { dataLayer: 'transportation', minzoom: 13, filter: cls('class', pathish), symbolizer: new Line({ color: '#b6ac9a', dash: [2, 2], dashColor: '#b6ac9a', width: w([[13, 0.5], [16, 1.4], [18, 3]]) }) },
      { dataLayer: 'transportation', minzoom: 9, filter: cls('class', railish), symbolizer: new Line({ color: '#b0b0b8', width: w([[9, 0.5], [14, 1], [18, 2.5]]) }) },
      // --- buildings ---
      { dataLayer: 'building', minzoom: 14, symbolizer: new Poly({ fill: '#e2ddcc', stroke: '#d3cdb8', width: 0.5 }) },
      // --- admin boundaries (state/country) ---
      { dataLayer: 'boundary', filter: function (z, f) { return (+f.props.admin_level) <= 4; }, symbolizer: new Line({ color: '#9e8fb0', dash: [4, 2], dashColor: '#9e8fb0', width: 1.4 }) }
    ];

    var labelRules = [
      { dataLayer: 'transportation_name', minzoom: 12, symbolizer: new LineLabel({ labelProps: ['name'], fill: '#4a4a4a', stroke: '#ffffff', width: 2.2, font: '500 12px sans-serif' }) },
      { dataLayer: 'water_name', minzoom: 10, symbolizer: new Text({ labelProps: ['name:en', 'name'], fill: '#5a7ea6', stroke: '#ffffff', width: 2, font: 'italic 400 11px sans-serif' }) },
      { dataLayer: 'place', minzoom: 7, filter: cls('class', ['city', 'town']), symbolizer: new Text({ labelProps: ['name:en', 'name'], fill: '#333333', stroke: '#ffffff', width: 2.5, font: '600 13px sans-serif' }) },
      { dataLayer: 'place', minzoom: 12, filter: cls('class', ['village', 'suburb', 'neighbourhood', 'hamlet']), symbolizer: new Text({ labelProps: ['name:en', 'name'], fill: '#555555', stroke: '#ffffff', width: 2, font: '400 11px sans-serif' }) }
    ];

    return { paintRules: paintRules, labelRules: labelRules, backgroundColor: '#e8e6e1' };
  };
})();
