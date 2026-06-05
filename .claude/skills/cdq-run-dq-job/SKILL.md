---
name: cdq-run-dq-job
description: Register a dataset definition and run a Data Quality job in Collibra DQ. Requires --dataset (logical name you choose) and --sql (query using PHYSICAL table name). Use when: (1) Running a new DQ job on a dataset, (2) Registering a new dataset with a logical name, (3) Re-running a job with updated rules, (4) Processing data with source SQL query.
---

# CDQ Run DQ Job

> **TL;DR:** Register a dataset with a logical name and run a DQ job on it.
>
> - `--dataset` = logical name you choose (e.g. `MY_DATASET`) — CDQ identifier
> - `--sql` = query using physical table (e.g. `SELECT * FROM samples.orders`) — runs against your DB

## Command

```bash
cdq run-dq-job --dataset "MY_DATASET" --sql "SELECT * FROM samples.table LIMIT 100000" [--run-id YYYY-MM-DD] [--connection CXN]
```

❌ `--dataset "samples.orders"` — `--dataset` is a logical name, not a physical table.  
❌ `--sql "SELECT * FROM MY_DATASET"` — `--sql` must use the physical table.  
✅ `--dataset "MY_DATASET" --sql "SELECT * FROM samples.orders LIMIT 100000"`

Default to `LIMIT 100000` in `--sql` unless the user requests otherwise.

## Done

Run the job, then immediately call `cdq get-results --dataset "MY_DATASET" --run-id "YYYY-MM-DD"` — jobs finish in 1–2 seconds. Report both results and stop.
