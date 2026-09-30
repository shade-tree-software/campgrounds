// Day picker: show the whole trip, or one day of it (AWH 2026-09-30).
//
// The timeline is one flat column: a `.day-divider` opens each day and every
// card after it, up to the next divider, belongs to that day. That includes
// the time-column spacers, the write-up, the road-photo placeholders and the
// home card that closes the trip — so this reads days off the column in
// document order instead of tagging every element in the template, and a new
// kind of row added between two dividers belongs to its day without anyone
// remembering to tag it.
//
// Hiding is a class (`dp-out`), never the `hidden` attribute: several rules
// force cards visible (the photo-drag reveals, a shown waypoint run) and would
// beat the UA's [hidden] rule. The class's display:none is !important for
// exactly that reason.
//
// With all days showing, the picker follows the scroll and names the day in
// view, so the arrows always step from where the reader is. Picking a day
// frames it on the map (`focusTripDay` in map.js); going back to all days
// fits the whole trip again and returns to the same day in the long list.
(function () {
  const col = document.querySelector('.cards-column');
  const picker = col && col.querySelector('.day-picker');
  if (!picker) return;

  const allBtn = picker.querySelector('.dp-all');
  const step = picker.querySelector('.dp-step');
  const prevBtn = picker.querySelector('.dp-prev');
  const nextBtn = picker.querySelector('.dp-next');
  const select = picker.querySelector('.dp-select');
  const days = [...select.options].map(o => o.value);
  const dividers = new Map(days.map(d => [d, col.querySelector(`.day-divider[data-day="${d}"]`)]));

  // Which day each top-level row of the column belongs to. Rows ahead of the
  // first divider (none today) are counted as the first day's.
  function rowsByDay() {
    const out = [];
    let day = days[0];
    for (const el of col.children) {
      if (el === picker) continue;
      if (el.classList.contains('day-divider') && el.dataset.day) day = el.dataset.day;
      out.push([el, day]);
    }
    return out;
  }
  function dayOf(el) {
    // Walk up to the column's direct child, then back to the divider before it.
    while (el && el.parentElement !== col) el = el.parentElement;
    for (let n = el; n; n = n.previousElementSibling) {
      if (n.classList && n.classList.contains('day-divider') && n.dataset.day) return n.dataset.day;
    }
    return days[0];
  }

  let shown = null;          // null = all days
  let inView = days[0];      // the day the scroll is on, with all days showing
  // Scroll-following pauses briefly after the picker scrolls the page itself.
  // Going back to all days from one of the last days asks for a scroll the
  // page is too short to make (the last divider can't reach the top), and the
  // follower would then name an earlier day — "Day 14" right after leaving
  // Day 15. The day just picked is the right answer; the reader's own next
  // scroll takes over again.
  let followPausedUntil = 0;

  function headerOffset() {
    const rs = getComputedStyle(document.documentElement);
    return (parseFloat(rs.getPropertyValue('--site-top-height')) || 0)
         + (parseFloat(rs.getPropertyValue('--trip-header-height')) || 0)
         + picker.offsetHeight;
  }
  function scrollToDay(day, smooth) {
    const div = dividers.get(day);
    if (!div) return;
    const top = window.scrollY + div.getBoundingClientRect().top - headerOffset() - 8;
    followPausedUntil = performance.now() + (smooth ? 1000 : 400);
    window.scrollTo({ top: Math.max(0, top), behavior: smooth ? 'smooth' : 'auto' });
  }

  function syncControls() {
    const current = shown || inView;
    const i = days.indexOf(current);
    allBtn.setAttribute('aria-pressed', shown ? 'false' : 'true');
    step.classList.toggle('active', !!shown);
    if (select.value !== current) select.value = current;
    prevBtn.disabled = i <= 0;
    nextBtn.disabled = i >= days.length - 1;
  }

  // `opts.fit` (default true) reframes the map; `opts.scroll` (default true)
  // brings the day's divider up under the picker.
  function show(day, opts) {
    opts = opts || {};
    shown = day || null;
    col.classList.toggle('dp-single', !!shown);
    for (const [el, d] of rowsByDay()) el.classList.toggle('dp-out', !!shown && d !== shown);
    if (shown) inView = shown;
    syncControls();
    if (window.focusTripDay) window.focusTripDay(shown, { fit: opts.fit !== false });
    if (opts.scroll !== false) scrollToDay(shown || inView, false);
  }

  allBtn.addEventListener('click', () => { if (shown) show(null); });
  select.addEventListener('change', () => show(select.value));
  prevBtn.addEventListener('click', () => {
    const i = days.indexOf(shown || inView);
    if (i > 0) show(days[i - 1]);
  });
  nextBtn.addEventListener('click', () => {
    const i = days.indexOf(shown || inView);
    if (i < days.length - 1) show(days[i + 1]);
  });

  // Follow the scroll while every day is showing: the day in view is the last
  // divider that has reached the bottom of the sticky headers. At the very
  // bottom of the page the last days' dividers can never get that high, so
  // there it is the last divider on screen instead — otherwise a reader who
  // scrolls to the end of the trip would be told they're still a day or two
  // short of it.
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (shown || ticking || performance.now() < followPausedUntil) return;
    ticking = true;
    requestAnimationFrame(() => {
      ticking = false;
      const atBottom = window.innerHeight + window.scrollY
        >= document.documentElement.scrollHeight - 2;
      const line = atBottom ? window.innerHeight - 24 : headerOffset() + 24;
      let day = days[0];
      for (const d of days) {
        const div = dividers.get(d);
        if (div && div.getBoundingClientRect().top <= line) day = d;
      }
      if (day !== inView) { inView = day; syncControls(); }
    });
  }, { passive: true });

  // A marker click (scrollToCard) on a card of another day switches to it. The
  // map is left alone — the reader is looking at it — and scrollToCard does
  // its own scrolling to the card.
  window.tripDays = {
    showDayOf(el) { show(dayOf(el), { fit: false, scroll: false }); },
    current() { return shown; },
  };

  // Keep the day across the page's own save-and-reload (`_reloadKeepingMapView`
  // sets the flag), exactly as the map keeps its view: an admin fixing a card
  // on Day 6 lands back on Day 6. A manual reload or arriving from another
  // page starts on the whole trip. The map restores its own view, so this
  // doesn't reframe it, and the browser restores the scroll position.
  const KEY = `tripDay:${TRIP_ID}`;
  window.addEventListener('beforeunload', () => {
    try { sessionStorage.setItem(KEY, shown || ''); } catch (_) {}
  });
  let restore = null;
  try {
    const keep = sessionStorage.getItem('tripDayKeep');
    sessionStorage.removeItem('tripDayKeep');
    if (keep) restore = sessionStorage.getItem(KEY) || null;
  } catch (_) {}
  if (restore && days.includes(restore)) show(restore, { fit: false, scroll: false });
  else syncControls();
})();
