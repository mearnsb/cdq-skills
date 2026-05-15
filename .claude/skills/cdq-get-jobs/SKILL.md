---
name: cdq-get-jobs
description: List queued and running DQ jobs in the Collibra DQ platform. All parameters optional. Use when: (1) Checking the status of DQ jobs, (2) Finding pending/running jobs, (3) Monitoring job queue. For completed run IDs, use cdq-get-recent-runs instead.
---

# CDQ Get Jobs

> **TL;DR:** Check the job queue for running or pending jobs. CDQ jobs finish in 1–2 seconds — check immediately after `run-dq-job`.

## Command

```bash
cdq get-jobs [--status STATUS] [--limit N]
```

**Help output:**
```
usage: cdq get-jobs [-h] [--status STATUS] [--limit LIMIT]

options:
  -h, --help       show this help message and exit
  --status STATUS  Filter by status
  --limit LIMIT    Max results
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--status` | all | Filter: `running`, `setup`, `finished`, `failed` |
| `--limit` | 10 | Max results |

**Correct vs. incorrect usage:**
```
❌ cdq get-jobs --dataset "MY_DATASET"    (WRONG — no --dataset flag exists)
✅ cdq get-jobs                           (correct — lists all recent jobs)
✅ cdq get-jobs --status running          (correct)
✅ cdq get-jobs --limit 20               (correct)
```

## Examples

```bash
# Check all recent jobs
cdq get-jobs --limit 20

# Check for running jobs
cdq get-jobs --status running
```

## Output

JSON array of jobs with dataset name, run ID, and status. Use `cdq get-recent-runs` if you need completed run IDs.
