---
name: cdq-get-rules
description: Retrieve Data Quality rules configured for a dataset in Collibra DQ. Use when: (1) Listing rules for a dataset, (2) Checking existing rule definitions, (3) Finding rule types and SQL expressions, (4) Verifying rules before saving new ones.
---

# CDQ Get Rules

Retrieve Data Quality rules configured for a specific dataset.

> **Note:** The `--dataset` parameter uses the **logical dataset name** registered in CDQ, not necessarily a `schema.table`. Datasets can have names like `DEMO_JOB`, `TEST_RUN`, or `my_dataset`.

## Usage

After `pip install -e .`, run:
```bash
cdq-get-rules --dataset "DATASET_NAME"
```

Or directly from skill directory:
```bash
cdq-get-rules --dataset "DATASET_NAME"
```

## Alternative (curl)

```bash
source .env && TOKEN=$(curl -sk -X POST "${DQ_URL}/auth/signin" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${DQ_USERNAME}\",\"password\":\"${DQ_PASSWORD}\",\"iss\":\"${DQ_ISS}\"}" | jq -r '.token')

curl -sk "${DQ_URL}/v3/rules/DATASET_NAME" \
  -H "Authorization: Bearer $TOKEN"
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--dataset` | Yes | Dataset name (logical name, e.g., `MY_DATASET` or `samples.nyse_categorical`) |
| `--limit` | No | Limit number of rules returned (default: all rules) |

## Examples

```bash
# Get rules using logical dataset name
cdq-get-rules --dataset "MY_DATASET"

# Get rules for a dataset named like schema.table
cdq-get-rules --dataset "samples.nyse_categorical"

# Limit results to first 10 rules
cdq-get-rules --dataset "MY_DATASET" --limit 10

# Find dataset names via search-catalog
cdq-search-catalog --query "" --limit 50
```

## Output

Returns JSON array of rule definitions including:
- `ruleNm` - Rule name
- `ruleType` - Type (SQLF, etc.)
- `ruleValue` - SQL expression
- `points` - Point value
- `perc` - Percentage threshold
- `isActive` - Active status

## API Endpoint

`GET /v3/rules/{dataset}`