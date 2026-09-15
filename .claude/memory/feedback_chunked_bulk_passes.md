---
name: feedback-chunked-bulk-passes
description: AWH wants bulk/LLM passes built as small stoppable resumable chunks that commit as they go — never one long job that loses everything
metadata:
  type: feedback
---

For any bulk pass over the library — an LLM extraction, a re-audit, a sweep —
build it as **small chunks, run sequentially, stoppable, easy to commit**, not
as one long job.

AWH, 2026-09-15, asking for phase 3 of the campground schema: *"no huge
unstoppable tasks that lose all their data if the session limit hits. Small
chunks, sequentially, stoppable, easy to commit work."*

**Why:** a pass over 12,689 entries is hours of wall clock, and the session
running it can end at any point — the limit, a crash, a Ctrl-C. A job that
holds its results in memory until the end loses all of them; one that writes
continuously loses nothing and can be picked up by anyone, later, on another
machine.

**How to apply** — the shape `extract_fields.py` settled on, which worked:

- **Write every batch to disk before starting the next.** The batch is the unit
  of durability, so keep it small (12). With concurrency, write in WAVES — all
  requests in the wave finish, then one write — which keeps a single writer, so
  the read-modify-write needs no lock, and bounds a kill to one wave.
- **Put progress in the DATA, not a cursor file.** A per-entry record of what
  was processed (there: `note_scan`, the hash of the note that was read) means
  resuming is just running the command again, a cursor can never desync, and
  the progress travels with the repo to another host.
- **Record "looked and found nothing"**, or the empty cases are re-done and
  re-billed every run. See [[feedback-absent-is-not-unknown]].
- **Cap each run** (`--limit`) and handle SIGINT by finishing the work in
  flight, so stopping is clean rather than a kill.
- **Offer a free `--report`** so "how much is left" never costs an API call,
  and a `--dry-run` that shows what would be written.
- **Commit between runs.** Re-dumping a JSON store is fine if it round-trips
  byte-identically (check!) — then only the touched entries appear in the diff.

Related: [[project-campground-schema]], [[feedback-sequential-sweep-agents]]
(the same instinct applied to research agents: one at a time, tiny batches).
