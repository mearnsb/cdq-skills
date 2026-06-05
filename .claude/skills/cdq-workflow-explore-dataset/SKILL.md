---
name: cdq-workflow-explore-dataset
description: Complete workflow for exploring a dataset - search catalog, identify columns, and sample data with safe limits. Use when: (1) First-time exploration of a table, (2) Understanding schema before creating rules, (3) Checking data before running DQ jobs, (4) Getting row counts safely.
---

# CDQ Workflow: Explore Dataset

> **TL;DR:** Safely explore a physical table. All SQL uses physical table names (e.g. `samples.orders`). Always LIMIT exploratory queries.

## Steps

```bash
# 1. Check if dataset is already registered in CDQ
cdq search-catalog --query "table_name"

# 2. Find physical tables if needed
cdq list-tables --schema samples

# 3. Sample data — LIMIT 5 for first look
cdq run-sql --sql "SELECT * FROM samples.my_table LIMIT 5"

# 4. Row count
cdq run-sql --sql "SELECT COUNT(*) as cnt FROM samples.my_table"
```

After each step, stop and wait for results before proceeding to the next. Only continue to the next step if it's needed.
