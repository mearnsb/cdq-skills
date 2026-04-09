# Safety Limits and Thresholds

Safety limits to prevent runaway queries and resource issues when analyzing datasets.

## Thresholds and Actions

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

## Safety Limits Table

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

## Pre-flight Check

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