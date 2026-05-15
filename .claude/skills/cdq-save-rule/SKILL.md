---
name: cdq-save-rule
description: Create a new Data Quality rule for a dataset in Collibra DQ. Requires --dataset (logical name), --name, and --sql (physical table name in SQL). Use when: (1) Adding DQ rules to check for data quality issues, (2) Creating completeness/validity checks, (3) Setting up uniqueness or range validations, (4) Defining custom SQL-based rules.
---

# CDQ Save Rule

> **TL;DR:** Attach a SQL-based DQ rule to a dataset. Rows returned by the rule SQL count as **failures**.
>
> **Two names are in play:**
> - `--dataset` = **logical name** (e.g., `MY_DATASET`) — which CDQ dataset this rule belongs to
> - `--sql` = query using **physical table name** (e.g., `FROM samples.orders`) — runs against your actual database. Do NOT use `{dataset}` placeholder — it breaks on BigQuery.
>
> See [lib/NAMING.md](../lib/NAMING.md).

## Command

```bash
cdq save-rule --dataset "MY_DATASET" --name "rule_name" --sql "SELECT * FROM schema.table WHERE col IS NULL" [--points N] [--perc N] [--scoring-scheme {0,1}]
```

**Help output:**
```
usage: cdq save-rule [-h] --dataset DATASET --name NAME --sql SQL
                     [--points POINTS] [--perc PERC] [--scoring-scheme {0,1}]

options:
  -h, --help            show this help message and exit
  --dataset DATASET     Dataset name
  --name NAME           Rule name
  --sql SQL             Rule SQL
  --points POINTS       Rule points (default: 1)
  --perc PERC           Percentage threshold (default: 10)
  --scoring-scheme {0,1}
                        Scoring scheme: 0=absolute, 1=proportional (default: 1)
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--dataset` | required | **Logical dataset name** in CDQ |
| `--name` | required | Rule name (no spaces recommended) |
| `--sql` | required | SQL using **physical** `schema.table` — returned rows = failures |
| `--points` | 1 | Point value |
| `--perc` | 10 | Failure percentage threshold |
| `--scoring-scheme` | 1 | 0=absolute count, 1=proportional (% of rows) |

**Correct vs. incorrect usage:**
```
❌ cdq save-rule --dataset "MY_DATASET" --name "check" --sql "SELECT * FROM {dataset} WHERE email IS NULL"
   (WRONG — {dataset} placeholder breaks on BigQuery; use physical table name)

❌ cdq save-rule --dataset "samples.orders" --name "check" --sql "SELECT * FROM samples.orders WHERE email IS NULL"
   (WRONG — --dataset must be a logical name, not a physical table)

✅ cdq save-rule --dataset "MY_DATASET" --name "email_not_null" --sql "SELECT * FROM samples.orders WHERE email IS NULL"
   (correct)
```

## Common Rule Patterns

```bash
# Not null
--sql "SELECT * FROM samples.orders WHERE email IS NULL"

# Unique
--sql "SELECT order_id FROM samples.orders GROUP BY order_id HAVING COUNT(*) > 1"

# Valid values
--sql "SELECT * FROM samples.orders WHERE status NOT IN ('OPEN','CLOSED','PENDING')"

# Range check
--sql "SELECT * FROM samples.orders WHERE amount < 0"
```

## Before Saving

Always check for existing rules first to avoid duplicates:
```bash
cdq get-rules --dataset "MY_DATASET"
```
