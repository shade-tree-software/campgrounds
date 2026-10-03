---
name: feedback-limit-headless-browsers
description: Run at most ONE headless Chrome/Playwright helper at a time (gm.py, rates.py, txt.py, cs.py) - parallel browsers ate too much memory/CPU
metadata:
  type: feedback
---

Run the private-gap browser helpers (gm.py, rates.py, txt.py --browser, cs.py, newbook.py) **one at a time** - no `xargs -P3`, no 4-way split of a Google lookup list. Batch many queries into a single gm.py call instead (it takes many args), and run it with `python3 -u` so a killed run keeps what it already printed.

**Why:** AWH 2026-10-03, during the MO private gap: 4 parallel gm.py + 3 rates.py browsers used too much memory and CPU on the dev box. Supersedes the GA-era "xargs -P3/-P4 works" note in [[project-private-gap]].

**How to apply:** one browser process at a time; plain `curl` fetches (no browser) are fine to parallelise lightly. Don't kill helpers with `pkill -f <pattern>` from a Bash call whose own command line contains the pattern - it kills the calling shell (exit 144).
