---
name: cdq-run-sql
description: Execute SQL queries directly against the underlying datasource in Collibra DQ. Requires --sql with a PHYSICAL table name (e.g. schema.table) — never use logical CDQ dataset names here. Use when: (1) Testing source queries before creating datasets, (2) Exploring table schema and sample data, (3) Running ad-hoc queries for analysis, (4) Getting row counts.
---

# CDQ Run SQL

> **TL;DR:** Run SQL directly against your database (not CDQ). Always use **physical table names** (e.g., `samples.orders`) — never CDQ logical dataset names here.
>
> See [lib/NAMING.md](../lib/NAMING.md) for the logical vs physical distinction.

## Command

```bash
cdq run-sql --sql "SELECT * FROM schema.table LIMIT 10" [--connection CXN] | python3 lib/format_sql.py
```

**Help output:**
```
usage: cdq run-sql [-h] --sql SQL [--connection CONNECTION]

options:
  -h, --help            show this help message and exit
  --sql SQL             SQL query string
  --connection CONNECTION
                        Datasource connection name
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--sql` | required | SQL query — use **physical** `schema.table` names |
| `--connection` | $DQ_CXN | Datasource connection name |

**Correct vs. incorrect usage:**
```
❌ cdq run-sql --sql "SELECT * FROM MY_DATASET LIMIT 5"         (WRONG — MY_DATASET is a logical name, not a table)
❌ cdq run-sql --sql "SELECT * FROM samples.orders"             (WRONG — missing LIMIT, will scan full table)
✅ cdq run-sql --sql "SELECT * FROM samples.orders LIMIT 5"     (correct)
✅ cdq run-sql --sql "SELECT COUNT(*) as cnt FROM samples.orders" (correct — aggregate needs no LIMIT)
```

## Examples

```bash
# Sample data (always use LIMIT for exploration)
cdq run-sql --sql "SELECT * FROM samples.orders LIMIT 5" | python3 lib/format_sql.py

# Row count
cdq run-sql --sql "SELECT COUNT(*) as cnt FROM samples.orders" | python3 lib/format_sql.py

# Check for nulls
cdq run-sql --sql "SELECT COUNT(*) as nulls FROM samples.orders WHERE email IS NULL" | python3 lib/format_sql.py
```

## Output

Formatted as a markdown table. Raw JSON includes `schema` (column metadata) and `rows` (data values).

## Workflow Tip

Use `run-sql` to develop and test your source query, then reuse that SQL in `run-dq-job --sql` and `save-rule --sql`.
