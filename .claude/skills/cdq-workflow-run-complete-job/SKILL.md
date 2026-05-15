---
name: cdq-workflow-run-complete-job
description: Complete DQ job workflow - explore first with limits, run job, check status, retrieve results. Use when: (1) Running a full DQ job cycle safely, (2) Processing data with safe limits, (3) Monitoring job from start to finish, (4) Getting comprehensive results.
---

# CDQ Workflow: Run Complete Job

> **TL;DR:** Full cycle: explore → run job → get results. Default to `LIMIT 100000` for jobs.
>
> **Two names are in play — don't confuse them:**
> - `--dataset` in `run-dq-job` / `get-results` = **logical name** you choose in CDQ
> - SQL queries in `run-sql` and `--sql` = use **physical** `schema.table`
>
> See [lib/NAMING.md](../lib/NAMING.md).

## Steps

```bash
# 1. Explore the physical table (LIMIT 5)
cdq run-sql --sql "SELECT * FROM samples.my_table LIMIT 5"
cdq run-sql --sql "SELECT COUNT(*) as cnt FROM samples.my_table"

# 2. Run DQ job (logical name + physical SQL)
cdq run-dq-job \
  --dataset "MY_DATASET" \
  --sql "SELECT * FROM samples.my_table LIMIT 100000"

# 3. Get results immediately (CDQ jobs finish in 1–2 seconds)
cdq get-results --dataset "MY_DATASET" --run-id "2026-05-14"
```

## Results Key Fields

| Field | Description |
|-------|-------------|
| `score` | DQ score 0–100 |
| `passFail` | 1 = passed, 0 = failed |
| `rows` | Rows processed |
| `activeRules` | Rules evaluated |

## Adding Rules After the First Run

```bash
cdq save-rule \
  --dataset "MY_DATASET" \
  --name "email_not_null" \
  --sql "SELECT * FROM samples.my_table WHERE email IS NULL"

# Re-run to apply the new rule
cdq run-dq-job --dataset "MY_DATASET" --sql "SELECT * FROM samples.my_table LIMIT 100000"
```
