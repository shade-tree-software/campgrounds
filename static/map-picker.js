/**
 * Shared map picker popup — used by campground manage and event location picker.
 *
 * Usage:
 *   const picker = createMapPicker({
 *     containerId: 'my-map-container',
 *     mapId:       'my-map',
 *     headerId:    'my-map-header',
 *     searchId:    'my-search-input',
 *     resultsId:   'my-search-results',
 *     defaultView: [38.93, -77.37],
 *     onPick:      function(lat, lng) { ... }
 *   });
 *
 *   picker.show(existingLocation);   // "lat,lng" string or falsy
 *   picker.hide();
 */

function createMapPicker(opts) {
  const container = document.getElementById(opts.containerId);
  let map = null;
  let marker = null;
  const allMarkers = [];

  function clearAllMarkers() {
    if (!map) return;
    while (allMarkers.length) {
      map.removeLayer(allMarkers.pop());
    }
    marker = null;
  }

  // ── Map init ──────────────────────────────────────────────────────────
  function initMap() {
    if (map) return;
    map = L.map(opts.mapId).setView(opts.defaultView || [38.93, -77.37], 7);
    const streets = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 18,
    }).addTo(map);
    const satellite = L.layerGroup([
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: '&copy; Esri', maxZoom: 19,
      }),
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 19,
      }),
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 19,
      }),
    ]);
    L.control.layers({ 'Map': streets, 'Satellite': satellite }).addTo(map);

    map.on('click', function(e) {
      placeMarker(e.latlng.lat, e.latlng.lng);
      if (opts.onPick) opts.onPick(e.latlng.lat, e.latlng.lng);
    });
  }

  function placeMarker(lat, lng) {
    clearAllMarkers();
    marker = L.marker([lat, lng]).addTo(map);
    allMarkers.push(marker);
  }

  // ── Show / hide ──────��────────────────────────────────────────────────
  function show(location) {
    container.style.display = 'flex';
    initMap();
    setTimeout(() => map.invalidateSize(), 100);

    // Reset: clear any markers left from a previous open and dismiss search results
    clearAllMarkers();
    const results = opts.resultsId ? document.getElementById(opts.resultsId) : null;
    if (results) results.classList.remove('open');
    const searchInput = opts.searchId ? document.getElementById(opts.searchId) : null;
    if (searchInput) searchInput.value = '';

    if (location) {
      const parts = location.split(',');
      const lat = parseFloat(parts[0]);
      const lng = parseFloat(parts[1]);
      if (!isNaN(lat) && !isNaN(lng)) {
        map.setView([lat, lng], 12);
        placeMarker(lat, lng);
        return;
      }
    }
    map.setView(opts.defaultView || [38.93, -77.37], 7);
  }

  function hide() {
    container.style.display = 'none';
  }

  function panTo(lat, lng) {
    if (!map) return;
    map.setView([lat, lng], 12);
    placeMarker(lat, lng);
  }

  // ── Drag to reposition ──────��─────────────────────────────────────────
  (function() {
    const header = document.getElementById(opts.headerId);
    if (!header) return;
    let dragging = false, startX, startY, startLeft, startTop;

    header.addEventListener('mousedown', function(e) {
      if (e.target.closest('.map-picker-close')) return;
      dragging = true;
      const rect = container.getBoundingClientRect();
      startX = e.clientX;
      startY = e.clientY;
      startLeft = rect.left;
      startTop = rect.top;
      container.style.left = startLeft + 'px';
      container.style.right = 'auto';
      container.style.top = startTop + 'px';
      e.preventDefault();
    });

    document.addEventListener('mousemove', function(e) {
      if (!dragging) return;
      container.style.left = (startLeft + e.clientX - startX) + 'px';
      container.style.top = (startTop + e.clientY - startY) + 'px';
      e.preventDefault();
    });

    document.addEventListener('mouseup', function() {
      dragging = false;
    });
  })();

  // ── Resize handles ───────��────────────────────────────��───────────────
  (function() {
    const handles = container.querySelectorAll('.resize-handle');
    const MIN_W = 280, MIN_H = 250;

    handles.forEach(function(handle) {
      handle.addEventListener('mousedown', function(e) {
        e.preventDefault();
        e.stopPropagation();
        const dir = handle.dataset.dir;
        const startX = e.clientX, startY = e.clientY;
        const rect = container.getBoundingClientRect();
        const startW = rect.width, startH = rect.height;
        const startL = rect.left;

        container.style.left = startL + 'px';
        container.style.right = 'auto';
        container.style.top = rect.top + 'px';

        function onMove(ev) {
          const dx = ev.clientX - startX;
          const dy = ev.clientY - startY;
          let newW = startW, newH = startH, newL = startL;

          if (dir === 'right' || dir === 'br') newW = Math.max(MIN_W, startW + dx);
          if (dir === 'bottom' || dir === 'br' || dir === 'bl') newH = Math.max(MIN_H, startH + dy);
          if (dir === 'left' || dir === 'bl') {
            newW = Math.max(MIN_W, startW - dx);
            if (newW > MIN_W) newL = startL + dx;
          }

          container.style.width = newW + 'px';
          container.style.height = newH + 'px';
          container.style.left = newL + 'px';
          if (map) map.invalidateSize();
        }

        function onUp() {
          document.removeEventListener('mousemove', onMove);
          document.removeEventListener('mouseup', onUp);
        }

        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
      });
    });
  })();

  // ── Current-location button ──────────────────────────────────────────
  // Inject a "use my location" button into the .geo-search row (if present).
  (function() {
    const input = document.getElementById(opts.searchId);
    if (!input) return;
    const row = input.closest('.geo-search');
    if (!row || row.querySelector('.geo-locate')) return;

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'geo-locate';
    btn.title = 'Use my current location';
    btn.setAttribute('aria-label', 'Use my current location');
    btn.textContent = '\u{1F4CD}';
    row.insertBefore(btn, input.nextSibling);

    btn.addEventListener('click', function() {
      if (!navigator.geolocation) {
        alert('Geolocation is not supported by this browser.');
        return;
      }
      btn.disabled = true;
      const prev = btn.textContent;
      btn.textContent = '⏳';
      navigator.geolocation.getCurrentPosition(function(pos) {
        btn.disabled = false;
        btn.textContent = prev;
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        if (map) {
          map.setView([lat, lng], 17);
          placeMarker(lat, lng);
        }
        if (opts.onPick) opts.onPick(lat, lng);
      }, function(err) {
        btn.disabled = false;
        btn.textContent = prev;
        alert('Could not get your location: ' + (err.message || 'permission denied'));
      }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 });
    });
  })();

  // ── Geocode search ────────────────────────────────────────────────────
  (function() {
    const input = document.getElementById(opts.searchId);
    const results = document.getElementById(opts.resultsId);
    if (!input || !results) return;
    let debounceTimer = null;

    function escHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }

    input.addEventListener('input', function() {
      clearTimeout(debounceTimer);
      const q = input.value.trim();
      if (q.length < 2) { results.classList.remove('open'); return; }
      debounceTimer = setTimeout(function() {
        fetch('/api/geocode?q=' + encodeURIComponent(q))
          .then(function(r) { return r.json(); })
          .then(function(data) {
            if (data.length === 0) { results.classList.remove('open'); return; }
            results.innerHTML = data.map(function(r) {
              return '<div class="geo-option" data-lat="' + r.lat + '" data-lng="' + r.lon + '">' + escHtml(r.name) + '</div>';
            }).join('');
            results.classList.add('open');
          })
          .catch(function() { results.classList.remove('open'); });
      }, 300);
    });

    results.addEventListener('click', function(e) {
      const opt = e.target.closest('.geo-option');
      if (!opt) return;
      const lat = parseFloat(opt.dataset.lat);
      const lng = parseFloat(opt.dataset.lng);
      results.classList.remove('open');
      input.value = '';
      if (map) {
        map.setView([lat, lng], 16);
        placeMarker(lat, lng);
      }
    });

    input.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') results.classList.remove('open');
    });

    document.addEventListener('click', function(e) {
      if (!e.target.closest('.geo-search')) results.classList.remove('open');
    });
  })();

  return { show: show, hide: hide, panTo: panTo };
}
