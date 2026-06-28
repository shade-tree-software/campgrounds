// EKKO Trips service worker — offline read-only viewing.
//
// Strategy (deliberately conservative so the admin never edits stale data):
//   - Photos + thumbs (/thumb/, /static/uploads/): cache-first. They're
//     effectively immutable (thumbs are mtime-keyed server-side), big, and
//     the main thing worth having at a campsite with no signal.
//   - Everything else (pages, /static JS/CSS, API GETs): network-first.
//     Online behavior is byte-identical to no-SW; the cache is only a
//     fallback when the network is unreachable. Successful basic 200
//     responses are stashed as you browse, so "trips you've looked at
//     recently" are what's available offline.
//   - Navigations with no cached copy fall back to the /offline page.
//   - Map tiles (OSM + Esri/ArcGIS): cache-first, like photos. Tiles are
//     immutable per z/x/y, so revisited tiles come back instantly (Cache
//     API, no re-validation flash) and the map renders offline instead of
//     gray. These are cross-origin no-cors, so the responses are opaque —
//     cached specially (see tileCacheFirst). Other cross-origin (unpkg
//     leaflet) is still not intercepted.
//   - Non-GET requests are never touched.
//
// Bump VERSION to invalidate all caches after a deploy that changes the
// app shell in incompatible ways.

const VERSION = 'v1';
const PAGE_CACHE = 'ekko-pages-' + VERSION;
const PHOTO_CACHE = 'ekko-photos-' + VERSION;
const TILE_CACHE = 'ekko-tiles-' + VERSION;
const OFFLINE_URL = '/offline';

const PAGE_CACHE_MAX = 80;     // pages + API responses + static assets
const PHOTO_CACHE_MAX = 500;   // thumbs are ~50 KB; originals only as viewed
const TILE_CACHE_MAX = 1000;   // map tiles are ~10-30 KB each

// Map-tile origins served cache-first. OSM rotates a/b/c subdomains, so match
// the base host and any subdomain of it.
const TILE_HOSTS = ['tile.openstreetmap.org', 'server.arcgisonline.com'];
function isTileHost(host) {
  return TILE_HOSTS.some((h) => host === h || host.endsWith('.' + h));
}

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(PAGE_CACHE)
      .then((c) => c.add(OFFLINE_URL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys
          .filter((k) => k.startsWith('ekko-') && !k.endsWith(VERSION))
          .map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

// Drop oldest entries once a cache exceeds its cap. Cache key order is
// insertion order, so this is a rough FIFO — good enough to bound quota.
async function trimCache(name, max) {
  const cache = await caches.open(name);
  const keys = await cache.keys();
  for (let i = 0; i < keys.length - max; i++) {
    await cache.delete(keys[i]);
  }
}

// Cacheable: a plain same-origin 200 that isn't the tail of a redirect
// chain. The redirect guard matters: logged-out page fetches 302 to
// /login and caching that would make every offline page "be" the login
// screen.
function cacheable(res) {
  return res && res.status === 200 && res.type === 'basic' && !res.redirected;
}

async function cacheFirst(req) {
  const cached = await caches.match(req);
  if (cached) return cached;
  const res = await fetch(req);
  if (cacheable(res)) {
    const cache = await caches.open(PHOTO_CACHE);
    cache.put(req, res.clone());
    trimCache(PHOTO_CACHE, PHOTO_CACHE_MAX);
  }
  return res;
}

// Tiles are cross-origin and loaded by Leaflet's <img> tags without a
// crossorigin attribute, so the requests are no-cors and the responses come
// back opaque (status 0, type 'opaque'). The same-origin cacheable() check
// rejects those, so tiles get their own path that also stores opaque hits.
// An opaque error response can't be told apart from a good one; a rare broken
// tile self-heals on the next load past the FIFO trim or a VERSION bump.
async function tileCacheFirst(req) {
  const cached = await caches.match(req);
  if (cached) return cached;
  const res = await fetch(req);
  if (res && (res.status === 200 || res.type === 'opaque')) {
    const cache = await caches.open(TILE_CACHE);
    cache.put(req, res.clone());
    trimCache(TILE_CACHE, TILE_CACHE_MAX);
  }
  return res;
}

async function networkFirst(req) {
  try {
    const res = await fetch(req);
    if (cacheable(res)) {
      const cache = await caches.open(PAGE_CACHE);
      cache.put(req, res.clone());
      trimCache(PAGE_CACHE, PAGE_CACHE_MAX);
    }
    return res;
  } catch (err) {
    const cached = await caches.match(req);
    if (cached) return cached;
    if (req.mode === 'navigate') {
      const offline = await caches.match(OFFLINE_URL);
      if (offline) return offline;
    }
    throw err;
  }
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // Map tiles are cross-origin and immutable — cache-first so revisited tiles
  // are instant and the map renders offline. Handled before the same-origin
  // gate below (which would otherwise let them fall through to the network).
  if (isTileHost(url.hostname)) {
    e.respondWith(tileCacheFirst(req));
    return;
  }
  if (url.origin !== location.origin) return;
  // Session mutations, the SW itself, and the SW kill-switch stay un-cached
  // and un-served — /sw-reset must always hit the network so a wedged cache
  // can never intercept the very page meant to clear it.
  if (url.pathname === '/sw.js' || url.pathname.startsWith('/login') ||
      url.pathname.startsWith('/logout') || url.pathname === '/sw-reset') return;

  if (url.pathname.startsWith('/thumb/') || url.pathname.startsWith('/static/uploads/')) {
    e.respondWith(cacheFirst(req));
  } else {
    e.respondWith(networkFirst(req));
  }
});
