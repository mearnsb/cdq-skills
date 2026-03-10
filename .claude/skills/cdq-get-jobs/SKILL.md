---
name: cdq-get-jobs
description: List queued and running DQ jobs in the Collibra DQ platform. Use when: (1) Checking the status of DQ jobs, (2) Finding pending/running jobs, (3) Monitoring job queue, (4) Getting run IDs for recent jobs.
---

# CDQ Get Jobs

List DQ jobs currently in the queue.

## Usage

```bash
python lib/client.py get-jobs
python lib/client.py get-jobs --status "running" --limit 20
```

## Alternative (curl)

```bash
source .env && TOKEN=$(curl -sk -X POST "${DQ_URL}/auth/signin" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${DQ_USERNAME}\",\"password\":\"${DQ_PASSWORD}\",\"iss\":\"${DQ_ISS}\"}" | jq -r '.token')

curl -sk "${DQ_URL}/v2/getowlcheckq?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--status` | No | Filter by status (empty for all) |
| `--limit` | No | Maximum results (default: 10) |

## Examples

```bash
# List all jobs in queue
python lib/client.py get-jobs

# List running jobs
python lib/client.py get-jobs --status "running"

# List recent jobs
python lib/client.py get-jobs --limit 50
```

## Output

Returns JSON with job information including:
- Dataset name
- Run ID
- Status (pending, running, completed, failed)

## API Endpoint

`GET /v2/getowlcheckq`

## Related

- `cdq-get-recent-runs` - Get recently completed runs