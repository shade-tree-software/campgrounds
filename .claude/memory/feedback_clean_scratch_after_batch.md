---
name: feedback-clean-scratch-after-batch
description: AWH 2026-11-12 - delete each phase-7 batch's scratch (browser downloads, imagery, tools copy) right after its commit; the disk was at 98%
metadata:
  type: feedback
---

AWH 2026-11-12: "Be sure to clean up your temp files after every batch. I keep getting warnings about low disk space."
Each verifier batch folder ran 10-140 MB (imagery tiles, PDFs, browser output), and 300 of them filled the root disk to 98% (1.1 GB free).

**Why:** the session scratchpad lives on the same small root filesystem (53 GB) as everything else.

**How to apply:** once a batch is applied and committed, first copy any result JSON left in scratch (drops, held results) to `$S/kept_results/`. The notes file is already copied into `audit/verify/kit/<st>/`. Then `rm -rf $S/p3-NNN $S/p3-NNN_*` for that batch, except the latest `_para.txt`, which the next batch's lessons line is built from. Keep `post_p3-446.py`, the post-script template. Run `df -h /` now and then. Old sessions' scratch under `/tmp/claude-1000/-home-andrew-Dev-campgrounds/<session>/scratchpad/p3-*` is the same kind of debris. See [[project-phase7-verification]].
