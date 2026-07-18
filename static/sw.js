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
//     gray. Leaflet loads them as no-cors <img>, but caching the resulting
//     *opaque* responses was useless: browsers pad opaque cache entries to a
//     huge fixed size for quota, so the tile cache blew its quota almost
//     immediately and every cache.put silently failed — i.e. nothing stuck
//     and every tile was re-fetched from the slow public servers. Fix: the
//     SW re-requests each tile in CORS mode (both hosts send
//     Access-Control-Allow-Origin: *), so the response is a normal 200 that
//     caches without padding. See tileCacheFirst. Other cross-origin (unpkg
//     leaflet) is still not intercepted.
//   - Non-GET requests are never touched.
//
// Bump VERSION to invalidate the page/photo caches after a deploy that changes
// the app shell in incompatible ways.

const VERSION = 'v6';
const PAGE_CACHE = 'ekko-pages-' + VERSION;
const PHOTO_CACHE = 'ekko-photos-' + VERSION;
// Map tiles are immutable per z/x/y, so their cache is DELIBERATELY decoupled
// from VERSION: a routine page/UI deploy (which bumps VERSION) must NOT throw
// away tiles the user already downloaded from the slow public tile servers.
// Only bump this suffix if the tile-handling logic itself changes incompatibly.
// (Previously this was 'ekko-tiles-' + VERSION, so every VERSION bump silently
// flushed the whole tile cache and every recently-seen tile was re-fetched.)
const TILE_CACHE = 'ekko-tiles-v1';
const OFFLINE_URL = '/offline';
// Immutable vendored assets (Leaflet's JS/CSS/marker+layer images), self-hosted
// under /static/vendor/ so the map no longer depends on the unpkg CDN. Precached
// on install so the map initializes offline even before any map page is visited
// online, and served cache-first with ignoreSearch (see cacheFirstStatic) so the
// templates' ?v=<mtime> cache-buster still matches these bare precached URLs.
const VENDOR_ASSETS = [
  '/static/vendor/leaflet/leaflet.js',
  '/static/vendor/leaflet/leaflet.css',
  '/static/vendor/leaflet/images/marker-icon.png',
  '/static/vendor/leaflet/images/marker-icon-2x.png',
  '/static/vendor/leaflet/images/marker-shadow.png',
  '/static/vendor/leaflet/images/layers.png',
  '/static/vendor/leaflet/images/layers-2x.png',
];
// Caches to preserve across a VERSION bump. Anything else under the ekko-*
// prefix is stale and gets cleared on activate. TILE_CACHE is listed here (not
// matched by VERSION) precisely so app deploys don't evict immutable tiles.
const KEEP_CACHES = [PAGE_CACHE, PHOTO_CACHE, TILE_CACHE];

const PAGE_CACHE_MAX = 80;     // pages + API responses + static assets
const PHOTO_CACHE_MAX = 500;   // thumbs are ~50 KB; originals only as viewed
// Map tiles are ~10-30 KB each. The satellite view stacks THREE Esri layers
// (imagery + boundaries + transportation), so a single satellite pan can pull
// 3 tiles per cell — the cap needs real headroom to keep a working set warm.
const TILE_CACHE_MAX = 3000;   // ~30-90 MB

// Map-tile origins served cache-first. OSM rotates a/b/c subdomains, so match
// the base host and any subdomain of it.
const TILE_HOSTS = ['tile.openstreetmap.org', 'server.arcgisonline.com'];
function isTileHost(host) {
  return TILE_HOSTS.some((h) => host === h || host.endsWith('.' + h));
}

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(PAGE_CACHE)
      .then((c) => c.addAll([OFFLINE_URL, ...VENDOR_ASSETS]))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys
          .filter((k) => k.startsWith('ekko-') && !KEEP_CACHES.includes(k))
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

// Tiles are cross-origin and Leaflet requests them as no-cors <img>, so the
// page's own request yields an *opaque* response — which we must NOT cache:
// opaque entries get padded to a huge fixed size for quota, overflowing the
// cache so every put fails and nothing persists. Instead the SW issues its own
// CORS fetch (both tile hosts send Access-Control-Allow-Origin: *), giving a
// real 200 that caches at its true ~20 KB size; the CORS response is handed
// back to the no-cors <img>, which renders it fine. The put is awaited so a
// genuine quota error surfaces rather than silently dropping the tile. If the
// CORS fetch ever fails (a host without ACAO, or offline), fall back to the
// plain request so the tile still renders, just uncached.
async function tileCacheFirst(req) {
  const cache = await caches.open(TILE_CACHE);
  const cached = await cache.match(req);
  if (cached) {
    // LRU refresh: re-put the hit so it moves to the newest position. Cache
    // keys are in insertion order and trimCache evicts from the front, so
    // without this a tile you keep viewing would still be evicted as soon as
    // TILE_CACHE_MAX newer tiles loaded (pure FIFO). Fire-and-forget — the
    // response is served from `cached` regardless of whether the re-put lands.
    cache.put(req, cached.clone());
    return cached;
  }
  try {
    const res = await fetch(req.url, { mode: 'cors' });
    if (res && res.status === 200) {
      await cache.put(req, res.clone());
      trimCache(TILE_CACHE, TILE_CACHE_MAX);
    }
    return res;
  } catch (err) {
    return fetch(req);
  }
}

// Immutable vendored assets (Leaflet). Cache-first with ignoreSearch so the
// ?v=<mtime> versioned request matches the bare precached URL; on a miss (e.g.
// a ?v bump after a Leaflet upgrade), fetch and store the versioned entry too.
async function cacheFirstStatic(req) {
  const cached = await caches.match(req, { ignoreSearch: true });
  if (cached) return cached;
  const res = await fetch(req);
  if (cacheable(res)) {
    const cache = await caches.open(PAGE_CACHE);
    cache.put(req, res.clone());
  }
  return res;
}

async function networkFirst(req) {
  try {
    // For page navigations, bypass the browser HTTP cache entirely: a heuristically
    // cached HTML page (dynamic pages ship no validators) would otherwise let a
    // stale, pre-deploy page — with old inline JS — come back through fetch() and
    // get re-stored here. Static assets keep normal caching (they're ?v=-busted).
    const res = await fetch(req, req.mode === 'navigate' ? { cache: 'no-store' } : undefined);
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

  if (url.pathname.startsWith('/static/vendor/')) {
    // Immutable vendored libs (Leaflet) — cache-first, precached on install.
    e.respondWith(cacheFirstStatic(req));
  } else if (url.pathname.startsWith('/thumb/') || url.pathname.startsWith('/static/uploads/')) {
    e.respondWith(cacheFirst(req));
  } else {
    e.respondWith(networkFirst(req));
  }
});
