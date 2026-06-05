# Local Linux VM Setup

Any Linux VM with Docker installed. Uses the same compose file as Cloud Shell.

## Prerequisites

```bash
docker --version
docker compose version
```

## Start

```bash
# Clone or copy the SMOKE_TEST directory, then:
cd SMOKE_TEST
docker compose up -d

# Load sample data
docker compose exec db psql -U postgres -d postgres -c "
  CREATE TABLE items (id SERIAL PRIMARY KEY, name TEXT NOT NULL);
  INSERT INTO items (name) VALUES ('foo'), ('bar'), ('baz');
"

# Verify
curl http://localhost:3000/items
```

## DQ Web

```bash
# Create postgres role
docker compose exec db psql -U postgres -d postgres -c \
  "CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'password';" 2>/dev/null || true

# Run DQ Web
bash dq-web/dq-web-run.sh
```

## host.docker.internal on Linux

On Linux, `host.docker.internal` is not available by default. Use `--add-host`:

```bash
docker run --add-host=host.docker.internal:host-gateway ...
```

This resolves to the Docker bridge gateway (typically `172.17.0.1`). If that doesn't work, find the actual gateway:

```bash
docker network inspect bridge --format='{{(index .IPAM.Config 0).Gateway}}'
# → 172.17.0.1
```

Then use that IP in `SPRING_DATASOURCE_URL`.

## Run a job

```bash
pip install duckdb postgrest
python3 scripts/run_job.py --dataset demo_test
python3 scripts/test_connection.py
```

## Teardown

```bash
docker compose down -v
docker kill dq-web; docker rm dq-web
```