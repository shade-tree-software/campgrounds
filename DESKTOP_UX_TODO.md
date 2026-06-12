# UX improvement log — status

Two full passes completed (mobile-first 2026-06-12, then desktop +
cross-cutting). Latest batch, one commit each:

1. Photo upload progress banner + 3-worker pool — `78f524c`
2. Campground map opened to non-admins (nav + 5th "Camps" tab) — `429e490`
3. `alert()` → toast notifications + first success feedback — `2746424`
4. Accessibility + contrast pass (calendar/photo keyboard
   reachability, dialog semantics, focus return, placeholder/nav
   contrast) — `0eab99d`
5. Photo grid skeleton tiles + fade-in — `a36704f`

## Remaining (small, deliberate leftovers)

- `confirm()` prompts on destructive deletes were kept on purpose — a
  blocking prompt before a delete is correct UX. Revisit only if a
  styled in-page confirm is ever wanted.
- Full focus *trap* in lightbox/modals (Tab can still reach the page
  behind; Escape/close/focus-return are handled). Do if screen-reader
  use becomes real.
- Calendar touch tap-preview (first tap = tooltip) — rejected;
  single-tap-to-open is the better trade. The multi-trip chooser
  covers overlap days on touch.
