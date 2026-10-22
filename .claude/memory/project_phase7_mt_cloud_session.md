---
name: project_phase7_mt_cloud_session
description: 2026-10-22 a cloud session is doing phase 7 for Montana; local sessions must skip MT and expect a campgrounds.json merge
metadata:
  type: project
---

As of 2026-10-22 a separate cloud session is running phase 7 verification on Montana (AWH). Local phase 7 work must not queue or edit MT entries until AWH says that session is done.

**Why:** two sessions editing the same entries would conflict; the cloud session is managing its side.

**How to apply:** keep queue.py batches off MT (the local run is on MI, so check the state before generating a batch once MI ends). Before any push, fetch first and merge origin/master; a campgrounds.json merge is expected and should be clean. See [[project_phase7_verification]].
