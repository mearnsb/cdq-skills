---
name: cdq-workflow-explore-dataset
description: Complete workflow for exploring a dataset - search catalog, identify columns, and sample data with safe limits. Use when: (1) First-time exploration of a table, (2) Understanding schema before creating rules, (3) Checking data before running DQ jobs, (4) Getting row counts safely.
---

# CDQ Workflow: Explore Dataset

> **TL;DR:** Safely explore a table before running DQ jobs. Always use LIMIT on exploratory queries.
>
> All SQL here uses **physical table names** (e.g., `samples.orders`). See [lib/NAMING.md](../lib/NAMING.md).

## Steps

```bash
# 1. Find the table (searches CDQ catalog for registered datasets)
cdq search-catalog --query "table_name"

# 2. Browse physical tables in the database
cdq list-tables --schema samples

# 3. Sample data — ALWAYS use LIMIT 5 for first look
cdq run-sql --sql "SELECT * FROM samples.my_table LIMIT 5"

# 4. Row count
cdq run-sql --sql "SELECT COUNT(*) as cnt FROM samples.my_table"

# 5. Check for nulls in key columns
cdq run-sql --sql "SELECT COUNT(*) as nulls FROM samples.my_table WHERE email IS NULL"
```

## Safe Limits

| Query purpose | Default limit |
|---------------|--------------|
| Sample data | `LIMIT 5` |
| Row count | `LIMIT 1` (aggregate) |
| Distinct values | `LIMIT 20` |

Do not remove LIMIT without user confirmation.

## Next Steps After Exploration

- Run a DQ job: `cdq run-dq-job`
- Suggest rules: invoke `/cdq-workflow-suggest-rules`
- Save a rule: invoke `/cdq-workflow-save-complete-rule`
