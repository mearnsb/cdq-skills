---
name: cdq-search-catalog
description: Search registered datasets in the Collibra DQ catalog. Use when: (1) Finding available datasets, (2) Discovering dataset names and metadata, (3) Checking if a dataset already exists before creating, (4) Getting dataset connection info.
---

# CDQ Search Catalog

Search the data catalog to find registered datasets.

> **Note:** This searches **registered datasets** in CDQ, not the underlying database tables. Datasets are logical entities with names like `MY_DATASET`, `DEMO_JOB`, or `schema.table`. Use this to discover what datasets exist and their metadata.
>
> This can also be used to check for existing jobs before creating a new one to avoid duplicates — query by dataset name to see if it's already registered.

## Usage

```bash
python lib/client.py search-catalog --query "search_term" --limit 20
```

## Alternative (curl)

```bash
source .env && TOKEN=$(curl -sk -X POST "${DQ_URL}/auth/signin" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${DQ_USERNAME}\",\"password\":\"${DQ_PASSWORD}\",\"iss\":\"${DQ_ISS}\"}" | jq -r '.token')

curl -sk "${DQ_URL}/v2/getdataassetsarrforserversidewithmultifilters?draw=3&start=0&length=20&search[value]=&filterSource=${DQ_CXN}" \
  -H "Authorization: Bearer $TOKEN"
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--query` | Yes | Search query string (empty string for all) |
| `--limit` | No | Maximum results (default: 50) |
| `--connection` | No | Filter by connection (default: $DQ_CXN) |

## Examples

```bash
# List all registered datasets
python lib/client.py search-catalog --query "" --limit 100

# Search for specific datasets
python lib/client.py search-catalog --query "customer"

# Search with specific connection
python lib/client.py search-catalog --query "sales" --connection SNOWFLAKE
```

## Output

Returns JSON with:
- `recordsTotal` - Total number of datasets
- `recordsFiltered` - Number matching filter
- `dataAssetList` - Array of datasets with:
  - `dataset` - Logical dataset name
  - `dbNm` - Database name (if applicable)
  - `tableNm` - Table name (if applicable)
  - `source` - Source system
  - `connectionName` - Connection used
  - `ruleCnt` - Number of rules attached
  - `alertCnt` - Number of alerts configured
  - `lastRun` - Last execution timestamp
  - `updtTs` - Last updated timestamp

## API Endpoint

`GET /v2/getdataassetsarrforserversidewithmultifilters`

## Related

- Use dataset names from results with `get-rules`, `get-results`, `save-rule`, etc.