---
name: cdq-get-recent-runs
description: Get recent DQ job run IDs and timestamps. Takes NO arguments — do not add --dataset, --limit, or any other flag. Use when: (1) Finding run IDs for retrieving results, (2) Getting timestamps for recent job executions, (3) Identifying which dates have job data.
---

# CDQ Get Recent Runs

> **TL;DR:** Get run IDs for recently completed jobs. Use these IDs with `cdq get-results`.

## Command

```bash
cdq get-recent-runs
```

⚠️ **NO FLAGS** — adding any flag (`--dataset`, `--limit`, etc.) will cause an error.

## Done

Run the command, report the results, and stop. If the user needs to see results for a specific run, suggest `cdq get-results --dataset "NAME" --run-id "YYYY-MM-DD"`.
