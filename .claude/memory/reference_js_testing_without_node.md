---
name: reference-js-testing-without-node
description: This dev box has no node/deno/bun — install quickjs into the scratchpad to run the repo's pure shared JS modules against real data
metadata:
  type: reference
---

**There is no JavaScript runtime on this machine** (checked 2026-09-14: no `node`,
`nodejs`, `deno`, `bun`, `qjs`, `d8`). Check again on a new box before assuming it.

When there isn't one, the app's **pure** shared modules can still be executed —
`pip install --target <scratchpad>/jslib quickjs`, then

```python
import quickjs
ctx = quickjs.Context()
ctx.eval(open('static/campground-schema.js').read() + "\n" + wrapper_js)
run = ctx.get('run')
```

Do NOT install it into the repo venv or add it to either requirements file: it is a
test-time convenience, and `ekko_trips_requirements.txt` is a checkable claim about what
the web app can reach.

**What this is good for is real verification rather than a transliteration.** Two things
it did on the campground-schema popup work, neither of which a Python re-implementation
could honestly claim:

- Ran the **actual** `static/campground-schema.js` plus the popup functions sliced out of
  `templates/campground_map.html` (by string index, so the test runs the shipped source),
  with a stub `escapeHtml`, against **real payloads from the Flask test client** — the
  rendered HTML, end to end, no browser.
- Diffed the **old** renderer (`git show HEAD:templates/...`) against the new one across
  every distinct value-set in the live data, which is what turned "the refactor looks
  right" into "451 value-sets compared, exactly the two intended wording changes differ".

It only works for modules with no DOM and no page globals — which is an argument for
keeping shared formatters pure, not just tidy. Anything touching Leaflet or `document`
still needs a browser. Evaluating the module is also a free **syntax check**, which is
otherwise unavailable here.

See [[project-campground-schema]].
