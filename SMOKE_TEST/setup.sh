#!/usr/bin/env bash
# All-in-one setup for Cloud Shell
# Run this from your local machine (not inside Cloud Shell)
set -euo pipefail

echo "=== 1. Push docker-compose.yml to Cloud Shell ==="
gcloud cloud-shell ssh --command="cat > ~/docker-compose.yml" --authorize-session < "$(dirname "$0")/docker-compose.yml"

echo "=== 2. Create postgres role (needed for r/w validation schema) ==="
gcloud cloud-shell ssh --command="docker compose -f ~/docker-compose.yml exec -T db psql -U postgres -d postgres -c \"CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'password';\"" --authorize-session 2>/dev/null || true

echo "=== 3. Start PostgreSQL + PostgREST ==="
gcloud cloud-shell ssh --command="docker compose -f ~/docker-compose.yml up -d" --authorize-session

echo "=== 4. Load sample data ==="
gcloud cloud-shell ssh --command="docker compose -f ~/docker-compose.yml exec -T db psql -U postgres -d postgres -c \"
CREATE TABLE items (id SERIAL PRIMARY KEY, name TEXT NOT NULL, created_at TIMESTAMPTZ DEFAULT now());
INSERT INTO items (name) VALUES ('foo'), ('bar'), ('baz');
\"" --authorize-session

echo "=== 5. Verify ==="
gcloud cloud-shell ssh --command="curl -s http://localhost:3000/items" --authorize-session

echo "=== 6. Set up keepalive (prevent 20-min idle timeout) ==="
gcloud cloud-shell ssh --command="nohup bash -c 'while true; do curl -s http://localhost:3000 > /dev/null; sleep 300; done' > /dev/null 2>&1 &" --authorize-session

echo "=== 7. Start SSH tunnel (Ctrl+C to kill) ==="
echo "    Ports: 5432 (PG), 3000 (PostgREST), 9000 (DQ Web)"
gcloud cloud-shell ssh \
  --ssh-flag="-L" --ssh-flag="5432:localhost:5432" \
  --ssh-flag="-L" --ssh-flag="3000:localhost:3000" \
  --ssh-flag="-L" --ssh-flag="9000:localhost:9000" \
  --command="sleep 3600" \
  --authorize-session &

echo ""
echo "Setup complete! Test with:"
echo "  curl http://localhost:3000/items"
echo "  python3 scripts/test_connection.py"
echo "  python3 scripts/run_job.py --dataset demo_test"