---
name: cdq-test-connection
description: Test connection to the Collibra DQ API. Use when: (1) Verifying API credentials are correct, (2) Troubleshooting connection issues, (3) Checking if DQ server is reachable.
---

# CDQ Test Connection

Test connection to the Collibra DQ API.

## Usage

```bash
python lib/client.py test-connection
```

## Parameters

None - tests connection using configured credentials.

## Examples

```bash
# Test API connection
python lib/client.py test-connection
```

## Output

Returns JSON with:
- `success`: Boolean indicating if connection succeeded
- `message`: Status message

## API Endpoint

`POST /auth/signin`

## Notes

- Uses credentials from `.env` file (DQ_URL, DQ_USERNAME, DQ_PASSWORD, DQ_ISS)
- Tests authentication by attempting to get a token
- Good first step before running any other commands

## Related

- All other CDQ skills - require working connection