---
name: cdq-workflow-explore-dataset
description: Complete workflow for exploring a dataset - search catalog, identify columns, and sample data with safe limits. Use when: (1) First-time exploration of a table, (2) Understanding schema before creating rules, (3) Checking data before running DQ jobs, (4) Getting row counts safely.
---

# CDQ Workflow: Explore Dataset

Explore a dataset to identify its structure, columns, and sample data with safe limits.

> **Default limits:** LIMIT 5 for sample data, LIMIT 1 for counts. User must explicitly override for larger datasets.

## Usage

```bash
# Search catalog for a table
python lib/client.py search-catalog --query "table_name" --limit 10

# Explore schema + sample (LIMIT 5)
python lib/client.py run-sql --sql "SELECT * FROM schema.table LIMIT 5"

# Get row count
python lib/client.py run-sql --sql "SELECT COUNT(*) as cnt FROM schema.table"
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--query` | Yes | Search term for catalog |
| `--limit` | No | Search results limit (default: 10) |

## Exploratory SQL Patterns

Always use limits for exploratory queries:

| Query Type | Default Limit | Override |
|------------|---------------|----------|
| Sample data | LIMIT 5 | `--limit 100` |
| Row count | LIMIT 1 | Not needed |
| Distinct values | LIMIT 10 | `--limit 50` |

## Examples

```bash
# Find a table in the catalog
python lib/client.py search-catalog --query "nyse"

# Identify columns + sample (LIMIT 5)
python lib/client.py run-sql --sql "SELECT * FROM samples.nyse_categorical LIMIT 5"

# Get total row count
python lib/client.py run-sql --sql "SELECT COUNT(*) as cnt FROM samples.nyse_categorical"

# Check for nulls in a column
python lib/client.py run-sql --sql "SELECT COUNT(*) as total, SUM(CASE WHEN column IS NULL THEN 1 ELSE 0 END) as nulls FROM table LIMIT 1"
```

## Workflow

```
1. search-catalog  → Find available datasets
2. run-sql (LIMIT) → Identify columns and sample data
3. run-sql (COUNT) → Get row count
4. run-dq-job      → Run DQ job with appropriate limit
```

## Output Interpretation

- **schema** in results shows column names and metadata
- **rows** shows actual data with values
- **rowCount** shows number of rows returned

## Related

- `cdq-run-dq-job` - Run DQ job after exploration
- `cdq-workflow-run-complete-job` - Combined explore + run workflow