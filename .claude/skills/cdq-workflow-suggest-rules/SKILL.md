---
name: cdq-workflow-suggest-rules
description: Analyze columns and propose data quality rules based on patterns and statistics. Use when: (1) Suggesting DQ rules for a new dataset, (2) Analyzing data for quality issues, (3) Finding null patterns or format issues, (4) Recommending rule types based on column analysis.
---

# CDQ Workflow: Suggest Rules

> **TL;DR:** Analyze a physical table to propose DQ rules. Check size first. Propose max 3–5 rules. Check for duplicates before saving.

## Steps

```bash
# 1. Check row count — stop if > 100M rows
cdq run-sql --sql "SELECT COUNT(*) as cnt FROM samples.my_table"

# 2. Sample schema
cdq run-sql --sql "SELECT * FROM samples.my_table LIMIT 5"

# 3. Check existing rules
cdq get-rules --dataset "MY_DATASET"

# 4. Targeted analysis
cdq run-sql --sql "SELECT col, COUNT(*) FROM samples.my_table GROUP BY col ORDER BY cnt DESC LIMIT 20"
```

| Finding | Rule to propose |
|---------|----------------|
| Column has nulls | Not null check |
| < 20 distinct values | Valid values check |
| Email/phone/date col | Format check |
| ID col with duplicates | Uniqueness check |
| Numeric outliers | Range check |

Propose at most 3–5 rules. Confirm with the user before saving.
