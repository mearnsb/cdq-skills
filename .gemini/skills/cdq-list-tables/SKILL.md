---
name: cdq-list-tables
description: List physical tables in a database connection. Use when: (1) User doesn't know what tables exist, (2) Exploring available tables in a schema, (3) Finding table names before creating datasets, (4) Searching tables by name pattern.
---

# CDQ List Tables

List physical tables available in a database connection by querying INFORMATION_SCHEMA.

> **Note:** This command queries the database's INFORMATION_SCHEMA which requires read-only access. If you cannot query these tables, you won't be able to use this skill.
>
> **Alternative:** If INFORMATION_SCHEMA is not accessible, you can add table reference lists to your project's CLAUDE.md or a dedicated markdown file (e.g., `docs/tables.md`). Include table names, schemas, and descriptions so Claude can help you find tables without needing API access.

## Usage

```bash
python lib/client.py list-tables
python lib/client.py list-tables --schema samples
python lib/client.py list-tables --search account
python lib/client.py list-tables --limit 20
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--schema` | No | Uses DQ_CXN default | Database schema/dataset to list tables from |
| `--search` | No | None | Filter tables by name substring (case-insensitive) |
| `--limit` | No | 20 | Maximum number of tables to return (starts small for readability) |
| `--connection` | No | $DQ_CXN | Datasource connection name |

## Examples

```bash
# List first 20 tables in default schema
python lib/client.py list-tables

# List tables in a specific schema (BigQuery dataset)
python lib/client.py list-tables --schema samples

# Search for tables containing "account" in name
python lib/client.py list-tables --search account

# Get more results (up to 100)
python lib/client.py list-tables --limit 100

# Combine schema search and limit
python lib/client.py list-tables --schema my_dataset --limit 50

# Search with a connection
python lib/client.py list-tables --schema samples --connection BQ_CONNECTION
```

## Database-Specific Syntax

This skill adapts the query based on the database type:

### BigQuery
```sql
SELECT table_name FROM `<project>.<schema>.INFORMATION_SCHEMA.TABLES`
WHERE table_type = 'BASE TABLE'
ORDER BY table_name
```

### PostgreSQL/MySQL
```sql
SELECT table_name FROM INFORMATION_SCHEMA.TABLES
WHERE table_schema = '<schema>'
AND table_type = 'BASE TABLE'
ORDER BY table_name
```

### Snowflake
```sql
SELECT table_name FROM INFORMATION_SCHEMA.TABLES
WHERE table_schema = '<schema>'
AND table_type = 'BASE TABLE'
ORDER BY table_name
```

## Output

Returns a JSON array of table names, sorted alphabetically with limit applied.

```json
{
  "tables": ["accounts", "customers", "orders", ...],
  "count": 20,
  "schema": "samples",
  "total_available": "Run without --limit to see all"
}
```

## API Endpoint

`POST /v2/getsqlresult?sql=<query>&cxn=<connection>`

## Limitations

- Requires read-only access to INFORMATION_SCHEMA tables
- Default limit is 20 for readability - increase with --limit flag
- Schema must exist and be accessible to the connection user
- If INFORMATION_SCHEMA queries fail, user may need to check credentials/permissions

## Troubleshooting

If you get an error about INFORMATION_SCHEMA not found:
- Check that the schema name is correct
- Verify your connection has access to that schema
- Try a different schema or check with your DBA

If no tables appear:
- The schema may be empty
- Try removing --limit to see if there are tables
- Check the schema name is correct (case-sensitive for some databases)

## Alternative: Manual Table Reference Lists

If INFORMATION_SCHEMA is not accessible (no read permissions, restricted database, etc.), you can create a manual reference:

### In your project's CLAUDE.md:
```
# Table Reference
- samples.accounts - User account data
- samples.orders - Order history
- samples.customers - Customer profiles
```

### Or a dedicated doc like docs/tables.md:
```markdown
# Database Tables

## samples schema
| Table | Description |
|-------|-------------|
| accounts | User financial accounts |
| orders | Transaction orders |
| customers | Customer master data |
```

This allows Claude to help you find tables even without direct database access.