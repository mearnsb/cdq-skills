---
name: cdq-workflow-run-complete-job
description: Complete DQ job workflow - explore first with limits, run job, check status, retrieve results. Use when: (1) Running a full DQ job cycle safely, (2) Processing data with safe limits, (3) Monitoring job from start to finish, (4) Getting comprehensive results.
---

# CDQ Workflow: Run Complete Job

> **TL;DR:** Full cycle: explore → run job → get results.
>
> - `--dataset` = logical name you choose (e.g. `MY_DATASET`)
> - `--sql` = physical table (e.g. `SELECT * FROM samples.orders`)

## Steps

```bash
# 1. Explore (LIMIT 5)
cdq run-sql --sql "SELECT * FROM samples.my_table LIMIT 5"

# 2. Run DQ job (default LIMIT 100000)
cdq run-dq-job --dataset "MY_DATASET" --sql "SELECT * FROM samples.my_table LIMIT 100000"

# 3. Get results immediately — jobs finish in 1–2 seconds
cdq get-results --dataset "MY_DATASET" --run-id "YYYY-MM-DD"
```

To add rules and re-run:
```bash
cdq save-rule --dataset "MY_DATASET" --name "rule_name" --sql "SELECT * FROM samples.my_table WHERE col IS NULL"
cdq run-dq-job --dataset "MY_DATASET" --sql "SELECT * FROM samples.my_table LIMIT 100000"
cdq get-results --dataset "MY_DATASET" --run-id "YYYY-MM-DD"
```
