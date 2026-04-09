---
name: cdq-get-alerts
description: Retrieve alerts configured for a dataset in Collibra DQ. Use when: (1) Viewing existing alerts for a dataset, (2) Checking alert conditions and notification settings, (3) Finding active/inactive alerts.
---

# CDQ Get Alerts

Retrieve alerts configured for a specific dataset.

> **Note:** The `--dataset` parameter uses the **logical dataset name** registered in CDQ (e.g., `MY_DATASET`, `DEMO_JOB`), not necessarily a `schema.table`.

## Usage

```bash
python lib/client.py get-alerts --dataset "DATASET_NAME"
```

## Alternative (curl)

```bash
source .env && TOKEN=$(curl -sk -X POST "${DQ_URL}/auth/signin" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${DQ_USERNAME}\",\"password\":\"${DQ_PASSWORD}\",\"iss\":\"${DQ_ISS}\"}" | jq -r '.token')

curl -sk "${DQ_URL}/v2/getalerts?dataset=DATASET_NAME" \
  -H "Authorization: Bearer $TOKEN"
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--dataset` | Yes | Dataset name (logical name) |

## Examples

```bash
# Get all alerts for a dataset
python lib/client.py get-alerts --dataset "MY_DATASET"

# Get alerts using schema-like name
python lib/client.py get-alerts --dataset "samples.nyse_categorical"

# Find dataset names via search-catalog
python lib/client.py search-catalog --query "" --limit 50
```

## Output

Returns JSON array of alerts including:
- Alert name
- Condition expression
- Email/notification settings
- Active status

## API Endpoint

`GET /v2/getalerts?dataset=<name>`