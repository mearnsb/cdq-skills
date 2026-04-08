---
name: cdq-get-results
description: Retrieve DQ job results (hoot results) including scores and rule outcomes. Use when: (1) Getting DQ score for a completed job, (2) Viewing per-rule results, (3) Checking pass/fail counts, (4) Examining finding details.
---

# CDQ Get Results

Retrieve the results of a DQ job run (hoot results).

## Usage

```bash
python lib/client.py get-results --dataset "schema.table" --run-id "2025-03-09"
```

## Alternative (curl)

```bash
source .env && TOKEN=$(curl -sk -X POST "${DQ_URL}/auth/signin" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${DQ_USERNAME}\",\"password\":\"${DQ_PASSWORD}\",\"iss\":\"${DQ_ISS}\"}" | jq -r '.token')

curl -sk "${DQ_URL}/v2/gethoot?dataset=schema.table&runId=2025-03-09" \
  -H "Authorization: Bearer $TOKEN"
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--dataset` | Yes | Dataset name |
| `--run-id` | Yes | Run ID (typically a date like 2025-03-09) |

## Examples

```bash
# Get results for specific run
python lib/client.py get-results --dataset "samples.nyse_categorical" --run-id "2025-03-09"

# Get results for today's run
python lib/client.py get-results --dataset "my_dataset.customers" --run-id "$(date +%Y-%m-%d)"
```

## Output

Returns JSON with detailed DQ results including:
- Overall score
- Per-rule results
- Pass/fail counts
- Finding details

## API Endpoint

`GET /v2/gethoot?dataset=<name>&runId=<date>`

## Related

- `cdq-get-recent-runs` - Find recent run IDs