# Adaptations

The `duckdq` pip package is **not needed**. Everything in this directory is self-contained.

## What changed

The `duckdq` pip package uses `supabase` under the hood, which is incompatible with raw PostgREST v14 (different URL paths, API key validation, auth endpoints).

Instead, `client.py` at the root of this directory provides `DQClient` — a standalone 120-line class that talks directly to PostgREST via `SyncPostgrestClient`. Same register/run workflow, zero Supabase dependency.

## Requirements

```bash
pip install -r requirements.txt
# → installs: duckdb, postgrest
```

That's it. No `pip install duckdq` needed.

## If you still want the original duckdq package

The pip package is `duckdq` v0.0.7. Its `client.py` lives at:
`site-packages/duckdq/client.py`

But the DQClient in `client.py` here is a complete replacement — same method signatures, direct PostgREST, no Supabase overhead.