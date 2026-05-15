---
name: cdq-get-results
description: Retrieve DQ job results including scores and rule outcomes. Requires --dataset (logical name) and --run-id (get from cdq get-recent-runs). Use when: (1) Getting DQ score for a completed job, (2) Viewing per-rule results, (3) Checking pass/fail counts, (4) Examining finding details.
---

# CDQ Get Results

> **TL;DR:** Get the full DQ results for a completed job run.
>
> `--dataset` takes the **logical dataset name**. Get `--run-id` from `cdq get-recent-runs`. See [lib/NAMING.md](../lib/NAMING.md).

## Command

```bash
cdq get-results --dataset "DATASET_NAME" --run-id "YYYY-MM-DD"
```

**Help output:**
```
usage: cdq get-results [-h] --dataset DATASET --run-id RUN_ID

options:
  -h, --help         show this help message and exit
  --dataset DATASET  Dataset name
  --run-id RUN_ID    Run ID
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `--dataset` | **Logical dataset name** registered in CDQ |
| `--run-id` | Run ID from `cdq get-recent-runs` (date like `2026-05-14`) |

**Correct vs. incorrect usage:**
```
❌ cdq get-results --dataset "MY_DATASET"                           (WRONG — missing --run-id)
❌ cdq get-results --dataset "MY_DATASET" --run-id "2026-05-14T00:00:00.000+0000"  (WRONG — use date only)
✅ cdq get-results --dataset "MY_DATASET" --run-id "2026-05-14"    (correct)
```

> **run-id format:** Use the date portion only (e.g., `2026-05-14`), not the full ISO timestamp. Run `cdq get-recent-runs` to find valid run IDs.

## Example

```bash
cdq get-results --dataset "MY_DATASET" --run-id "2026-05-14"
```

## Output

JSON with overall score, per-rule results, pass/fail counts, and finding details.

## Workflow

```
cdq get-recent-runs          → find run IDs
cdq get-results --run-id ... → get full results
```
