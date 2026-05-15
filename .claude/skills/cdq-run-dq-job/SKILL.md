---
name: cdq-run-dq-job
description: Register a dataset definition and run a Data Quality job in Collibra DQ. Requires --dataset (logical name you choose) and --sql (query using PHYSICAL table name). Use when: (1) Running a new DQ job on a dataset, (2) Registering a new dataset with a logical name, (3) Re-running a job with updated rules, (4) Processing data with source SQL query.
---

# CDQ Run DQ Job

> **TL;DR:** Register a dataset with a logical name and run a DQ job on it.
>
> **Two names are in play — don't confuse them:**
> - `--dataset` = **logical name** you choose (e.g., `MY_DATASET`) — used to identify the dataset in CDQ
> - `--sql` = query using **physical table name** (e.g., `SELECT * FROM samples.orders`) — runs against your actual database
>
> See [lib/NAMING.md](../lib/NAMING.md).

## Command

```bash
cdq run-dq-job --dataset "MY_DATASET" --sql "SELECT * FROM schema.table LIMIT 100000" [--run-id YYYY-MM-DD] [--connection CXN]
```

**Help output:**
```
usage: cdq run-dq-job [-h] --dataset DATASET [--run-id RUN_ID] --sql SQL
                      [--connection CONNECTION]

options:
  -h, --help            show this help message and exit
  --dataset DATASET     Dataset name
  --run-id RUN_ID       Run ID (default: today's date)
  --sql SQL             Source SQL query
  --connection CONNECTION
                        Datasource connection name
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--dataset` | required | **Logical name** you assign in CDQ (your choice) |
| `--sql` | required | Source query using **physical** `schema.table` |
| `--run-id` | today's date | Run identifier (YYYY-MM-DD) |
| `--connection` | $DQ_CXN | Datasource connection name |

**Correct vs. incorrect usage:**
```
❌ cdq run-dq-job --dataset "samples.orders" --sql "SELECT * FROM samples.orders LIMIT 100000"
   (WRONG — --dataset should be a logical name you choose, not the physical table)

❌ cdq run-dq-job --dataset "MY_DATASET" --sql "SELECT * FROM MY_DATASET LIMIT 100000"
   (WRONG — --sql must use physical table name, not the logical dataset name)

✅ cdq run-dq-job --dataset "MY_DATASET" --sql "SELECT * FROM samples.orders LIMIT 100000"
   (correct — logical name in --dataset, physical table in --sql)
```

## Example

```bash
cdq run-dq-job \
  --dataset "CUSTOMER_ANALYSIS" \
  --sql "SELECT * FROM samples.customers LIMIT 100000"
```

## Safety

Default to `LIMIT 100000` in `--sql`. User must explicitly request a larger limit.

## Output

JSON with `registration` (dataset def saved) and `job` (run result). Jobs finish in 1–2 seconds — call `cdq get-results` immediately after.

## Workflow

```
cdq run-sql     → test your query with physical table
cdq run-dq-job  → register logical name + run job
cdq get-results → check score and rule results
cdq save-rule   → add rules (uses logical name), then re-run
```
