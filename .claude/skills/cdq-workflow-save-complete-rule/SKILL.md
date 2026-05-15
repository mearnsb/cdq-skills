---
name: cdq-workflow-save-complete-rule
description: Complete rule creation workflow - explore data, confirm schema, then save rule. Use when: (1) Creating new DQ rules safely, (2) Validating schema before saving rules, (3) Avoiding duplicate rules, (4) Ensuring rule SQL correctness.
---

# CDQ Workflow: Save Complete Rule

> **TL;DR:** Safely create a rule: explore columns → check existing rules → save rule → verify.
>
> **Two names are in play:**
> - `--dataset` = **logical name** in CDQ (e.g., `MY_DATASET`)
> - Rule `--sql` = uses **physical** `schema.table` — do NOT use `{dataset}` placeholder (breaks on BigQuery)
>
> See [lib/NAMING.md](../lib/NAMING.md).

## Steps

```bash
# 1. Understand the columns
cdq run-sql --sql "SELECT * FROM samples.my_table LIMIT 5"

# 2. Check existing rules to avoid duplicates
cdq get-rules --dataset "MY_DATASET"

# 3. Test your rule SQL — rows returned = failures
cdq run-sql --sql "SELECT * FROM samples.my_table WHERE email IS NULL LIMIT 10"

# 4. Save the rule (only if no similar rule exists)
cdq save-rule \
  --dataset "MY_DATASET" \
  --name "email_not_null" \
  --sql "SELECT * FROM samples.my_table WHERE email IS NULL"

# 5. Verify it was saved
cdq get-rules --dataset "MY_DATASET"
```

## Rule SQL Patterns

```sql
-- Not null
SELECT * FROM samples.my_table WHERE col IS NULL

-- Unique
SELECT col FROM samples.my_table GROUP BY col HAVING COUNT(*) > 1

-- Valid values
SELECT * FROM samples.my_table WHERE status NOT IN ('ACTIVE','INACTIVE')

-- Format check (email)
SELECT * FROM samples.my_table WHERE email NOT LIKE '%@%.%'

-- Range check
SELECT * FROM samples.my_table WHERE amount < 0 OR amount > 1000000
```

## Before Saving — Confirm

- Column names match actual schema (from step 1)
- No identical or near-identical rule exists (from step 2)
- Rule SQL returns expected failures (from step 3)
