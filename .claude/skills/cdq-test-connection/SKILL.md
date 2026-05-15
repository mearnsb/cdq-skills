---
name: cdq-test-connection
description: Test connection to the Collibra DQ API. Takes NO arguments — do not add any flags. Use when: (1) Verifying API credentials are correct, (2) Troubleshooting connection issues, (3) Checking if DQ server is reachable.
---

# CDQ Test Connection

> **TL;DR:** Verify credentials work. Run this first if any other command fails.

## Command

```bash
cdq test-connection
```

> ⚠️ **NO FLAGS** — this command takes zero arguments. Do not add any flags. Adding any flag will cause an error.

**Correct vs. incorrect usage:**
```
❌ cdq test-connection --url http://...   (WRONG — will error)
❌ cdq test-connection --user admin       (WRONG — will error)
✅ cdq test-connection                    (correct)
```

**Help output (no flags exist):**
```
usage: cdq test-connection [-h]

options:
  -h, --help  show this help message and exit
```

Reads `DQ_URL`, `DQ_USERNAME`, `DQ_PASSWORD`, `DQ_ISS` from `.env`.

## Output

```json
{"success": true, "message": "Connection successful"}
```

On failure: returns `success: false` with an error message — check your `.env` values.
