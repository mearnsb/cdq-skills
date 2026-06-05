# SMOKE TEST — Ephemeral PostgREST + DQ Web Stack

End-to-end smoke test environment: PostgreSQL → PostgREST → DQ Web + Python job runner. Spins up in minutes on Cloud Shell or any Linux VM, tears down cleanly.

## Architecture

```
┌────────────────────────────────────────────────┐
│          Cloud Shell VM / Linux Host            │
│                                                  │
│  ┌──────────┐      ┌──────────────┐             │
│  │PostgreSQL│◄─────│  PostgREST   │             │
│  │ :5432    │      │  :3000       │             │
│  │          │      │  schemas:    │             │
│  │  db:     │      │  - public    │             │
│  │  postgres│      │  - validation│             │
│  └────┬─────┘      └──────┬───────┘             │
│       │                   │                     │
│       │                   │                     │
│  ┌────▼───────────────────▼────────┐            │
│  │        DQ Web :9000             │            │
│  │  (connects via                  │            │
│  │   host.docker.internal:5432)    │            │
│  └────────────────────────────────┘            │
│                                                  │
│  ┌──────────────────────────────┐               │
│  │  Cloudflare tunnel (optional)│               │
│  │  → trycloudflare.com         │               │
│  └──────────────────────────────┘               │
└──────────────┬──────────────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
 SSH tunnel  Cloudflare  Direct
 (this PC)   (anywhere)  (VM only)
 localhost    .com/items  localhost:3000
```

## Files

| File | Purpose |
|------|---------|
| **Core** | |
| `docker-compose.yml` | PostgreSQL + PostgREST — single file, two containers |
| `client.py` | Standalone DQClient class — replaces `duckdq` pip package |
| `setup.sh` | All-in-one Cloud Shell quickstart |
| `requirements.txt` | Minimal deps: `duckdb` + `postgrest` |
| **Scripts** | |
| `scripts/run_job.py` | Register + run a DQ job (`--dataset`, `--run-id`, `--csv`) |
| `scripts/test_connection.py` | Verify PostgREST is healthy and schemas are accessible |
| **DQ Web** | |
| `dq-web/dq-web.env` | All env vars for the DQ Web container |
| `dq-web/dq-web-run.sh` | One-command docker run for DQ Web |
| `dq-web/env-demo.txt` | Original env file format (reference) |
| **Data** | |
| `data/fake_customers.csv` | Sample 10-row dataset |
| **Guides** | |
| `guides/cloud-shell.md` | Google Cloud Shell walkthrough |
| `guides/local-linux.md` | Any Linux VM with Docker |
| `guides/tunnel.md` | SSH tunnel + Cloudflare tunnel setup |
| `guides/colab.md` | Google Colab (no Docker, manual installs) |
| **Reference** | |
| `reference/ADAPTATIONS.md` | Why duckdq isn't needed — replaced by client.py |

## Quick Start

### 1. Start PostgreSQL + PostgREST

```bash
docker compose up -d
```

### 2. Create postgres superuser (required for DQ tables)

```bash
docker compose exec db psql -U postgres -d postgres -c \
  "CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'password';" 2>/dev/null || true
```

### 3. Load sample data

```bash
docker compose exec db psql -U postgres -d postgres -c "
  CREATE TABLE items (id SERIAL PRIMARY KEY, name TEXT NOT NULL, created_at TIMESTAMPTZ DEFAULT now());
  INSERT INTO items (name) VALUES ('foo'), ('bar'), ('baz');
"
```

### 4. Verify

```bash
curl http://localhost:3000/items
# → [{"id":1,"name":"foo",...},...]
```

### 5. Install dependencies (only 2 packages needed)

```bash
pip install -r requirements.txt
# → duckdb, postgrest
```

No `pip install duckdq` needed — everything is self-contained in `client.py`.

### 6. Run a DQ job

```bash
# Using the standalone script
python3 scripts/run_job.py --dataset demo_test
python3 scripts/run_job.py --dataset another_test --run-id "2026-05-19"

# Or using client.py directly in your own code
python3 -c "
from client import DQClient
from postgrest import SyncPostgrestClient
import duckdb
conn = duckdb.connect(':memory:')
conn.execute('CREATE TABLE t AS SELECT 1 AS x')
dq = DQClient(SyncPostgrestClient('http://localhost:3000'), conn)
dq.register('my_data')
dq.run('my_data', '2026-05-19')
print('done')
"

# Verify connectivity
python3 scripts/test_connection.py
```

### 6. (Optional) DQ Web

```bash
bash dq-web/dq-web-run.sh
# Wait ~50s for Spring Boot, then:
curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/
# → 302 (redirect to login page)
```

### 7. (Optional) SSH tunnel (Cloud Shell)

```bash
gcloud cloud-shell ssh \
  --ssh-flag="-L" --ssh-flag="5432:localhost:5432" \
  --ssh-flag="-L" --ssh-flag="3000:localhost:3000" \
  --ssh-flag="-L" --ssh-flag="9000:localhost:9000" \
  --command="sleep 3600" --authorize-session &
```

### 8. (Optional) Cloudflare tunnel (public, no account)

```bash
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
./cloudflared-linux-amd64 tunnel --url http://localhost:3000
# → https://xxxx.trycloudflare.com
```

## Schema Layout

All DQ tables live in the `validation` schema of the `postgres` database:

| Table | Purpose |
|-------|---------|
| `dataset_scan` | Overall job scan result (score, row count) |
| `dataset_field` | Per-column profile (nulls, uniqueness, min/max) |
| `dataset_schema` | Column-level schema types |
| `dataset_activity` | Job timing breakdown |
| `owl_catalog` | Dataset metadata (source, DB, table) |
| `owl_check_history` | Execution history per run |
| `owl_rule` | Defined quality rules |
| `rule_output` | Per-rule results |
| `opt_*` | Configuration tables (spark, pushdown, profile, load, env, owl) |
| `dq_inbox` | Quality issue notifications |
| `assignment_q` | Rule/alert assignments |
| `data_preview` | Sample break-record data |
| `connections` | Connection definitions |

PostgREST access pattern:

```python
from postgrest import SyncPostgrestClient
pg = SyncPostgrestClient("http://localhost:3000")

# Public schema (items table)
pg.from_("items").select("*").execute()

# Validation schema (DQ tables) — uses Accept-Profile header
pg.schema("validation").from_("dataset_scan").select("*").execute()
pg.schema("validation").from_("dataset_field").select("*").eq("dataset", "demo_test").execute()
```

## run_job.py Usage

```bash
# Minimal (inline 5-row data)
python3 scripts/run_job.py --dataset my_test

# With explicit run ID (yyyy-MM-dd format)
python3 scripts/run_job.py --dataset my_test --run-id "2026-05-19"

# From CSV
python3 scripts/run_job.py --dataset customers --csv data/fake_customers.csv

# Limit rows from CSV
python3 scripts/run_job.py --dataset customers --csv data/fake_customers.csv --rows 5

# Custom API URL
python3 scripts/run_job.py --dataset my_test --api-url http://localhost:3000
```

The script:
1. Loads data into DuckDB (inline VALUES or CSV via `read_csv_auto`)
2. Runs `SUMMARIZE` to profile columns
3. Calls `register()` → upserts into `opt_*` config tables
4. Calls `run()` → upserts into `owl_*`, `dataset_*`, `rule_output` tables
5. Verifies data is readable back from PostgREST

## PostgREST API Details

### Version
- Running: **PostgREST v14.11**
- Multi-schema via `PGRST_DB_SCHEMAS: public,validation`
- Schema switching via HTTP headers: `Accept-Profile: validation`, `Content-Profile: validation`

### Authentication

This PostgREST instance uses `PGRST_DB_ANON_ROLE: postgres` — no JWT needed for anonymous access. The `SyncPostgrestClient` used by `client.py` and `run_job.py` works without any auth headers.

**If you need a JWT** (e.g., to test Supabase client compatibility), generate one signed with the JWT secret:

```bash
pip install pyjwt
python3 -c "
import jwt
payload = {'role': 'anon', 'iss': 'supabase'}
secret = 'this-is-a-long-enough-secret-key-for-testing-12345'
anon_key = jwt.encode(payload, secret, algorithm='HS256')
print(anon_key)
"
```

This produces a valid Supabase-format anon key (`eyJ...`). The Supabase Python client will accept it:

```python
import os
from supabase import create_client
os.environ["API_URL"] = "http://localhost:3000"
os.environ["API_KEY"] = "<generated-key>"
client = create_client(os.environ["API_URL"], os.environ["API_KEY"])
```

**Why you don't need this for the smoke test:** The `DQClient` in `client.py` uses `SyncPostgrestClient` directly, which talks to raw PostgREST without any Supabase wrapping. No JWT, no GoTrue auth, no `/rest/v1` path prefix.

**Why you might want it:** If you're testing the `duckdq` pip package itself (which uses Supabase internally), you'll need the JWT-key to get past Supabase's API key validation at `create_client()`.

### Key URLs
| URL | Schema | Description |
|-----|--------|-------------|
| `GET /items` | public | Sample items table |
| `GET /validation/dataset_scan` | validation | Requires `Accept-Profile` header |
| `GET /validation/dataset_field` | validation | Requires `Accept-Profile` header |
| `GET /` | — | OpenAPI description (Swagger) |

## Environment Variables

### docker-compose.yml

| Variable | Value | Notes |
|----------|-------|-------|
| `POSTGRES_DB` | `postgres` | Default database name |
| `POSTGRES_USER` | `postgres` | Superuser |
| `POSTGRES_PASSWORD` | `password` | Superuser password |
| `PGRST_DB_URI` | `postgres://postgres:password@db:5432/postgres` | PostgREST connection string |
| `PGRST_DB_SCHEMAS` | `public,validation` | Schemas exposed via REST |
| `PGRST_DB_ANON_ROLE` | `postgres` | Role for unauthenticated requests |
| `PGRST_JWT_SECRET` | `this-is-a-long-enough-secret-key-for-testing-12345` | Must be ≥32 characters |

### DQ Web

See `dq-web/dq-web.env` for all variables. Key ones:

| Variable | Value | Purpose |
|----------|-------|---------|
| `SPRING_DATASOURCE_URL` | `jdbc:postgresql://host.docker.internal:5432/postgres` | Metastore connection |
| `SPRING_DATASOURCE_USERNAME` | `postgres` | DB user |
| `SPRING_DATASOURCE_PASSWORD` | `password` | DB password |
| `MULTITENANTMODE` | `TRUE` | Multi-tenant mode |
| `multiTenantSchemaHub` | `owlhub` | Schema for management model |
| `SERVER_HTTP_ENABLED` | `TRUE` | HTTP (not HTTPS) |
| `SPRING_FLYWAY_ENABLED` | `false` | Disable Flyway migrations |
| `DISABLENOAGENT` | `true` | Disable agent check |

## Port Summary

| Port | Service | Cloud Shell | Linux VM |
|------|---------|-------------|----------|
| 5432 | PostgreSQL | SSH tunnel only | Direct if ports open |
| 3000 | PostgREST | SSH tunnel or CF tunnel | Direct |
| 9000 | DQ Web | SSH tunnel or CF tunnel | Direct |

## Cloud Shell Caveats

| Constraint | Mitigation |
|------------|------------|
| **20-min idle timeout** | Keepalive loop: `while true; do curl -s localhost:3000 > /dev/null; sleep 300; done &` |
| **50h/week limit** | Use for short-lived smoke tests only |
| **Firewall blocks all ports** | SSH tunnel (`gcloud cloud-shell ssh -L`) or Cloudflare tunnel |
| **Tunnel URL changes** | Ephemeral; ngrok paid plan for fixed subdomain |
| **VM lifecycle** | Everything is Docker — full rebuild in ~2 minutes |
| **SSH tunnel expires** | Tied to `sleep 3600`; restart on new session |

## Teardown

```bash
# Docker cleanup
docker compose down -v
docker kill dq-web 2>/dev/null; docker rm dq-web 2>/dev/null

# Cloud Shell cleanup
gcloud cloud-shell ssh --command="
  docker compose -f ~/docker-compose.yml down -v
  docker kill dq-web 2>/dev/null; docker rm dq-web 2>/dev/null
  pkill -f cloudflared; pkill -f 'sleep 300'
  rm -f ~/docker-compose.yml ~/cloudflared /tmp/cloudflared.log
" --authorize-session

# Kill SSH tunnels locally
pkill -f 'gcloud cloud-shell ssh.*sleep 3600'
```

## Session History

This environment was built and tested on **2026-05-19**:

| Step | Status |
|------|--------|
| Cloud Shell SSH access | ✓ |
| Docker Compose (PostgreSQL 16 + PostgREST v14) | ✓ |
| JWT secret fix (32-char min requirement) | ✓ |
| Sample data (items table) | ✓ |
| Cloudflare tunnel | ✓ (melissa-still-res-noted.trycloudflare.com) |
| SSH tunnel (5432, 3000, 9000) | ✓ |
| DQ Web container (Spring Boot, 52s boot) | ✓ |
| PostgREST multi-schema (public + validation) | ✓ |
| duckdq smoke test (register + run + verify) | ✓ |
| `run_job.py` generic runner | ✓ |
| `demo_test` job | ✓ (score=100, 5 rows) |
| `quick_smoke_2` job | ✓ (score=100, 5 rows, run_id=2026-05-19) |