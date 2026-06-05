---
name: cdq-workflow-save-complete-rule
description: Complete rule creation workflow - explore data, confirm schema, then save rule. Use when: (1) Creating new DQ rules safely, (2) Validating schema before saving rules, (3) Avoiding duplicate rules, (4) Ensuring rule SQL correctness.
---

# CDQ Workflow: Save Complete Rule

> **TL;DR:** Safely create a rule: check schema → check existing rules → test SQL → save.
>
> - `--dataset` = logical name (e.g. `MY_DATASET`)
> - Rule `--sql` = physical table — do NOT use `{dataset}` placeholder (breaks on BigQuery)

## Steps

```bash
# 1. Check schema
cdq run-sql --sql "SELECT * FROM samples.my_table LIMIT 5"

# 2. Check existing rules (avoid duplicates)
cdq get-rules --dataset "MY_DATASET"

# 3. Test rule SQL — rows returned = failures
cdq run-sql --sql "SELECT * FROM samples.my_table WHERE col IS NULL LIMIT 10"

# 4. Save the rule
cdq save-rule --dataset "MY_DATASET" --name "col_not_null" --sql "SELECT * FROM samples.my_table WHERE col IS NULL"
```

Common rule patterns:
```sql
-- Unique:       SELECT col FROM t GROUP BY col HAVING COUNT(*) > 1
-- Valid values: SELECT * FROM t WHERE status NOT IN ('ACTIVE','INACTIVE')
-- Range:        SELECT * FROM t WHERE amount < 0
-- Format:       SELECT * FROM t WHERE email NOT LIKE '%@%.%'
```
