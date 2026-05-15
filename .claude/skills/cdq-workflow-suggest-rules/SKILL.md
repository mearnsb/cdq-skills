---
name: cdq-workflow-suggest-rules
description: Analyze columns and propose data quality rules based on patterns and statistics. Use when: (1) Suggesting DQ rules for a new dataset, (2) Analyzing data for quality issues, (3) Finding null patterns or format issues, (4) Recommending rule types based on column analysis.
---

# CDQ Workflow: Suggest Rules

> **TL;DR:** Analyze a physical table to propose DQ rules. Always check size first. Propose max 3–5 rules. Check for duplicates before saving.
>
> All SQL uses **physical table names** (e.g., `samples.orders`). See [lib/NAMING.md](../lib/NAMING.md).

## Steps

```bash
# 1. Check row count first — stop if > 100M rows
cdq run-sql --sql "SELECT COUNT(*) as cnt FROM samples.my_table"

# 2. Sample schema
cdq run-sql --sql "SELECT * FROM samples.my_table LIMIT 5"

# 3. Check existing rules (avoid duplicates)
cdq get-rules --dataset "MY_DATASET"

# 4. Run targeted analysis (examples below)

# 5. Save the top 3–5 rules found
cdq save-rule --dataset "MY_DATASET" --name "..." --sql "..."
```

## Analysis Patterns

```sql
-- Null % per column
SELECT COUNT(*) as total, SUM(CASE WHEN col IS NULL THEN 1 ELSE 0 END) as nulls
FROM samples.my_table

-- Low cardinality (good for valid-values rules)
SELECT col, COUNT(*) as cnt FROM samples.my_table GROUP BY col ORDER BY cnt DESC LIMIT 20

-- Duplicate keys
SELECT id, COUNT(*) FROM samples.my_table GROUP BY id HAVING COUNT(*) > 1 LIMIT 10

-- Format check sample
SELECT DISTINCT email FROM samples.my_table LIMIT 20
```

## Size Guardrails

| Condition | Action |
|-----------|--------|
| > 100M rows | Stop — ask user to add a WHERE filter or use LIMIT |
| > 100 columns | Pick the 10 most important columns to analyze |
| Query > 30s | Reduce LIMIT or add filter |

## Rule Types to Propose

| Finding | Rule Type |
|---------|-----------|
| Column has nulls | Not null check |
| < 20 distinct values | Valid values check |
| Email/phone/date column | Format check |
| ID column with duplicates | Uniqueness check |
| Numeric column with outliers | Range check |

Propose at most 3–5 rules. Run `cdq get-rules` first to skip any that already exist.
