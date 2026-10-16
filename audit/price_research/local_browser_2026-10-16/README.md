# Browser pass over unpriced local campgrounds (2026-10-16)

The operators' own pages for 1,147 unpriced local entries (`ids.json`, every one with a website), read in the
driver browser (`audit/private_gap_browser/drv.py`; one browser at a time).

- `tools/bcrawl.py ids.json browser.jsonl`: resumable crawl. Visits each entry's home page plus up to 3 rate/fee
  links and keeps the `$` lines (`WAIT=15000` for slow or captcha'd sites). Never run `drv.py` by hand while it
  runs, because they share one page.
- `tools/bst.py browser.jsonl ST`: view one state's captured lines.
- `tools/bmk.py st USD|CAD rows.txt`: writes `build_st.py` from rows `(id, low, high, resfee, KEY-or-URL, note)`.
  KEY must occur in a captured page; a URL key is for pages read after the crawl.
  Then `python3 -I build_st.py > findings_st.json` and `../apply.py findings_st.json --apply`.
- `tools/dp.sh URL [grep]`: one driver page, its `$` lines and fee links (follow-ups).

Result: 124 priced from the crawl and 24 in follow-ups (`build_ca3/co3/ia3.py`). The unpriceable ones and why
they stay unpriced are in `.claude/memory/project_remaining_work_map.md`.
