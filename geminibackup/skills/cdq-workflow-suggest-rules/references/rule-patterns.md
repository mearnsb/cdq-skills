# Rule SQL Patterns

Common patterns for writing DQ rule SQL. The rule SQL should return rows that represent failures/violations.

## Rule Type Patterns

| Rule Type | Example SQL | When to Use |
|-----------|-------------|-------------|
| Not null | `SELECT * FROM {dataset} WHERE column IS NULL` | Column should never be empty |
| Unique | `SELECT * FROM {dataset} GROUP BY column HAVING COUNT(*) > 1` | Column values should be unique |
| Valid values | `SELECT * FROM {dataset} WHERE column NOT IN ('A', 'B', 'C')` | Column must be one of allowed values |
| Format check | `SELECT * FROM {dataset} WHERE column NOT LIKE '%@%.%'` | Column must match pattern (e.g., email) |
| Range check | `SELECT * FROM {dataset} WHERE amount < 0 OR amount > 10000` | Values must be within range |
| Not empty | `SELECT * FROM {dataset} WHERE column = ''` | String should not be empty |
| Cross-table | `SELECT * FROM source s FULL JOIN target t ON s.id = t.id WHERE s.id IS NULL OR t.id IS NULL` | Reconciliation between tables |

## Using the Dataset Placeholder

- Use `{dataset}` in your rule SQL to reference the dataset dynamically
- This allows the same rule to work with different dataset names
- Example: `SELECT * FROM {dataset} WHERE email IS NULL`

## Analysis Patterns

### Low Cardinality (Valid Values)

Find columns with few distinct values - good for "allowed values" rules.

```sql
SELECT column, COUNT(*) as cnt, COUNT(DISTINCT column) as unique_cnt
FROM (SELECT column FROM schema.table LIMIT 10000) t
GROUP BY column
HAVING COUNT(DISTINCT column) < 20
```

### Null Check Candidates

Find columns that are mostly filled but have some nulls.

```sql
SELECT
  COUNT(*) as total,
  SUM(CASE WHEN column IS NULL THEN 1 ELSE 0 END) as null_count,
  SUM(CASE WHEN column = '' THEN 1 ELSE 0 END) as empty_count
FROM schema.table
LIMIT 1
```

### Format Pattern Analysis

Sample data to identify formatting patterns.

```sql
SELECT DISTINCT column FROM schema.table LIMIT 20
```

### Infrequent Values

Find values that appear rarely (potential errors or outliers).

```sql
SELECT column, COUNT(*) as cnt
FROM schema.table
GROUP BY column
HAVING COUNT(*) < (SELECT COUNT(*) / 100 FROM schema.table LIMIT 1)
ORDER BY cnt ASC
LIMIT 10
```

## Rule Type Recommendations

Based on analysis results:

| Analysis Result | Rule Type | Example |
|-----------------|-----------|---------|
| Low cardinality (< 20 values) | Allowed values | `column NOT IN ('A','B','C')` |
| 1-10% nulls | Not null | `column IS NULL` |
| Empty strings | Not empty | `column = ''` |
| Pattern detected | Format check | `column NOT LIKE '%@%.%'` |
| Infrequent values | Unusual value | `column IN ('ZZZ','XXX')` |
| Duplicate keys | Uniqueness | `GROUP BY key HAVING COUNT(*) > 1` |