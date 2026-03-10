---
name: cdq-workflow-suggest-rules
description: Analyze columns and propose data quality rules based on patterns and statistics. Use when: (1) Suggesting DQ rules for a new dataset, (2) Analyzing data for quality issues, (3) Finding null patterns or format issues, (4) Recommending rule types based on column analysis.
---

# CDQ Workflow: Suggest Rules

Analyze a dataset's columns to identify potential data quality rules. Propose rules based on:
- Low cardinality columns (valid value sets)
- Null/empty patterns
- Data format patterns
- Infrequent values

> **Safety:** Default to analyzing max 5-10 columns and max 3-5 rule types to prevent runaway queries.

## Important: Check Size First

Before running analysis, always check dataset size to avoid resource issues:

```bash
# Quick row count check (always run this first)
python lib/client.py run-sql --sql "SELECT COUNT(*) as row_count FROM schema.table LIMIT 1"

# Quick column count check (estimate from schema)
python lib/client.py run-sql --sql "SELECT * FROM schema.table LIMIT 1"
```

## Thresholds and Warnings

| Condition | Action |
|-----------|--------|
| > 100 million rows | **STOP** - Warn user, suggest filter/sample |
| > 100 columns | **STOP** - Limit to 10 key columns |
| Query takes > 30s | **STOP** - Reduce limit or add filter |
| No LIMIT on query | **STOP** - Add LIMIT |

### If Exceeded, Ask User:

1. Continue anyway? (User accepts risk)
2. Add filter? (WHERE clause, date range)
3. Use sample? (LIMIT 10000)
4. Analyze subset? (Specific columns only)

## Usage

```bash
# Step 1: Check size first (quick row count)
python lib/client.py run-sql --sql "SELECT COUNT(*) as row_count FROM schema.table LIMIT 1"

# Step 2: If < 100M rows, explore schema (LIMIT 5)
python lib/client.py run-sql --sql "SELECT * FROM schema.table LIMIT 5"

# Step 3: Check existing rules to avoid duplicates
python lib/client.py get-rules --dataset "MY_DATASET"

# Step 4: Run analysis queries to find rule opportunities
# (see patterns below)

# Step 5: Save selected rules
python lib/client.py save-rule --dataset "MY_DATASET" --name "Rule" --sql "SELECT..."
```

## Analysis Patterns

### 1. Low Cardinality (Valid Values)

Find columns with few distinct values - good for "allowed values" rules.

```sql
-- Find columns with low cardinality (good for code/value sets)
SELECT column, COUNT(*) as cnt, COUNT(DISTINCT column) as unique_cnt
FROM (SELECT column FROM schema.table LIMIT 10000) t
GROUP BY column
HAVING COUNT(DISTINCT column) < 20
```

### 2. Null Check Candidates

Find columns that are mostly filled but have some nulls.

```sql
-- Find columns with partial nulls (1-10% nulls)
SELECT
  COUNT(*) as total,
  SUM(CASE WHEN column IS NULL THEN 1 ELSE 0 END) as null_count,
  SUM(CASE WHEN column = '' THEN 1 ELSE 0 END) as empty_count
FROM schema.table
LIMIT 1
```

### 3. Format Pattern Analysis

Sample data to identify formatting patterns.

```sql
-- Sample to identify patterns (email, phone, date, etc.)
SELECT DISTINCT column FROM schema.table LIMIT 20
```

### 4. Infrequent Values

Find values that appear rarely (potential errors or outliers).

```sql
-- Find infrequent values (less than 1% of total)
SELECT column, COUNT(*) as cnt
FROM schema.table
GROUP BY column
HAVING COUNT(*) < (SELECT COUNT(*) / 100 FROM schema.table LIMIT 1)
ORDER BY cnt ASC
LIMIT 10
```

## Rule Type Recommendations

Based on analysis, these are typical rules to propose:

| Analysis | Rule Type | Example |
|----------|-----------|---------|
| Low cardinality (< 20 values) | Allowed values | `column NOT IN ('A','B','C')` |
| 1-10% nulls | Not null | `column IS NULL` |
| Empty strings | Not empty | `column = ''` |
| Pattern detected | Format check | `column NOT LIKE '%@%.%'` |
| Infrequent values | Unusual value | `column IN ('ZZZ','XXX')` |
| Duplicate keys | Uniqueness | `GROUP BY key HAVING COUNT(*) > 1` |

## Safety Limits

| Scenario | Default Limit | Action if Exceeded |
|----------|---------------|-------------------|
| Rows | 100 million | Warn + ask user |
| Columns | 100 | Limit to 10 key columns |
| Columns to analyze | 5-10 | Pick top columns only |
| Cardinality check | LIMIT 10,000 | Reduce to 1,000 |
| Null analysis | LIMIT 1 | Already aggregate |
| Pattern sampling | LIMIT 20 | Keep at 20 |
| Infrequent values | LIMIT 10 | Keep at 10 |
| Total rule suggestions | 3-5 | Pick top 3 only |

## Large Dataset Alternatives

If dataset is too large, try these approaches:

### 1. Add Date Filter
```sql
-- Filter to recent data only
WHERE date_col >= '2025-01-01'
```

### 2. Use Specific Columns
```sql
-- Don't use SELECT *, pick columns
SELECT id, email, status FROM table LIMIT 10000
```

### 3. Use Partition Column
```sql
-- If table is partitioned, use partition filter
WHERE partition_col = '2025-03-09'
```

### 4. Sample First
```sql
-- Test with small sample first
SELECT * FROM table LIMIT 1000
-- Then expand after confirming works
```

### 5. Incremental Column Analysis
```sql
-- Analyze one column at a time
SELECT column, COUNT(*) FROM table GROUP BY column LIMIT 20
```

## Quick Pre-flight Check

Always run these first:

```bash
# 1. Row count (takes ~5-10s on large tables)
python lib/client.py run-sql --sql "SELECT COUNT(*) as cnt FROM schema.table LIMIT 1"

# 2. Schema check (LIMIT 1 is fast)
python lib/client.py run-sql --sql "SELECT * FROM schema.table LIMIT 1"

# 3. Check existing rules to avoid duplicates
python lib/client.py get-rules --dataset "MY_DATASET"

# If row count > 100M: STOP and ask user
# If columns > 100: Limit to key columns
# If similar rule exists: Skip or modify
```

## Example Workflow

```bash
# 1. Explore schema
python lib/client.py run-sql --sql "SELECT * FROM customers LIMIT 5"

# 2. Check cardinality for key columns
python lib/client.py run-sql --sql "SELECT status, COUNT(*) as cnt FROM customers GROUP BY status LIMIT 20"

# 3. Check null percentages
python lib/client.py run-sql --sql "SELECT COUNT(*) as total, SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) as nulls FROM customers LIMIT 1"

# 4. Sample to find patterns
python lib/client.py run-sql --sql "SELECT DISTINCT phone FROM customers LIMIT 20"

# 5. Save rules based on findings (use actual schema.table, no spaces in name)
python lib/client.py save-rule \
  --dataset "CUSTOMER_DATA" \
  --name "valid_status_values" \
  --sql "SELECT * FROM schema.table WHERE status NOT IN ('ACTIVE','INACTIVE','PENDING')"

python lib/client.py save-rule \
  --dataset "CUSTOMER_DATA" \
  --name "email_not_null" \
  --sql "SELECT * FROM schema.table WHERE email IS NULL"
```

## Large Dataset Warning

For tables with 100+ columns or millions of rows:
- Limit analysis to key columns (specify explicitly)
- Use LIMIT on all queries
- Pick top 3 rule types only
- Consider running on a sample first

## Avoid Duplicate Rules

Before proposing or saving any rule, always check existing rules:

```bash
# Check existing rules first
python lib/client.py get-rules --dataset "MY_DATASET"
```

### Check Questions:
- Does a similar rule already exist?
- Is the logic checking the same column and condition?
- Is the proposed rule redundant?

### If Duplicate Found:
- Skip this rule type
- Or note that it already exists
- Don't create overlapping rules

This prevents:
- Conflicting rules
- Duplicate alerts
- Confusion about which rule applies

## Related

- `cdq-workflow-explore-dataset` - Basic exploration
- `cdq-workflow-save-complete-rule` - Save after confirmation
- `cdq-save-rule` - Save rule command
- `cdq-get-rules` - List existing rules