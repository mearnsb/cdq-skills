# Cloud Shell Setup

Google Cloud Shell gives a free VM with Docker pre-installed (50h/week limit, 20-min idle timeout).

## Quick start

```bash
# Push compose file and setup
gcloud cloud-shell ssh --command="cat > ~/docker-compose.yml" --authorize-session < ../docker-compose.yml
gcloud cloud-shell ssh --command="docker compose -f ~/docker-compose.yml up -d" --authorize-session
```

## SSH tunnel (access ports locally)

```bash
gcloud cloud-shell ssh \
  --ssh-flag="-L" --ssh-flag="5432:localhost:5432" \
  --ssh-flag="-L" --ssh-flag="3000:localhost:3000" \
  --ssh-flag="-L" --ssh-flag="9000:localhost:9000" \
  --command="sleep 3600" \
  --authorize-session &
```

## Keepalive

```bash
gcloud cloud-shell ssh --command="nohup bash -c 'while true; do curl -s http://localhost:3000 > /dev/null; sleep 300; done' > /dev/null 2>&1 &" --authorize-session
```

## Cloudflare tunnel (public URL, no account needed)

```bash
gcloud cloud-shell ssh --command="
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O ~/cloudflared
chmod +x ~/cloudflared
nohup ~/cloudflared tunnel --url http://localhost:3000 > /tmp/cloudflared.log 2>&1 &
sleep 8
grep -o 'https://[a-zA-Z0-9.-]*\.trycloudflare\.com' /tmp/cloudflared.log | head -1
" --authorize-session
```

## DQ Web

```bash
# Create postgres role (required by DQ Web)
gcloud cloud-shell ssh --command="docker compose -f ~/docker-compose.yml exec -T db psql -U postgres -d postgres -c \"CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'password';\"" --authorize-session 2>/dev/null || true

# Pull and run
gcloud cloud-shell ssh --command="
docker pull brianmearns162/dq-web:latest
docker run -d --name dq-web -p 9000:9005 --memory='4g' \
  --add-host=host.docker.internal:host-gateway \
  --env-file <(cat <<'EOF'
$(cat ../dq-web/dq-web.env)
EOF
) brianmearns162/dq-web:latest
" --authorize-session
```

## Teardown

```bash
gcloud cloud-shell ssh --command="
docker compose -f ~/docker-compose.yml down -v
docker kill dq-web 2>/dev/null; docker rm dq-web 2>/dev/null
pkill -f cloudflared; pkill -f 'sleep 300'
rm -f ~/docker-compose.yml ~/cloudflared /tmp/cloudflared.log
" --authorize-session
pkill -f 'gcloud cloud-shell ssh.*sleep 3600'
```