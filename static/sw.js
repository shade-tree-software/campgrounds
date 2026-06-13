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
//   - Cross-origin (map tiles, unpkg leaflet) is not intercepted — the
//     map renders gray offline; the timeline and photos still work.
//   - Non-GET requests are never touched.
//
// Bump VERSION to invalidate all caches after a deploy that changes the
// app shell in incompatible ways.

const VERSION = 'v1';
const PAGE_CACHE = 'ekko-pages-' + VERSION;
const PHOTO_CACHE = 'ekko-photos-' + VERSION;
const OFFLINE_URL = '/offline';

const PAGE_CACHE_MAX = 80;     // pages + API responses + static assets
const PHOTO_CACHE_MAX = 500;   // thumbs are ~50 KB; originals only as viewed

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
