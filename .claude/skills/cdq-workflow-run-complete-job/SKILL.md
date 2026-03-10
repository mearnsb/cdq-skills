---
name: cdq-workflow-run-complete-job
description: Complete DQ job workflow - explore first with limits, run job, check status, retrieve results. Use when: (1) Running a full DQ job cycle safely, (2) Processing data with safe limits, (3) Monitoring job from start to finish, (4) Getting comprehensive results.
---

# CDQ Workflow: Run Complete Job

Run a complete DQ job workflow: explore first with limits, run job, check status, retrieve results.

> **Safety:** Default LIMIT 100,000 for jobs. User must explicitly request larger.

## Usage

```bash
# Run complete workflow in one go
python lib/client.py run-dq-job \
  --dataset "MY_DATASET" \
  --sql "SELECT * FROM schema.table LIMIT 100000"

# Then check results
python lib/client.py get-results --dataset "MY_DATASET" --run-id "2026-03-09"

# Or get job status
python lib/client.py get-jobs --limit 5
```

## Complete Workflow

```bash
# Step 1: Explore first (recommended)
python lib/client.py run-sql --sql "SELECT * FROM schema.table LIMIT 5"
python lib/client.py run-sql --sql "SELECT COUNT(*) as cnt FROM schema.table"

# Step 2: Run DQ job with appropriate limit
python lib/client.py run-dq-job \
  --dataset "MY_DATASET" \
  --sql "SELECT * FROM schema.table LIMIT 100000"

# Step 3: Check job status
python lib/client.py get-jobs --limit 3

# Step 4: Get results (after job completes)
python lib/client.py get-results --dataset "MY_DATASET" --run-id "2026-03-09"
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--dataset` | Yes | Logical dataset name (your choice) |
| `--sql` | Yes | Source SQL with LIMIT |
| `--run-id` | No | Run ID (default: today's date) |
| `--connection` | No | Connection name (default: $DQ_CXN) |

## Default Limits

| Phase | Default Limit | When to Increase |
|-------|---------------|------------------|
| Exploratory | LIMIT 5 | User confirms table looks good |
| Job run | LIMIT 100,000 | User explicitly requests more |

## Job Status Values

| Status | Meaning |
|--------|---------|
| SETUP | Job initializing |
| RUNNING | Job in progress |
| FINISHED | Job completed successfully |
| FAILED | Job failed |
| CANCELLED | Job was cancelled |

## Results Key Metrics

```json
{
  "rows": 100000,
  "score": 100,
  "passFail": 1,
  "runTime": "00:00:15",
  "cols": 9,
  "activeRules": 0,
  "activeAlerts": 0
}
```

| Field | Description |
|-------|-------------|
| rows | Number of rows processed |
| score | DQ score (0-100) |
| passFail | 1 = passed, 0 = failed |
| runTime | Job duration |
| cols | Number of columns |
| activeRules | Rules evaluated |
| activeAlerts | Alerts triggered |

## Examples

```bash
# Standard workflow with 100k limit (default)
python lib/client.py run-dq-job \
  --dataset "SALES_ANALYSIS" \
  --sql "SELECT * FROM sales.orders LIMIT 100000"

# Smaller exploratory run
python lib/client.py run-dq-job \
  --dataset "QUICK_CHECK" \
  --sql "SELECT * FROM customers LIMIT 1000"

# Check specific run
python lib/client.py get-results \
  --dataset "SALES_ANALYSIS" \
  --run-id "2026-03-09"
```

## Related

- `cdq-workflow-explore-dataset` - For exploration-only workflow
- `cdq-get-results` - Get detailed results
- `cdq-get-jobs` - List job history