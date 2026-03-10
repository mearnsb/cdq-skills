---
name: cdq-get-recent-runs
description: Get recent DQ job run IDs and timestamps. Use when: (1) Finding run IDs for retrieving results, (2) Getting timestamps for recent job executions, (3) Identifying which dates have job data.
---

# CDQ Get Recent Runs

Get recent DQ job run IDs and timestamps.

## Usage

```bash
python lib/client.py get-recent-runs
```

## Parameters

None - returns all recent runs.

## Examples

```bash
# Get recent run IDs
python lib/client.py get-recent-runs
```

## Output

Returns JSON with recent run information including:
- Run ID (typically a date)
- Timestamp
- Dataset name
- Status

## API Endpoint

`GET /v2/getrecentruns`

## Related

- `cdq-get-results` - Get results for a specific run ID
- `cdq-get-jobs` - List queued/running jobs