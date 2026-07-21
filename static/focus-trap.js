/* Keyboard focus trap for the app's modal dialogs.
 *
 * Every modal already handles Escape, an explicit close button, and returning
 * focus to whatever opened it — the one remaining gap was that Tab could walk
 * out of an open dialog and into the page behind it, which strands keyboard and
 * screen-reader users on controls they can't see.
 *
 * This is deliberately DOM-driven rather than wired into each modal's
 * open/close pair: it looks up the currently-visible `[role="dialog"]` on every
 * Tab press. That means no open/close call site has to remember to activate or
 * release it, and any dialog added later is covered the moment it carries
 * role="dialog" (which it needs for screen readers anyway).
 *
 * Only Tab is intercepted. Programmatic focus moves are left alone — several
 * dialogs legitimately move focus themselves (the lightbox to its close button,
 * the add-modal to its first field), and policing those would fight them.
 */
(function () {
  'use strict';

  var FOCUSABLE = [
    'a[href]', 'area[href]',
    'button:not([disabled])',
    'input:not([disabled]):not([type="hidden"])',
    'select:not([disabled])', 'textarea:not([disabled])',
    'iframe', 'object', 'embed', 'summary',
    '[tabindex]:not([tabindex="-1"])'
  ].join(',');

  // getClientRects() is empty for anything display:none — including an ancestor
  // — which is exactly how these modals hide themselves (.visible toggling).
  function visible(el) {
    return !!(el && el.getClientRects().length);
  }

  // The dialog Tab should be confined to. Prefer the one that already holds
  // focus so a nested dialog wins over its parent; otherwise take the last in
  // DOM order, which is the most recently opened of any stacked pair.
  function activeDialog() {
    var open = [].filter.call(document.querySelectorAll('[role="dialog"]'), visible);
    if (!open.length) return null;
    var focused = document.activeElement;
    for (var i = open.length - 1; i >= 0; i--) {
      if (open[i].contains(focused)) return open[i];
    }
    return open[open.length - 1];
  }

  function focusableIn(root) {
    return [].filter.call(root.querySelectorAll(FOCUSABLE), function (el) {
      return visible(el) && el.tabIndex !== -1;
    });
  }

  // Capture phase: run before any dialog's own keydown handler can act on Tab.
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Tab' || e.altKey || e.ctrlKey || e.metaKey) return;
    var dialog = activeDialog();
    if (!dialog) return;

    var items = focusableIn(dialog);
    if (!items.length) {
      // A dialog with nothing tabbable still must not leak focus to the page.
      e.preventDefault();
      if (dialog.tabIndex < 0) dialog.tabIndex = -1;
      dialog.focus();
      return;
    }

    var first = items[0];
    var last = items[items.length - 1];
    var current = document.activeElement;

    if (!dialog.contains(current)) {
      // Focus was on the page behind (or nowhere) — pull it into the dialog.
      e.preventDefault();
      (e.shiftKey ? last : first).focus();
    } else if (e.shiftKey && current === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && current === last) {
      e.preventDefault();
      first.focus();
    }
  }, true);
})();
