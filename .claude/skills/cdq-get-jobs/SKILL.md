---
name: cdq-get-jobs
description: List queued and running DQ jobs in the Collibra DQ platform. All parameters optional. Use when: (1) Checking the status of DQ jobs, (2) Finding pending/running jobs, (3) Monitoring job queue. For completed run IDs, use cdq-get-recent-runs instead.
---

# CDQ Get Jobs

> **TL;DR:** Check the job queue for running or pending jobs. CDQ jobs finish in 1–2 seconds — check immediately after `run-dq-job`.

## Command

```bash
cdq get-jobs [--status running|setup|finished|failed] [--limit N]
```

❌ `cdq get-jobs --dataset "MY_DATASET"` — no `--dataset` flag exists.

## Done

Run the command, report the results, and stop. For completed run IDs use `cdq get-recent-runs` instead.
