# PostgREST on Google Colab

**Note:** Colab has no Docker, so everything installs raw. More manual but works.

## Step 1: Install PostgreSQL

Run this cell:

```python
# Install PostgreSQL
!apt-get update -qq && apt-get install -y -qq postgresql postgresql-client > /dev/null 2>&1

# Start the service
!service postgresql start

# Create a user and database
!su - postgres -c "psql -c \"CREATE USER app WITH PASSWORD 'secret' SUPERUSER;\""
!su - postgres -c "psql -c \"CREATE DATABASE api OWNER app;\""

print("PostgreSQL ready")
```

## Step 2: Install PostgREST binary

```python
import os, urllib.request, tarfile

# Download latest PostgREST Linux binary
url = "https://github.com/PostgREST/postgrest/releases/latest/download/postgrest-v12.2.1-linux-x86_64.tar.xz"
urllib.request.urlretrieve(url, "postgrest.tar.xz")

# Extract
import tarfile
with tarfile.open("postgrest.tar.xz", "r:xz") as tar:
    tar.extractall()

# Make executable
!chmod +x postgrest

print("PostgREST binary ready")
```

## Step 3: Create a config file

```python
config = """
db-uri = "postgres://app:secret@localhost:5432/api"
db-schema = "public"
db-anon-role = "app"
jwt-secret = "test-secret-change-me"
server-port = 3000
"""

with open("postgrest.conf", "w") as f:
    f.write(config)
```

## Step 4: Load sample data

```python
!su - postgres -c "psql -d api -c \"
  CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
  );
  INSERT INTO items (name) VALUES ('foo'), ('bar'), ('baz');
\""

print("Sample data loaded")
```

## Step 5: Start PostgREST

```python
import subprocess, time

proc = subprocess.Popen(
    ["./postgrest", "postgrest.conf"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

time.sleep(2)

# Test locally
!curl -s http://localhost:3000/items | python3 -m json.tool
```

You should see the three items as JSON.

## Step 6: Expose via tunnel

### Option A: ngrok

```python
# Download ngrok
!wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
!tar xzf ngrok-v3-stable-linux-amd64.tgz

# Auth (get your token from https://dashboard.ngrok.com)
!./ngrok config add-authtoken YOUR_TOKEN

# Start tunnel in background
import subprocess
ngrok_proc = subprocess.Popen(
    ["./ngrok", "http", "3000", "--log=stdout"],
    stdout=subprocess.PIPE
)

time.sleep(3)

# Get the public URL
import json, urllib.request
resp = urllib.request.urlopen("http://localhost:4040/api/tunnels")
tunnels = json.loads(resp.read())
print("Public URL:", tunnels["tunnels"][0]["public_url"])
```

### Option B: Cloudflare Tunnel

```python
# Download cloudflared
!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
!chmod +x cloudflared-linux-amd64

# Start tunnel
import subprocess
cf_proc = subprocess.Popen(
    ["./cloudflared-linux-amd64", "tunnel", "--url", "http://localhost:3000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT
)

time.sleep(5)

# The URL will be in the output — check cf_proc.stdout
# Or just look at the cell output for "trycloudflare.com"
```

## Step 7: Test from Python

```python
!pip install -q postgrest httpx
```

```python
from postgrest import PostgrestClient

client = PostgrestClient("https://xxxx.ngrok-free.app")  # or trycloudflare URL
data = client.from_("items").select("*").execute()
print(data)
```

## Caveats

- **No Docker** — manual binary install, more to go wrong
- **Colab runtime resets** — everything gone after ~12h or disconnect
- **No persistence** — re-run all steps on reconnect
- **ngrok/cloudflared binary each time** — re-download on fresh runtime
- Works for demos/smoke tests, not dev work