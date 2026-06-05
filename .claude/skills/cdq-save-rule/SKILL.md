---
name: cdq-save-rule
description: Create a new Data Quality rule for a dataset in Collibra DQ. Requires --dataset (logical name), --name, and --sql (physical table name in SQL). Use when: (1) Adding DQ rules to check for data quality issues, (2) Creating completeness/validity checks, (3) Setting up uniqueness or range validations, (4) Defining custom SQL-based rules.
---

# CDQ Save Rule

> **TL;DR:** Attach a SQL-based DQ rule to a dataset. Rows returned by the rule SQL count as **failures**.
>
> - `--dataset` = logical name (e.g. `MY_DATASET`)
> - `--sql` = uses physical table — do NOT use `{dataset}` placeholder (breaks on BigQuery)

## Command

```bash
cdq save-rule --dataset "MY_DATASET" --name "rule_name" --sql "SELECT * FROM samples.table WHERE col IS NULL" [--points N] [--perc N] [--scoring-scheme {0,1}]
```

Common patterns:
```sql
-- Not null
SELECT * FROM samples.t WHERE col IS NULL
-- Unique
SELECT col FROM samples.t GROUP BY col HAVING COUNT(*) > 1
-- Valid values
SELECT * FROM samples.t WHERE status NOT IN ('OPEN','CLOSED')
-- Range
SELECT * FROM samples.t WHERE amount < 0
```

## Done

Run the command, report the result, and stop.
