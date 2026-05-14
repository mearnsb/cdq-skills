---
name: cdq-save-rule
description: Create a new Data Quality rule for a dataset in Collibra DQ. Use when: (1) Adding DQ rules to check for data quality issues, (2) Creating completeness/validity checks, (3) Setting up uniqueness or range validations, (4) Defining custom SQL-based rules.
---

# CDQ Save Rule

Create a new Data Quality rule for a dataset.

> **Note:** The `--dataset` parameter uses the **logical dataset name** registered in CDQ, not necessarily a `schema.table`. Rules attach to datasets by their logical name (e.g., `MY_DATASET`, `DEMO_JOB`).

> **Rule SQL:** The `--sql` parameter defines what records represent failures. Any rows returned by the rule SQL count as DQ violations. Use the actual `schema.table` name in your rule SQL (NOT the `{dataset}` placeholder - it may not work with all connections like BigQuery).

## Usage

```bash
# Use actual schema.table in rule SQL (not {dataset} placeholder)
cdq-save-rule --dataset "DATASET_NAME" --name "Rule Name" --sql "SELECT * FROM schema.table WHERE col IS NULL"
```

## Alternative (curl)

```bash
source .env && TOKEN=$(curl -sk -X POST "${DQ_URL}/auth/signin" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${DQ_USERNAME}\",\"password\":\"${DQ_PASSWORD}\",\"iss\":\"${DQ_ISS}\"}" | jq -r '.token')

curl -sk -X POST "${DQ_URL}/v3/rules" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset": "DATASET_NAME",
    "ruleNm": "Rule Name",
    "ruleType": "SQLF",
    "ruleValue": "SELECT * FROM table WHERE col IS NULL",
    "points": 1,
    "perc": 10,
    "scoringScheme": 1
  }'
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--dataset` | Yes | - | Dataset name (logical name registered in CDQ) |
| `--name` | Yes | - | Rule name |
| `--sql` | Yes | - | SQL query - rows returned = failures |
| `--points` | No | 1 | Point value (optional) |
| `--perc` | No | 10 | Percentage threshold (default: 10) |
| `--scoring-scheme` | No | 1 | Scoring scheme: `0` = absolute, `1` = proportional (default: 1) |

## Usage

```bash
# Minimal (uses defaults: points=1, perc=10, scoring-scheme=1)
cdq-save-rule --dataset "DATASET_NAME" --name "Rule Name" --sql "SELECT * FROM schema.table WHERE col IS NULL"

# Custom scoring: absolute with custom points
cdq-save-rule --dataset "DATASET_NAME" --name "Rule Name" --sql "SELECT * FROM schema.table WHERE col IS NULL" --scoring-scheme 0 --points 5

# Custom scoring: proportional with higher threshold
cdq-save-rule --dataset "DATASET_NAME" --name "Rule Name" --sql "SELECT * FROM schema.table WHERE col IS NULL" --points 5 --perc 20
```

## Examples

```bash
# Completeness rule - check for null values
cdq-save-rule --dataset "MY_DATASET" --name "email_not_null" --sql "SELECT * FROM schema.table WHERE email IS NULL"

# Uniqueness rule
cdq-save-rule --dataset "ORDERS_DATASET" --name "unique_order_id" --sql "SELECT order_id, COUNT(*) as cnt FROM schema.table GROUP BY order_id HAVING COUNT(*) > 1"

# Range check
cdq-save-rule --dataset "PRODUCTS" --name "price_range_check" --sql "SELECT * FROM schema.table WHERE price < 0 OR price > 1000000"

# Cross-table reconciliation
cdq-save-rule --dataset "RECON_DATASET" --name "Source vs Target Match" --sql "SELECT * FROM source_table s FULL OUTER JOIN target_table t ON s.id = t.id WHERE s.id IS NULL OR t.id IS NULL"
```

## Rule SQL Tips

- Use actual `schema.table` name in your rule SQL (e.g., `samples.nyse_categorical`)
- Do NOT use `{dataset}` placeholder - it may not work with all connections (BigQuery returns syntax error)
- For cross-table queries, use actual `schema.table` names
- Any row returned counts as a failure
- Write SQL that identifies problematic records, not the count

## Output

Returns JSON with created rule details.

## API Endpoint

`POST /v3/rules`

## Related Workflow

1. Use `run-sql` to test your rule query first
2. Use `save-rule` to attach the rule to your dataset
3. Use `get-rules` to verify the rule was created