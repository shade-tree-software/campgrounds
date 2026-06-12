// Trip-detail photo lightbox: opens a fullscreen overlay over the photo
// grid, paged via prev/next buttons, arrow keys, or swipe. Touch users
// also get pinch-to-zoom, drag-to-pan while zoomed, and double-tap to
// toggle zoom. F toggles fullscreen; a download button gives mobile
// users a save path (right-click is unavailable on touch). Functions
// are kept global so inline onclick="…" attributes in the photo-grid
// HTML still resolve.

let lightboxPhotos = [];
let lightboxIndex = 0;

// ── Zoom state ───────────────────────────────────────────────────────────
// The image's transform is `translate(tx,ty) scale(s)` with the default
// center origin; tx/ty are screen px. Reset on every photo change/close.
let lbScale = 1, lbTx = 0, lbTy = 0;

function lbApplyTransform(animate) {
  const img = document.getElementById('lightbox-img');
  if (animate) {
    img.style.transition = 'transform .18s ease-out';
    setTimeout(() => { img.style.transition = ''; }, 200);
  }
  img.style.transform = (lbScale === 1 && !lbTx && !lbTy)
    ? ''
    : `translate(${lbTx}px, ${lbTy}px) scale(${lbScale})`;
}

// Keep the scaled image covering its original centered box so a pan can't
// fling it off screen. offsetWidth/Height are layout sizes — unaffected by
// the transform — so the bound is stable mid-gesture.
function lbClampPan() {
  const img = document.getElementById('lightbox-img');
  const maxX = img.offsetWidth * (lbScale - 1) / 2;
  const maxY = img.offsetHeight * (lbScale - 1) / 2;
  lbTx = Math.max(-maxX, Math.min(maxX, lbTx));
  lbTy = Math.max(-maxY, Math.min(maxY, lbTy));
}

function lbResetZoom(animate) {
  lbScale = 1; lbTx = 0; lbTy = 0;
  lbApplyTransform(animate);
}

// Double-tap zoom: in at 2.5x anchored on the tap point, or back out.
function lbToggleZoom(x, y) {
  if (lbScale > 1) { lbResetZoom(true); return; }
  const img = document.getElementById('lightbox-img');
  const r = img.getBoundingClientRect();  // scale is 1, so visual == layout
  lbScale = 2.5;
  // Anchor the tapped image point: with center origin, the point under
  // (x,y) stays put when translate = (center - tap) * (scale - 1).
  lbTx = (r.left + r.width / 2 - x) * (lbScale - 1);
  lbTy = (r.top + r.height / 2 - y) * (lbScale - 1);
  lbClampPan();
  lbApplyTransform(true);
}

function openLightbox(imgEl) {
  // Collect all photos in the same grid
  const grid = imgEl.closest('.photo-grid');
  lightboxPhotos = Array.from(grid.querySelectorAll('.photo-item img'));
  lightboxIndex = lightboxPhotos.indexOf(imgEl);
  showLightboxPhoto();
  document.getElementById('lightbox').classList.add('visible');
}

function showLightboxPhoto() {
  lbResetZoom(false);
  const img = lightboxPhotos[lightboxIndex];
  document.getElementById('lightbox-img').src = img.src;
  // Get caption from the caption-text span in the same photo-item
  const item = img.closest('.photo-item');
  const spanEl = item.querySelector('.caption-text');
  let caption = '';
  if (spanEl && !spanEl.classList.contains('placeholder')) {
    caption = spanEl.textContent;
  }
  document.getElementById('lb-caption').textContent = caption;
  // Show date (and time, when EXIF carries one) taken
  const raw = img.dataset.dateTaken || '';
  let dateStr = '';
  if (raw) {
    const [datePart, timePart] = raw.split(' ');
    const d = new Date(datePart + 'T' + (timePart || '00:00:00'));
    dateStr = d.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
    if (timePart) {
      dateStr += ' · ' + d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    }
  }
  document.getElementById('lb-date').textContent = dateStr;
  document.getElementById('lb-prev').classList.toggle('hidden', lightboxIndex === 0);
  document.getElementById('lb-next').classList.toggle('hidden', lightboxIndex === lightboxPhotos.length - 1);
}

function lightboxNav(e, dir) {
  e.stopPropagation();
  const next = lightboxIndex + dir;
  if (next >= 0 && next < lightboxPhotos.length) {
    lightboxIndex = next;
    showLightboxPhoto();
  }
}

function closeLightbox(e) {
  if (e && (e.target.classList.contains('nav-btn') || e.target.id === 'lightbox-img' || e.target.id === 'lb-caption' || e.target.id === 'lb-date')) return;
  document.getElementById('lightbox').classList.remove('visible');
  lbResetZoom(false);
}

document.addEventListener('keydown', e => {
  if (!document.getElementById('lightbox').classList.contains('visible')) return;
  if (e.key === 'Escape') closeLightbox();
  if (e.key === 'ArrowLeft') lightboxNav(e, -1);
  if (e.key === 'ArrowRight') lightboxNav(e, 1);
  if (e.key === 'f' || e.key === 'F') toggleLightboxFullscreen();
});

// Toggle browser fullscreen on the lightbox element. Browsers gate
// requestFullscreen on a user gesture — a keydown counts, so this works
// without prompting.
function toggleLightboxFullscreen() {
  const lb = document.getElementById('lightbox');
  if (document.fullscreenElement) {
    document.exitFullscreen();
  } else if (lb.requestFullscreen) {
    lb.requestFullscreen().catch(() => { /* user denied or browser refused */ });
  }
}

// Trigger a download of the current lightbox photo. The image is served
// from /static/uploads (same origin) so the anchor's `download` attr
// honors the filename hint. Stop propagation so the click doesn't also
// hit closeLightbox.
function downloadLightbox(e) {
  if (e) { e.stopPropagation(); e.preventDefault(); }
  const img = document.getElementById('lightbox-img');
  const src = img && img.src;
  if (!src) return;
  const filename = src.split('/').pop().split('?')[0] || 'photo.jpg';
  const a = document.createElement('a');
  a.href = src;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

// Touch gestures. Listen on the lightbox container so touches on the
// photo, caption, or empty backdrop all count; listeners are wired once
// at load and survive open/close cycles. One state machine covers all
// four gestures so they can't fight each other:
//   - 1 finger at scale 1  → swipe to prev/next (≥50px, mostly
//     horizontal, under 800ms — filters out jitter)
//   - 1 finger while zoomed → pan (clamped; never pages)
//   - 2 fingers             → pinch zoom (1x–4x), midpoint-anchored
//   - quick double tap      → toggle 2.5x zoom on the tapped point
// touchmove during pan/pinch preventDefaults (plus touch-action: none in
// CSS) so the browser's native page-zoom/scroll never competes.
(function() {
  const lb = document.getElementById('lightbox');
  if (!lb) return;

  const MAX_SCALE = 4;
  let mode = null;               // null | 'swipe' | 'pan' | 'pinch'
  let startX = 0, startY = 0, startT = 0;
  let startTx = 0, startTy = 0;  // translate at pan start
  let pinchStartDist = 0, pinchStartScale = 1;
  let moved = false;
  let lastTapT = 0, lastTapX = 0, lastTapY = 0;

  const dist = (a, b) => Math.hypot(b.clientX - a.clientX, b.clientY - a.clientY);

  lb.addEventListener('touchstart', e => {
    if (!lb.classList.contains('visible')) return;
    if (e.touches.length === 2) {
      mode = 'pinch';
      pinchStartDist = dist(e.touches[0], e.touches[1]);
      pinchStartScale = lbScale;
    } else if (e.touches.length === 1) {
      const t = e.touches[0];
      startX = t.clientX; startY = t.clientY; startT = Date.now();
      startTx = lbTx; startTy = lbTy;
      moved = false;
      mode = lbScale > 1 ? 'pan' : 'swipe';
    }
  }, { passive: true });

  lb.addEventListener('touchmove', e => {
    if (mode === 'pinch' && e.touches.length === 2) {
      e.preventDefault();
      const newScale = Math.min(MAX_SCALE,
        Math.max(1, pinchStartScale * dist(e.touches[0], e.touches[1]) / pinchStartDist));
      // Anchor the pinch midpoint: the image point under it must map to
      // the same screen spot after rescaling. With center origin, a
      // screen point q maps to image offset (q - C - t)/s, so the new
      // translate is t' = q - C - (q - C - t)·(s'/s). C (the layout
      // center) is the visual center minus the current translate.
      const img = document.getElementById('lightbox-img');
      const r = img.getBoundingClientRect();
      const cx = r.left + r.width / 2 - lbTx;
      const cy = r.top + r.height / 2 - lbTy;
      const mx = (e.touches[0].clientX + e.touches[1].clientX) / 2;
      const my = (e.touches[0].clientY + e.touches[1].clientY) / 2;
      lbTx = mx - cx - (mx - cx - lbTx) * (newScale / lbScale);
      lbTy = my - cy - (my - cy - lbTy) * (newScale / lbScale);
      lbScale = newScale;
      lbClampPan();
      lbApplyTransform(false);
    } else if (mode === 'pan' && e.touches.length === 1) {
      e.preventDefault();
      const t = e.touches[0];
      lbTx = startTx + (t.clientX - startX);
      lbTy = startTy + (t.clientY - startY);
      if (Math.abs(t.clientX - startX) + Math.abs(t.clientY - startY) > 6) moved = true;
      lbClampPan();
      lbApplyTransform(false);
    }
  }, { passive: false });

  lb.addEventListener('touchend', e => {
    if (!mode) return;
    if (mode === 'pinch') {
      if (e.touches.length === 1) {
        // One finger lifted — hand off to a pan with the remaining finger.
        const t = e.touches[0];
        startX = t.clientX; startY = t.clientY;
        startTx = lbTx; startTy = lbTy;
        moved = true;
        mode = 'pan';
      } else if (e.touches.length === 0) {
        if (lbScale < 1.05) lbResetZoom(false);  // snap a near-1x back to clean state
        mode = null;
      }
      return;
    }
    const t = e.changedTouches && e.changedTouches[0];
    mode = null;
    if (!t) return;
    const dx = t.clientX - startX;
    const dy = t.clientY - startY;
    const dt = Date.now() - startT;

    // Double-tap zoom toggle: two quick stationary taps. Taps on the
    // nav/close/download buttons don't count — rapid prev/next tapping
    // must never zoom.
    const onButton = e.target.closest && e.target.closest('button');
    const isTap = !moved && Math.abs(dx) < 10 && Math.abs(dy) < 10 && dt < 300;
    if (isTap && !onButton) {
      const now = Date.now();
      if (now - lastTapT < 300 &&
          Math.abs(t.clientX - lastTapX) < 30 && Math.abs(t.clientY - lastTapY) < 30) {
        lastTapT = 0;
        lbToggleZoom(t.clientX, t.clientY);
        return;
      }
      lastTapT = now; lastTapX = t.clientX; lastTapY = t.clientY;
      return;
    }
    lastTapT = 0;

    // Swipe nav — only when unzoomed, so panning never pages.
    if (lbScale === 1 && Math.abs(dx) >= 50 && Math.abs(dy) <= 80 && dt <= 800) {
      lightboxNav({ stopPropagation() {} }, dx < 0 ? 1 : -1);
    }
  }, { passive: true });
})();
