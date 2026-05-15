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

> ⚠️ **NO FLAGS** — this command takes zero arguments. Do not add `--dataset`, `--limit`, or any other flag. Adding any flag will cause an error.

**Correct vs. incorrect usage:**
```
❌ cdq get-recent-runs --dataset "samples.sales_data"   (WRONG — will error)
❌ cdq get-recent-runs --limit 10                        (WRONG — will error)
✅ cdq get-recent-runs                                   (correct)
```

**Help output (no flags exist):**
```
usage: cdq get-recent-runs [-h]

options:
  -h, --help  show this help message and exit
```

## Output

JSON array of recent runs. Key fields per run:
- `runId` — use this with `cdq get-results --run-id`
- `dataset` — logical dataset name
- `runDate` — when the job ran
- `score` / `passFail` — DQ score and pass/fail status

## Next Step

```bash
cdq get-results --dataset "MY_DATASET" --run-id "2026-05-14"
```
