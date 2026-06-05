# Tunnel Options

PostgreSQL, PostgREST, and DQ Web ports are firewalled in Cloud Shell. Use tunnels to access them.

## Option A: SSH Tunnel (local machine only)

Forwards Cloud Shell VM ports to your local machine.

```bash
# Three ports at once
gcloud cloud-shell ssh \
  --ssh-flag="-L" --ssh-flag="5432:localhost:5432" \
  --ssh-flag="-L" --ssh-flag="3000:localhost:3000" \
  --ssh-flag="-L" --ssh-flag="9000:localhost:9000" \
  --command="sleep 3600" \
  --authorize-session &
```

Tunnel stays open for 1 hour. Verify:

```bash
curl http://localhost:3000/items
python3 -c "import socket; s=socket.socket(); s.settimeout(3); s.connect(('localhost',5432)); s.close(); print('PG OK')"
curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/
```

## Option B: Cloudflare Tunnel (anywhere, no account)

Public URL accessible from any machine.

```bash
# In Cloud Shell:
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O ~/cloudflared
chmod +x ~/cloudflared
nohup ~/cloudflared tunnel --url http://localhost:3000 > /tmp/cloudflared.log 2>&1 &
sleep 8
grep -o 'https://[a-zA-Z0-9.-]*\.trycloudflare\.com' /tmp/cloudflared.log | head -1
```

Test from anywhere:

```bash
curl https://your-url.trycloudflare.com/items
```

URL changes on restart. Ngrok paid plan for fixed subdomain.

## Port Summary

| Port | Service | Tunnel | Notes |
|------|---------|--------|-------|
| 5432 | PostgreSQL | SSH only | Direct DB access |
| 3000 | PostgREST | SSH + CF | REST API (public + validation schemas) |
| 9000 | DQ Web | SSH + CF | Spring Boot login page |