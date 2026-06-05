---
name: duckdb-sql
description: Run SQL queries against local CSV files using DuckDB (Python). No DB setup needed — read_csv_auto loads any CSV as a table. Supports aggregations, window functions, joins across files, and CTEs.
---

# DuckDB SQL — Local CSV Querying

> Query CSV/Parquet/JSON files with standard SQL using DuckDB's Python bindings. Uses `read_csv_auto` which automatically infers schema from headers. No database server, no config.

## When to Use

- **Ad-hoc analysis** of generated fake data, exports, or CSVs
- **Quick SQL practice** without setting up a database
- **Data validation** before loading into a real system
- **Composable analysis** — pipe faker output to DuckDB queries
- **Testing SQL logic** that you'll later run against a real DB

## How It Works

DuckDB is installed as a Python package. Use it inline or as a one-liner:

```python
import duckdb
con = duckdb.connect()
result = con.execute("SELECT ... FROM read_csv_auto('/path/to/file.csv')").fetchdf()
print(result.to_string())
```

### Key Functions

| Function | Purpose |
|----------|---------|
| `read_csv_auto(path)` | Load CSV with auto-schema detection |
| `read_csv(path, columns=...)` | Load CSV with explicit schema |
| `read_parquet(path)` | Load Parquet files |
| `read_json(path)` | Load JSON files |
| `read_json_auto(path)` | Load JSON with auto-schema |
| `fetchdf()` | Return result as pandas DataFrame |
| `df` | Return the result directly |

## Basic Usage

### Run from the command line

```bash
python3 -c "
import duckdb
con = duckdb.connect()
result = con.execute(\"\"\"
  SELECT * FROM read_csv_auto('/tmp/data.csv')
  LIMIT 10
\"\"\").fetchdf()
print(result.to_string())
"
```

### From a Python script

```python
import duckdb

con = duckdb.connect()
df = con.execute("""
  SELECT first_name, last_name, email, job
  FROM read_csv_auto('/tmp/customers.csv')
  WHERE state_abbr = 'CA'
  ORDER BY last_name
  LIMIT 20
""").fetchdf()

print(df.to_string())
```

## Query Patterns

### Aggregations

```sql
SELECT job, COUNT(*) AS cnt,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) AS pct
FROM read_csv_auto('/tmp/employees.csv')
GROUP BY job
ORDER BY cnt DESC
LIMIT 10
```

### Column computations

```sql
SELECT first_name || ' ' || last_name AS full_name,
       city || ', ' || state_abbr AS location,
       CASE
         WHEN CAST(strftime(date_of_birth, '%Y') AS INT) > 2000 THEN 'Gen Z'
         WHEN CAST(strftime(date_of_birth, '%Y') AS INT) > 1980 THEN 'Millennial'
         ELSE 'Gen X/Boomer'
       END AS generation
FROM read_csv_auto('/tmp/users.csv')
```

### Window functions

```sql
SELECT state_abbr, job, salary,
       AVG(salary) OVER (PARTITION BY state_abbr) AS state_avg,
       salary - AVG(salary) OVER (PARTITION BY state_abbr) AS vs_state_avg
FROM read_csv_auto('/tmp/employees.csv')
ORDER BY state_abbr, salary DESC
```

### Joining multiple files

```sql
SELECT o.order_id, o.amount, c.first_name, c.last_name, c.email
FROM read_csv_auto('/tmp/orders.csv') o
JOIN read_csv_auto('/tmp/customers.csv') c
  ON o.customer_id = c.customer_id
WHERE o.amount > 100
ORDER BY o.amount DESC
```

### CTEs (WITH clause)

```sql
WITH state_stats AS (
  SELECT state_abbr, COUNT(*) AS cnt,
         ROUND(AVG(CAST(age AS DOUBLE)), 1) AS avg_age
  FROM read_csv_auto('/tmp/users.csv')
  GROUP BY state_abbr
)
SELECT * FROM state_stats
WHERE cnt > 5
ORDER BY cnt DESC
```

### Handling nulls

```sql
SELECT column_name, COUNT(*) AS total,
       COUNT(CASE WHEN value IS NULL THEN 1 END) AS null_count,
       ROUND(100.0 * COUNT(CASE WHEN value IS NULL THEN 1 END) / COUNT(*), 1) AS null_pct
FROM read_csv_auto('/tmp/data_with_nulls.csv')
GROUP BY column_name
ORDER BY null_pct DESC
```

## No-Config Single-Line Query

Quickest way to run an ad-hoc query without a script file:

```bash
python3 -c "import duckdb; print(duckdb.connect().execute('SELECT COUNT(*) FROM read_csv_auto(\"'$1'\")').fetchdf().to_string())"
```

## Notes

- DuckDB runs in-process — no server, no ports, no config
- Results return as pandas DataFrame; use `.to_string()` for terminal display
- Use `.fetchall()` instead of `.fetchdf()` to get raw tuples (no pandas dependency)
- For large CSVs, consider `read_csv(path, header=true, delim=',')` with explicit types for performance
