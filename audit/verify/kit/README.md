# Session kit for phase-7 verification and waterfront re-audits

The briefs and helpers the Montana run used (2026-10-22), saved so a new session can pick up where it
stopped. Scratchpad paths are per-session, so the briefs carry `__SCRATCH__` and the generators fill it in.

- `setup.sh SCRATCH` copies `helpers/` into `SCRATCH/helpers/` and creates the shared
  `SCRATCH/headless-browser.lock` the briefs tell subagents to `flock`.
- `helpers/`: `rg.py <rec.gov facility id>` (campground record + rates), `catx.py <facility id>` (per-site
  catalog summary from rec.gov's public search API), `bw.py OUTPREFIX URL...` (headless Chromium render;
  uses the cloud container's `/opt/pw-browsers/chromium-1194` if present, else `/usr/bin/google-chrome`, else Playwright's own build; adds `~/.cache/ekko-pw` to `sys.path` for the local playwright install),
  `h2t.py` (HTML to text), `rev.py` (Google Maps reviews; works on a place URL, not a search URL).
- `wf_brief.txt` + `mkwfbrief.py SCRATCH wf-mt-N` -> `SCRATCH/wf-mt-N_prompt.txt`, the waterfront re-audit
  brief. Inputs are `audit/verify/waterfront/wf-mt-N.json` (built from the Montana section of
  `audit/verify/waterfront_leads.md`, each lead plus the entry's prior evidence).
- `brief_base.txt` + `mkbrief.py SCRATCH mt-N` -> the phase-7 schema verification brief (the batch
  paragraph in mkbrief.py is Montana-specific; edit it for another state).

## Waterfront loop (one subagent at a time)

1. `python3 audit/verify/kit/mkwfbrief.py $SCRATCH wf-mt-N`
2. Launch one background general-purpose agent: "Read your brief from $SCRATCH/wf-mt-N_prompt.txt and
   follow it exactly." It writes `$SCRATCH/wf-mt-N/results.json`.
3. Review the results (upgrades need counting evidence; flags go to AWH), then
   `cp $SCRATCH/wf-mt-N/results.json audit/verify/waterfront/wf-mt-N_results.json` and
   `python3 audit/apply_waterfront_audit.py audit/verify/waterfront/wf-mt-N_results.json`.
4. Move the batch's lines out of the Montana section of `waterfront_leads.md` into a
   "Resolved <date>, Montana wf-mt-N" block (see wf-mt-1's), commit, push, report briefly.

Status 2026-10-22: wf-mt-1 applied (69492f0). wf-mt-2..wf-mt-6 (37 entries) not started.
Drawdown leads (14121, 14143, 14148, 14172, 6103) fall in wf-mt-5/6: the gate measures to the high-water
edge, so drawdown alone does not downgrade.
