---
name: cdq-workflow-save-complete-rule
description: Complete rule creation workflow - explore data, confirm schema, then save rule. Use when: (1) Creating new DQ rules safely, (2) Validating schema before saving rules, (3) Avoiding duplicate rules, (4) Ensuring rule SQL correctness.
---

# CDQ Workflow: Save Complete Rule

Explore a dataset to understand its structure, then save a DQ rule with user confirmation.

> **Safety:** Always explore first with LIMIT before saving rules.

## Usage

```bash
# Run complete workflow: explore, confirm, then save rule
python lib/client.py run-sql --sql "SELECT * FROM schema.table LIMIT 5"
python lib/client.py run-sql --sql "SELECT COUNT(*) as cnt FROM schema.table"

# Then save rule (use actual schema.table, no spaces in name)
python lib/client.py save-rule \
  --dataset "MY_DATASET" \
  --name "rule_name" \
  --sql "SELECT * FROM schema.table WHERE column IS NULL"
```

## Complete Workflow

```bash
# Step 1: Explore data to understand schema (always use LIMIT)
python lib/client.py run-sql --sql "SELECT * FROM schema.table LIMIT 5"

# Step 2: Get row count
python lib/client.py run-sql --sql "SELECT COUNT(*) as cnt FROM schema.table"

# Step 3: Check existing rules for this dataset
python lib/client.py get-rules --dataset "MY_DATASET"

# Step 4: Review column names, sample values, and existing rules
# Confirm you have the right columns and rule doesn't already exist

# Step 5: Save the rule (only if no similar rule exists)
# Use actual schema.table, NOT {dataset} placeholder
python lib/client.py save-rule \
  --dataset "MY_DATASET" \
  --name "no_nulls_email" \
  --sql "SELECT * FROM schema.table WHERE email IS NULL"

# Step 6: Verify rule was saved
python lib/client.py get-rules --dataset "MY_DATASET"
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--dataset` | Yes | Logical dataset name |
| `--name` | Yes | Rule name |
| `--sql` | Yes | Rule SQL (use actual `schema.table`, NOT `{dataset}` placeholder) |
| `--points` | No | Rule points (default: 1) |
| `--perc` | No | Percentage threshold (default: 1) |

## Rule SQL Patterns

Use the actual `schema.table` in your rule SQL (NOT the `{dataset}` placeholder - it may not work with all connections like BigQuery):

| Rule Type | Example SQL |
|-----------|-------------|
| Not null | `SELECT * FROM schema.table WHERE column IS NULL` |
| Unique | `SELECT * FROM schema.table GROUP BY column HAVING COUNT(*) > 1` |
| Valid values | `SELECT * FROM schema.table WHERE column NOT IN ('A', 'B', 'C')` |
| Format check | `SELECT * FROM schema.table WHERE column NOT LIKE '%@%.%'` |
| Range check | `SELECT * FROM schema.table WHERE amount < 0 OR amount > 10000` |

> **Important:** Always use the actual `schema.table` (e.g., `samples.nyse_categorical`) instead of `{dataset}`. The placeholder syntax is not supported by all datasource connections (e.g., BigQuery returns a syntax error).

## Default Limits

| Phase | Default Limit |
|-------|---------------|
| Exploratory (sample) | LIMIT 5 |
| Row count | LIMIT 1 |
| Rule preview | Shows first 6 failures |

## User Confirmation

Before saving, confirm:
- [ ] Column names are correct
- [ ] Data types match your rule logic
- [ ] Rule SQL syntax is valid
- [ ] Dataset name is correct
- [ ] No similar rule already exists (check with `get-rules` first)

## Example

```bash
# Explore first
python lib/client.py run-sql --sql "SELECT * FROM customers LIMIT 5"

# Save rule for email validation (use actual schema.table)
python lib/client.py save-rule \
  --dataset "CUSTOMER_DATA" \
  --name "Email Not Null" \
  --sql "SELECT * FROM schema.table WHERE email IS NULL"

# Check it was saved
python lib/client.py get-rules --dataset "CUSTOMER_DATA"
```

## Avoid Duplicate Rules

Always check for existing rules before saving a new one:

```bash
# Check what rules already exist
python lib/client.py get-rules --dataset "MY_DATASET"
```

### Duplicate Check Questions:
- Does a rule with similar logic already exist?
- Is this rule checking the same column?
- Is the SQL condition identical or very similar?

If similar rule exists, either:
1. Use existing rule instead
2. Modify rule name to be distinct
3. Skip if redundant

## Related

- `cdq-workflow-explore-dataset` - Explore-only workflow
- `cdq-workflow-suggest-rules` - Analyze and propose rules
- `cdq-get-rules` - List rules for a dataset
- `cdq-save-rule` - Save rule command