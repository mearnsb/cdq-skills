---
name: cdq-get-dataset
description: Retrieve dataset configuration and metadata from Collibra DQ. Use when: (1) Getting dataset definition details, (2) Finding connection settings, (3) Viewing source query for a dataset, (4) Checking schedule information.
---

# CDQ Get Dataset

Retrieve the configuration/definition for a dataset.

## Usage

```bash
python lib/client.py get-dataset --dataset "schema.table"
```

## Alternative (curl)

```bash
source .env && TOKEN=$(curl -sk -X POST "${DQ_URL}/auth/signin" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${DQ_USERNAME}\",\"password\":\"${DQ_PASSWORD}\",\"iss\":\"${DQ_ISS}\"}" | jq -r '.token')

curl -sk "${DQ_URL}/v2/owl-options/get?dataset=schema.table" \
  -H "Authorization: Bearer $TOKEN"
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--dataset` | Yes | Dataset name |

## Examples

```bash
# Get dataset definition
python lib/client.py get-dataset --dataset "samples.nyse_categorical"

# Get definition for specific dataset
python lib/client.py get-dataset --dataset "my_project.my_dataset.customers"
```

## Output

Returns JSON with dataset configuration including:
- Connection settings
- Source query
- Schedule information
- Profile settings

## API Endpoint

`GET /v2/owl-options/get?dataset=<name>`