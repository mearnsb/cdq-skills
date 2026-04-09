---
name: cdq-save-alert
description: Create a new alert for a dataset in Collibra DQ. Use when: (1) Creating email notifications for DQ score thresholds, (2) Setting up alerts for rule failures, (3) Configuring condition-based notifications, (4) Monitoring specific metrics.
---

# CDQ Save Alert

Create a new alert that triggers when conditions are met.

> **Note:** The `--dataset` parameter uses the **logical dataset name** registered in CDQ (e.g., `MY_DATASET`, `DEMO_JOB`), not necessarily a `schema.table`. Alerts attach to datasets by their logical name.

## Usage

```bash
python lib/client.py save-alert \
  --dataset "DATASET_NAME" \
  --name "Alert Name" \
  --condition "score < 90" \
  --email "team@company.com"
```

## Alternative (curl)

```bash
source .env && TOKEN=$(curl -sk -X POST "${DQ_URL}/auth/signin" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${DQ_USERNAME}\",\"password\":\"${DQ_PASSWORD}\",\"iss\":\"${DQ_ISS}\"}" | jq -r '.token')

curl -sk -X POST "${DQ_URL}/v3/alerts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset": "DATASET_NAME",
    "alertNm": "Low Score Alert",
    "alertCond": "score < 90",
    "alertFormat": "EMAIL",
    "alertFormatValue": "team@company.com",
    "alertMsg": "Low score alert",
    "active": true
  }'
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--dataset` | Yes | Dataset name (logical name registered in CDQ) |
| `--name` | Yes | Alert name |
| `--condition` | Yes | Alert condition expression |
| `--email` | Yes | Email address for notifications |
| `--message` | No | Custom alert message |

## Examples

```bash
# Alert on low DQ score
python lib/client.py save-alert \
  --dataset "MY_DATASET" \
  --name "Customer DQ Alert" \
  --condition "score < 85" \
  --email "dq-team@company.com"

# Alert on specific rule failure
python lib/client.py save-alert \
  --dataset "ORDERS_DATASET" \
  --name "Order Check Failure" \
  --condition "rule_failed('Unique Order ID')" \
  --email "alerts@company.com" \
  --message "Order uniqueness check failed"

# Alert with custom message
python lib/client.py save-alert \
  --dataset "INVENTORY" \
  --name "Inventory Alert" \
  --condition "score < 90" \
  --email "inventory-team@company.com" \
  --message "Inventory DQ score dropped below threshold"
```

## Condition Examples

- `score < 90` - Alert when DQ score drops below threshold
- `rule_failed('Rule Name')` - Alert when specific rule fails
- `completeness < 95` - Alert on completeness metric
- `accuracy < 80` - Alert on accuracy metric

## Output

Returns JSON with created alert details.

## API Endpoint

`POST /v3/alerts`

## Related

- Use `get-alerts` to see existing alerts
- Alerts trigger after jobs complete - run jobs with `run-dq-job`