// ── Event photo functions ─────────────────────────────────────────────────
// Recompute bare-ness for a photo-grid that may have just been emptied.
// Called from every code path that removes the last photo from a grid —
// the drop handler (cross-card drag), the single-photo delete buttons,
// and the "Remove All Photos" buttons. Mirrors the Jinja `is_bare`
// predicate from initial render: bare iff no photos AND (it's a
// waypoint/family-visit OR there's no description). Stay cards
// (closest('.event-card') returns null) are never bare, but their
// "Remove All Photos" button still gets hidden when the grid empties.
// No-op when the grid still has photos.
function _maybeBarifyEmptyGrid(grid) {
  if (!grid || grid.querySelectorAll('.photo-item').length > 0) return;
  const card = grid.closest('.event-card');
  if (card) {
    const isWaypointOrFamily = card.classList.contains('waypoint')
      || card.classList.contains('family-visit');
    const hasDescription = !!card.querySelector('.event-body .event-description');
    if (isWaypointOrFamily || !hasDescription) {
      card.classList.add('bare');
    }
  }
  const section = grid.closest('.photos-section');
  const removeAllBtn = section && section.querySelector('.btn-delete-all-photos');
  if (removeAllBtn) removeAllBtn.style.display = 'none';
}

function deleteEventPhoto(tripId, eventIdx, filename, btn) {
  if (!confirm('Delete this photo?')) return;
  fetch(`/trips/${tripId}/events/${eventIdx}/photos/${filename}`, { method: 'DELETE' })
    .then(() => {
      const item = btn.closest('.photo-item');
      const grid = item.closest('.photo-grid');
      item.remove();
      _maybeBarifyEmptyGrid(grid);
    });
}

function deleteAllEventPhotos(tripId, eventIdx) {
  const grid = document.getElementById('event-photos-' + eventIdx);
  const count = grid.querySelectorAll('.photo-item').length;
  if (!count || !confirm('Delete all ' + count + ' photo' + (count !== 1 ? 's' : '') + ' from this event?')) return;
  fetch(`/trips/${tripId}/events/${eventIdx}/photos`, { method: 'DELETE' })
    .then(r => r.json())
    .then(data => {
      if (data.ok) {
        grid.innerHTML = '';
        _maybeBarifyEmptyGrid(grid);
      }
    });
}

// Upload photos for a stay or event directly from its card's header button.
// Triggers a hidden file input, uploads each file, then reloads on completion.
function uploadPhotosForItem(kind, idx) {
  if (!IS_ADMIN && !IS_UPLOADER) return;
  const url = kind === 'stay'
    ? `/trips/${TRIP_ID}/stays/${idx}/upload`
    : `/trips/${TRIP_ID}/events/${idx}/upload`;
  const input = document.createElement('input');
  input.type = 'file';
  input.multiple = true;
  input.accept = 'image/*,.zip,application/zip';
  input.style.display = 'none';
  document.body.appendChild(input);
  input.onchange = () => {
    if (!input.files || !input.files.length) {
      input.remove();
      return;
    }
    const total = input.files.length;
    let done = 0;
    const errors = [];
    Array.from(input.files).forEach(file => {
      const form = new FormData();
      form.append('photo', file);
      fetch(url, { method: 'POST', body: form })
        .then(r => r.json())
        .then(data => {
          if (data.error) errors.push(file.name + ': ' + data.error);
        })
        .catch(() => errors.push(file.name + ': upload failed'))
        .finally(() => {
          done++;
          if (done === total) {
            input.remove();
            if (errors.length) alert('Upload errors:\n' + errors.join('\n'));
            _reloadKeepingMapView();
          }
        });
    });
  };
  input.click();
}

function saveCaption(tripId, stayIdx, filename, caption) {
  fetch(`/trips/${tripId}/stays/${stayIdx}/caption`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename, caption })
  });
}

function editCaption(spanEl) {
  const textarea = spanEl.nextElementSibling;
  spanEl.style.display = 'none';
  textarea.style.display = 'block';
  textarea.focus();
}

function saveCaptionField(textarea, tripId, idx, filename, type) {
  const caption = textarea.value.trim();
  const spanEl = textarea.previousElementSibling;

  // Update the display span
  if (caption) {
    spanEl.textContent = caption;
    spanEl.classList.remove('placeholder');
  } else {
    spanEl.textContent = 'Add a caption...';
    spanEl.classList.add('placeholder');
  }
  spanEl.style.display = '';
  textarea.style.display = 'none';

  // Save to server
  const url = type === 'event'
    ? `/trips/${tripId}/events/${idx}/caption`
    : `/trips/${tripId}/stays/${idx}/caption`;
  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename, caption })
  });
}

function deletePhoto(tripId, stayIdx, filename, btn) {
  if (!confirm('Delete this photo?')) return;
  fetch(`/trips/${tripId}/stays/${stayIdx}/photos/${filename}`, { method: 'DELETE' })
    .then(() => {
      const item = btn.closest('.photo-item');
      const grid = item.closest('.photo-grid');
      item.remove();
      _maybeBarifyEmptyGrid(grid);
    });
}

function deleteAllPhotos(tripId, stayIdx) {
  const grid = document.getElementById('photos-' + stayIdx);
  const count = grid.querySelectorAll('.photo-item').length;
  if (!count || !confirm('Delete all ' + count + ' photo' + (count !== 1 ? 's' : '') + ' from this campspot?')) return;
  fetch(`/trips/${tripId}/stays/${stayIdx}/photos`, { method: 'DELETE' })
    .then(r => r.json())
    .then(data => {
      if (data.ok) {
        grid.innerHTML = '';
        _maybeBarifyEmptyGrid(grid);
      }
    });
}

// ── Photo reorder via drag and drop ─────────────────────────────────────
let dragItem = null;
let dragSourceGrid = null;
let dropTarget = null;
let dropBefore = false;

function parseGridId(grid) {
  if (grid.dataset.stayIdx != null) {
    return { type: 'stay', idx: parseInt(grid.dataset.stayIdx, 10) };
  }
  const id = grid.id;
  if (id.startsWith('event-photos-')) return { type: 'event', idx: parseInt(id.replace('event-photos-', '')) };
  // Fallback for single-copy stay grids whose ID is "photos-{idx}".
  return { type: 'stay', idx: parseInt(id.replace('photos-', '')) };
}

function saveGridOrder(grid) {
  const info = parseGridId(grid);
  // For multi-copy stays, each copy has its own grid (all share data-stay-idx).
  // Concatenate filenames across every grid for this stay in document order
  // so the whole-stay photo_order reflects the visible arrangement.
  let filenames;
  if (info.type === 'stay') {
    const grids = document.querySelectorAll(`.photo-grid[data-stay-idx="${info.idx}"]`);
    const collector = grids.length > 0 ? Array.from(grids) : [grid];
    filenames = [];
    collector.forEach(g => {
      g.querySelectorAll('.photo-item').forEach(el => filenames.push(el.dataset.filename));
    });
  } else {
    filenames = Array.from(grid.querySelectorAll('.photo-item')).map(el => el.dataset.filename);
  }
  const url = info.type === 'event'
    ? `/trips/${TRIP_ID}/events/${info.idx}/reorder`
    : `/trips/${TRIP_ID}/stays/${info.idx}/reorder`;
  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filenames })
  });
}

function initPhotoDrag(grid) {
  grid.addEventListener('dragstart', e => {
    const item = e.target.closest('.photo-item');
    if (!item || !item.draggable) return;
    dragItem = item;
    dragSourceGrid = grid;
    dropTarget = null;
    // Pin the drag image to a canvas rasterized at the on-screen thumbnail
    // size. Two reasons we don't pass the <img> (or a styled clone) directly:
    // (1) browsers snapshot <img> elements at their intrinsic resolution
    // regardless of inline width/height, so the ghost would render full-size;
    // (2) the body/source-grid class changes below would shift layout before
    // a DOM-element snapshot, leaving the ghost offset from the pointer.
    const img = item.querySelector('img');
    if (img && img.complete && img.naturalWidth && e.dataTransfer.setDragImage) {
      const r = img.getBoundingClientRect();
      const ox = Math.max(0, Math.min(r.width,  e.clientX - r.left));
      const oy = Math.max(0, Math.min(r.height, e.clientY - r.top));
      const dpr = window.devicePixelRatio || 1;
      const canvas = document.createElement('canvas');
      canvas.width = Math.round(r.width * dpr);
      canvas.height = Math.round(r.height * dpr);
      canvas.style.width = r.width + 'px';
      canvas.style.height = r.height + 'px';
      canvas.style.position = 'absolute';
      canvas.style.top = '-1000px';
      canvas.style.left = '-1000px';
      canvas.style.pointerEvents = 'none';
      const ctx = canvas.getContext('2d');
      ctx.scale(dpr, dpr);
      // Reproduce object-fit: cover by center-cropping the source rect.
      const sw = img.naturalWidth, sh = img.naturalHeight;
      const dstAR = r.width / r.height;
      const srcAR = sw / sh;
      let sx, sy, sWidth, sHeight;
      if (srcAR > dstAR) {
        sHeight = sh; sWidth = sh * dstAR;
        sx = (sw - sWidth) / 2; sy = 0;
      } else {
        sWidth = sw; sHeight = sw / dstAR;
        sx = 0; sy = (sh - sHeight) / 2;
      }
      try {
        ctx.drawImage(img, sx, sy, sWidth, sHeight, 0, 0, r.width, r.height);
        document.body.appendChild(canvas);
        e.dataTransfer.setDragImage(canvas, ox, oy);
        // Remove on next tick — by then the browser has cached the snapshot.
        setTimeout(() => canvas.remove(), 0);
      } catch (_) { /* CORS-tainted canvas — fall back to default snapshot */ }
    }
    item.classList.add('dragging');
    // Enlarge / outline empty grids on other cards so they're droppable.
    grid.classList.add('drag-source');
    document.body.classList.add('photo-dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', '');
  });

  grid.addEventListener('dragover', e => {
    if (!dragItem) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';

    const target = e.target.closest('.photo-item');
    if (target && target !== dragItem) {
      // Clear all highlights across all grids
      document.querySelectorAll('.drag-over-before,.drag-over-after').forEach(el => {
        el.classList.remove('drag-over-before', 'drag-over-after');
      });
      document.querySelectorAll('.photo-grid.drag-target').forEach(el => {
        el.classList.remove('drag-target');
      });
      const rect = target.getBoundingClientRect();
      const midX = rect.left + rect.width / 2;
      dropBefore = e.clientX < midX;
      target.classList.add(dropBefore ? 'drag-over-before' : 'drag-over-after');
      dropTarget = target;
    } else if (!target || target === dragItem) {
      // Hovering over empty area or self — show grid-level indicator if cross-grid
      if (grid !== dragSourceGrid) {
        document.querySelectorAll('.photo-grid.drag-target').forEach(el => {
          el.classList.remove('drag-target');
        });
        grid.classList.add('drag-target');
      }
      dropTarget = null;
    }
  });

  grid.addEventListener('dragleave', e => {
    const target = e.target.closest('.photo-item');
    if (target) target.classList.remove('drag-over-before', 'drag-over-after');
    // Only remove grid highlight if truly leaving the grid
    if (e.target === grid && !grid.contains(e.relatedTarget)) {
      grid.classList.remove('drag-target');
    }
  });

  grid.addEventListener('drop', e => {
    e.preventDefault();
    document.querySelectorAll('.drag-over-before,.drag-over-after').forEach(el => {
      el.classList.remove('drag-over-before', 'drag-over-after');
    });
    document.querySelectorAll('.photo-grid.drag-target').forEach(el => {
      el.classList.remove('drag-target');
    });
    if (!dragItem) return;

    const crossGrid = dragSourceGrid && dragSourceGrid !== grid;

    // Place the item in the DOM
    if (dropTarget && dropTarget !== dragItem) {
      if (dropBefore) dropTarget.before(dragItem);
      else dropTarget.after(dragItem);
    } else if (crossGrid) {
      grid.appendChild(dragItem);
    } else {
      return;  // same-grid drop on empty space, nothing to do
    }

    if (crossGrid) {
      // The destination card may have been bare (waypoint / family-visit /
      // empty event with no description), in which case its .event-body is
      // styled `display: none` and was only visible during the drag via the
      // body.photo-dragging reveal rule. Once `dragend` strips that class,
      // the body slides back to hidden and the dropped photo disappears
      // until the next page load. Promoting the card out of bare mode here
      // (and revealing the previously-hidden "Remove All Photos" button)
      // keeps the body — and the photo it now contains — on screen.
      const dstCard = grid.closest('.event-card');
      if (dstCard) dstCard.classList.remove('bare');
      const dstRemoveAll = grid.closest('.photos-section')
        && grid.closest('.photos-section').querySelector('.btn-delete-all-photos');
      if (dstRemoveAll) dstRemoveAll.style.display = '';

      // Symmetric handling for the *source*: if that was its last photo,
      // the card may need to go bare again so an empty body doesn't sit
      // below the header. Helper is no-op when the grid still has photos.
      _maybeBarifyEmptyGrid(dragSourceGrid);

      // Move file on server, then save both grid orders
      const src = parseGridId(dragSourceGrid);
      const dst = parseGridId(grid);
      const filename = dragItem.dataset.filename;
      // dragend nulls the module-level dragItem/dragSourceGrid before the
      // fetch resolves — capture locals for the async continuation.
      const movedItem = dragItem;
      const movedSourceGrid = dragSourceGrid;
      fetch(`/trips/${TRIP_ID}/move-photo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename: filename,
          src_type: src.type, src_idx: src.idx,
          dst_type: dst.type, dst_idx: dst.idx,
        })
      })
      .then(r => r.json())
      .then(data => {
        if (data.error) { alert(data.error); _reloadKeepingMapView(); return; }
        // Update filename if server renamed it to avoid collision
        if (data.filename !== filename) {
          movedItem.dataset.filename = data.filename;
        }
        // Repoint the img at the photo's new server location — the old
        // thumb/full URLs 404 once the file moves (matters if the admin
        // opens the lightbox before the next reload).
        const img = movedItem.querySelector('img');
        if (img) {
          const sub = (dst.type === 'event' ? `${TRIP_ID}/events/${dst.idx}` : `${TRIP_ID}/${dst.idx}`)
            + '/' + encodeURIComponent(data.filename);
          img.src = '/thumb/' + sub;
          img.dataset.full = '/static/uploads/' + sub;
        }
        saveGridOrder(movedSourceGrid);
        saveGridOrder(grid);
      });
    } else {
      saveGridOrder(grid);
    }
  });

  grid.addEventListener('dragend', () => {
    if (dragItem) dragItem.classList.remove('dragging');
    document.querySelectorAll('.drag-over-before,.drag-over-after').forEach(el => {
      el.classList.remove('drag-over-before', 'drag-over-after');
    });
    document.querySelectorAll('.photo-grid.drag-target').forEach(el => {
      el.classList.remove('drag-target');
    });
    document.querySelectorAll('.photo-grid.drag-source').forEach(el => {
      el.classList.remove('drag-source');
    });
    document.body.classList.remove('photo-dragging');
    dragItem = null;
    dragSourceGrid = null;
    dropTarget = null;
  });
}

if (IS_ADMIN) document.querySelectorAll('.photo-grid').forEach(initPhotoDrag);
