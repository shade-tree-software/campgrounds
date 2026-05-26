// Trip-detail photo lightbox: opens a fullscreen overlay over the photo
// grid, paged via prev/next buttons, arrow keys, or swipe. F toggles
// fullscreen; a download button gives mobile users a save path
// (right-click is unavailable on touch). Functions are kept global so
// inline onclick="…" attributes in the photo-grid HTML still resolve.

let lightboxPhotos = [];
let lightboxIndex = 0;

function openLightbox(imgEl) {
  // Collect all photos in the same grid
  const grid = imgEl.closest('.photo-grid');
  lightboxPhotos = Array.from(grid.querySelectorAll('.photo-item img'));
  lightboxIndex = lightboxPhotos.indexOf(imgEl);
  showLightboxPhoto();
  document.getElementById('lightbox').classList.add('visible');
}

function showLightboxPhoto() {
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
}

document.addEventListener('keydown', e => {
  if (!document.getElementById('lightbox').classList.contains('visible')) return;
  if (e.key === 'Escape') document.getElementById('lightbox').classList.remove('visible');
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

// Swipe-to-navigate on mobile. Listen on the lightbox container so
// touches on the photo, caption, or empty backdrop all count. Threshold
// of 50px / max-vertical 80px filters out scroll/jitter. The lightbox
// element exists in the DOM at page load; this IIFE wires up the
// listeners once and they survive open/close cycles.
(function() {
  let startX = null, startY = null, startT = 0;
  const lb = document.getElementById('lightbox');
  if (!lb) return;
  lb.addEventListener('touchstart', e => {
    if (e.touches.length !== 1) { startX = null; return; }
    const t = e.touches[0];
    startX = t.clientX; startY = t.clientY; startT = Date.now();
  }, { passive: true });
  lb.addEventListener('touchend', e => {
    if (startX == null) return;
    const t = (e.changedTouches && e.changedTouches[0]);
    if (!t) { startX = null; return; }
    const dx = t.clientX - startX;
    const dy = t.clientY - startY;
    const dt = Date.now() - startT;
    startX = null;
    // Horizontal swipe: ≥ 50 px and mostly horizontal and under 800 ms.
    if (Math.abs(dx) >= 50 && Math.abs(dy) <= 80 && dt <= 800) {
      lightboxNav({ stopPropagation() {} }, dx < 0 ? 1 : -1);
    }
  }, { passive: true });
})();
