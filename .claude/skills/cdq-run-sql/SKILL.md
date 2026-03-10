---
name: cdq-run-sql
description: Execute SQL queries directly against the underlying datasource in Collibra DQ. Use when: (1) Testing source queries before creating datasets, (2) Exploring table schema and sample data, (3) Running ad-hoc queries for analysis, (4) Getting row counts.
---

# CDQ Run SQL

Execute SQL queries directly against the underlying datasource (database or data warehouse).

> **Important:** This command interacts directly with your database/data warehouse. Use **actual `schema.table` names**, not CDQ logical dataset names. This is the only command that requires strict database object names.

## Usage

```bash
python lib/client.py run-sql --sql "SELECT * FROM schema.actual_table LIMIT 10"
```

## Alternative (curl)

```bash
# First authenticate to get token
source .env && TOKEN=$(curl -sk -X POST "${DQ_URL}/auth/signin" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${DQ_USERNAME}\",\"password\":\"${DQ_PASSWORD}\",\"iss\":\"${DQ_ISS}\"}" | jq -r '.token')

# Then run SQL
curl -sk -X POST "${DQ_URL}/v2/getsqlresult?sql=SELECT%201&cxn=${DQ_CXN}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--sql` | Yes | SQL query string (use actual schema.table) |
| `--connection` | No | Datasource connection name (default: $DQ_CXN) |

## Examples

```bash
# Simple query on actual table
python lib/client.py run-sql --sql "SELECT * FROM my_schema.my_table LIMIT 10"

# Query with specific connection
python lib/client.py run-sql --sql "SELECT COUNT(*) FROM schema.table" --connection SNOWFLAKE

# Query BigQuery (use actual project.dataset.table)
python lib/client.py run-sql --sql "SELECT * FROM myproject.mydataset.mytable LIMIT 100"

# Test query before creating a dataset
python lib/client.py run-sql --sql "SELECT * FROM raw.customers WHERE active = true"

# Use this SQL to then create a dataset via run-dq-job
```

## Workflow Tip

Use `run-sql` to develop and test your source query, then use that same SQL in:
- `run-dq-job` - To register a dataset with a logical name
- `save-rule` - To define rules that check for data quality issues

## Output

Returns JSON with query results including schema and rows.

## API Endpoint

`POST /v2/getsqlresult?sql=<query>&cxn=<connection>`