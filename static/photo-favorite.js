// Shared photo "favorite" marking — the star that makes a photo eligible for
// the poster's big 2×2 hero cells.
//
// There is no heuristic for "is this a good photo", so the poster deals its
// heroes from a hand-marked set and this is where the marking happens. The
// cost is deliberately small: a sheet needs a couple of dozen good photos, not
// a rating on every one.
//
// A photo's identity here is its storage key — "{trip_id}/{stay_idx}/{file}"
// or "{trip_id}/events/{event_idx}/{file}" — which is exactly the subpath
// every photo URL already carries. So any surface can derive it from a src
// without knowing whether it's showing a stay photo or an event photo, and one
// endpoint serves all of them.
//
// A page opts in by loading this file, rendering data-photo-key +
// data-favorite on its photo <img>s, and setting window.PHOTO_FAVORITES to
// whether this viewer may mark (i.e. is_admin — the API accepts nothing less).
// The lightbox's star (lightbox.js) reads the same attributes, so opting in
// gets the mark on both surfaces and syncPhotoFavorite() keeps them in step.

// /photo/42/0/img.jpg, /thumb/42/events/1/img.jpg and /view/... all carry the
// same key after the prefix.
function photoKeyFromSrc(src) {
  const m = /\/(?:photo|thumb|view)\/(.+)$/.exec(src || '');
  return m ? decodeURI(m[1].split('?')[0]) : '';
}

function photoKeyOf(img) {
  if (!img) return '';
  return img.dataset.photoKey ||
         photoKeyFromSrc(img.dataset.full || img.dataset.view || img.src);
}

// Push a state onto every element on the page that names this photo — the grid
// tile's img, its star button, and the lightbox's star if it's open — so the
// surfaces can't drift apart. Buttons additionally carry the pressed state.
function syncPhotoFavorite(key, on) {
  document.querySelectorAll('[data-photo-key]').forEach(el => {
    if (el.dataset.photoKey !== key) return;
    el.dataset.favorite = on ? '1' : '0';
    if (el.tagName === 'BUTTON') {
      el.setAttribute('aria-pressed', on ? 'true' : 'false');
      el.title = on ? 'Remove from poster favorites' : 'Mark as a poster favorite';
    }
  });
}

function setPhotoFavorite(key, on) {
  if (!key) return Promise.resolve(false);
  // Optimistic: a star has to answer the click instantly, and the only thing
  // riding on it is which photos the poster prefers. A failure rolls back and
  // says so rather than leaving a lie on screen.
  syncPhotoFavorite(key, on);
  return fetch('/api/photos/favorite', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ photo: key, favorite: on }),
  })
    .then(r => (r.ok ? r.json() : Promise.reject(r)))
    .then(d => { syncPhotoFavorite(key, !!d.favorite); return !!d.favorite; })
    .catch(() => {
      syncPhotoFavorite(key, !on);
      if (window.toast) window.toast("Couldn't save that favorite", 'error');
      return !on;
    });
}

// Delegated so grids rendered after load (a photo upload splices in tiles)
// need no rewiring. stopPropagation keeps the click off the img underneath,
// which would otherwise open the lightbox.
document.addEventListener('click', e => {
  const btn = e.target.closest && e.target.closest('.fav-btn');
  if (!btn) return;
  e.preventDefault();
  e.stopPropagation();
  setPhotoFavorite(btn.dataset.photoKey, btn.getAttribute('aria-pressed') !== 'true');
});
