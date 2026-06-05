---
name: cdq-get-results
description: Retrieve DQ job results including scores and rule outcomes. Requires --dataset (logical name) and --run-id (get from cdq get-recent-runs). Use when: (1) Getting DQ score for a completed job, (2) Viewing per-rule results, (3) Checking pass/fail counts, (4) Examining finding details.
---

# CDQ Get Results

> **TL;DR:** Get the full DQ results for a completed job run. `--dataset` = logical name, `--run-id` = date from `cdq get-recent-runs`.

## Command

```bash
cdq get-results --dataset "DATASET_NAME" --run-id "YYYY-MM-DD"
```

❌ `--run-id "2026-05-14T00:00:00.000+0000"` — use the date portion only.  
✅ `--run-id "2026-05-14"`

## Done

Run the command, report the results, and stop.
