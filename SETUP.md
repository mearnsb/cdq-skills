# Setup Guide - CDQ Skills

Get started with Collibra Data Quality (CDQ) skills for Claude Code, Gemini CLI, and other AI platforms.

---

## Prerequisites

- **Python** 3.8 or later
- **pip** or conda for package management
- **Collibra DQ** instance with API access
- **API Credentials** (username, password, tenant ID)

---

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `python-dotenv` - Environment variable management
- `requests` - HTTP client library

---

## Step 2: Configure Environment

### Create .env File

```bash
cp .env.example .env
```

### Edit .env with Your Credentials

Open `.env` and fill in your Collibra DQ details:

```bash
# Collibra DQ API Configuration
DQ_URL=https://your-collibra-instance.com
DQ_USERNAME=your_username
DQ_PASSWORD=your_password
DQ_ISS=your_tenant_id
DQ_CXN=BIGQUERY          # or SNOWFLAKE, etc.
DQ_VERIFY_SSL=true       # false if using self-signed certificates
```

**Environment Variables Reference:**

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `DQ_URL` | Collibra DQ API base URL | `https://collibra.company.com` | Yes |
| `DQ_USERNAME` | Collibra username | `api_user@company.com` | Yes |
| `DQ_PASSWORD` | Collibra password | `YourSecurePassword123!` | Yes |
| `DQ_ISS` | Tenant identifier | `my_tenant` or `my-tenant-id` | Yes |
| `DQ_CXN` | Default database connection | `BIGQUERY`, `SNOWFLAKE`, etc. | No (default: BIGQUERY) |
| `DQ_VERIFY_SSL` | SSL certificate verification | `true` or `false` | No (default: true) |

---

## Step 3: Test Connection

Verify your setup works:

```bash
python lib/client.py test-connection
```

**Expected Output:**
```
Testing connection to Collibra DQ...
✓ Authentication successful
✓ API is reachable
✓ Connection verified
```

If this fails, see [Troubleshooting](#troubleshooting) below.

---

## Step 4: Use the Skills

### Option A: Direct Python CLI (Universal)

Works everywhere - no platform-specific setup needed:

```bash
# Search for datasets
python lib/client.py search-catalog --query "customer"

# Preview table data
python lib/client.py run-sql --sql "SELECT * FROM samples.customers LIMIT 5"

# Register a dataset
python lib/client.py run-dq-job \
  --dataset "MY_CUSTOMERS" \
  --sql "SELECT * FROM samples.customers LIMIT 10000"

# Get results
python lib/client.py get-results --dataset "MY_CUSTOMERS" --run-id "2026-04-08"
```

### Option B: Claude Code (.claude/skills/)

For Claude Code users (recommended):

```bash
# Link skills to Claude Code
mkdir -p ~/.claude/skills
ln -s /path/to/cdq-skills/.claude/skills/* ~/.claude/skills/

# Or copy instead of linking
cp -r /path/to/cdq-skills/.claude/skills/* ~/.claude/skills/
```

Then use in Claude Code:

```
/cdq-search-catalog --query "customer"
/cdq-run-sql --sql "SELECT * FROM table LIMIT 5"
/cdq-run-dq-job --dataset "MY_DATASET" --sql "SELECT * FROM table"
```

### Option C: Gemini CLI (.gemini/skills/)

For Gemini CLI users:

```bash
# Link skills
mkdir -p ~/.gemini/skills
ln -s /path/to/cdq-skills/.gemini/skills/* ~/.gemini/skills/
```

Then use:

```
cdq-search-catalog --query "customer"
cdq-run-sql --sql "SELECT * FROM table LIMIT 5"
```

### Option D: OpenClaw (.claw/skills/)

For OpenClaw users:

```bash
mkdir -p ~/.claw/skills
ln -s /path/to/cdq-skills/.claude/skills/* ~/.claw/skills/
```

Then use:

```
/cdq-search-catalog --query "customer"
```

---

## Quick Start Examples

### Example 1: Discover & Preview a Table

```bash
# Search for datasets with "customer" in name
python lib/client.py search-catalog --query "customer"

# Preview the data (safe LIMIT)
python lib/client.py run-sql --sql "SELECT * FROM samples.customers LIMIT 5"

# Get row count
python lib/client.py run-sql --sql "SELECT COUNT(*) as row_count FROM samples.customers"
```

### Example 2: Register & Run a DQ Job

```bash
# Register a dataset (creates logical name)
python lib/client.py run-dq-job \
  --dataset "AI_CUSTOMERS_JOB" \
  --sql "SELECT * FROM samples.customers LIMIT 50000"

# The command returns a run-id like: 2026-04-08

# Check the results
python lib/client.py get-results \
  --dataset "AI_CUSTOMERS_JOB" \
  --run-id "2026-04-08"
```

### Example 3: Create a DQ Rule

```bash
# Create a rule checking for NULL emails
python lib/client.py save-rule \
  --dataset "AI_CUSTOMERS_JOB" \
  --name "No Null Emails" \
  --description "Emails must not be NULL" \
  --sql "SELECT * FROM {dataset} WHERE email IS NULL"

# Verify the rule was saved
python lib/client.py get-rules --dataset "AI_CUSTOMERS_JOB"
```

### Example 4: Set Up Monitoring Alert

```bash
# Create an alert for low data quality score
python lib/client.py save-alert \
  --dataset "AI_CUSTOMERS_JOB" \
  --name "Low Quality Alert" \
  --condition "score < 85" \
  --email "team@company.com"

# View alerts
python lib/client.py get-alerts --dataset "AI_CUSTOMERS_JOB"
```

---

## Available Commands

### Single-Step Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `test-connection` | Verify API credentials | `python lib/client.py test-connection` |
| `search-catalog` | Find registered datasets | `python lib/client.py search-catalog --query "customer"` |
| `list-tables` | List available database tables | `python lib/client.py list-tables --search "customer"` |
| `run-sql` | Execute direct SQL queries | `python lib/client.py run-sql --sql "SELECT * FROM table"` |
| `run-dq-job` | Register dataset and run DQ | `python lib/client.py run-dq-job --dataset "MY_DS" --sql "..."` |
| `get-rules` | View DQ rules for dataset | `python lib/client.py get-rules --dataset "MY_DS"` |
| `save-rule` | Create new DQ rule | `python lib/client.py save-rule --dataset "MY_DS" ...` |
| `get-results` | Get DQ job results | `python lib/client.py get-results --dataset "MY_DS" --run-id "..."` |
| `get-alerts` | View alerts for dataset | `python lib/client.py get-alerts --dataset "MY_DS"` |
| `save-alert` | Create monitoring alert | `python lib/client.py save-alert --dataset "MY_DS" ...` |
| `get-jobs` | List DQ jobs in queue | `python lib/client.py get-jobs --limit 5` |
| `get-recent-runs` | Get recent job execution IDs | `python lib/client.py get-recent-runs` |

### Multi-Step Workflows

For complex tasks with validation, see [EXAMPLE_PROMPTS.md](./EXAMPLE_PROMPTS.md):

- **Explore & Onboard:** `cdq-workflow-explore-dataset`
- **Full Cycle:** `cdq-workflow-run-complete-job`
- **Rule Generation:** `cdq-workflow-suggest-rules`
- **Guided Assistant:** `auto-cdq` (interactive wizard)

---

## Troubleshooting

### "Required environment variable DQ_URL is not set"

**Cause:** Environment variables not loaded from `.env`

**Solution:**
1. Verify `.env` file exists: `ls -la .env`
2. Verify variables are filled in: `cat .env`
3. Ensure you're running from the cdq-skills directory
4. Try explicitly sourcing: `source .env`

### "SSL: CERTIFICATE_VERIFY_FAILED"

**Cause:** Collibra DQ uses self-signed certificate

**Solution:**
Add to `.env`:
```
DQ_VERIFY_SSL=false
```

### "Authentication failed" or "Invalid credentials"

**Cause:** Username/password/tenant incorrect

**Solution:**
1. Verify credentials in `.env`
2. Confirm account has API access
3. Check tenant ID (not always obvious)
4. Test credentials directly at your Collibra instance

### "Connection refused" or "Network error"

**Cause:** Cannot reach Collibra DQ instance

**Solution:**
1. Verify `DQ_URL` is correct: `curl -I https://your-collibra-url`
2. Check firewall/network access
3. Verify VPN connection if needed
4. For on-prem: confirm instance is running

### "Dataset not found" or "Invalid dataset name"

**Cause:** Dataset doesn't exist in CDQ

**Solution:**
1. List available datasets: `python lib/client.py search-catalog --query ""`
2. Note the exact logical name (often different from table name)
3. Use that logical name for rules, alerts, etc.

### "Command not found" in Claude Code

**Cause:** Skills not linked or Claude hasn't reloaded

**Solution:**
1. Verify symlinks exist: `ls -la ~/.claude/skills/ | grep cdq`
2. Reload Claude Code settings
3. Try restarting Claude Code
4. Check `.claude/skills/` has proper permissions

---

## Advanced: Understanding Key Concepts

### Connection vs. Dataset vs. Rule

- **Connection**: JDBC/cloud access to your database (configured by Collibra admin)
- **Dataset**: Logical name for your data (you create these)
- **Rule**: DQ check attached to a dataset (you define)
- **Job**: Execution of dataset with all rules
- **Results**: Scores and findings from job completion

### Important Distinctions

| Skill | Uses | Notes |
|-------|------|-------|
| `run-sql` | Actual `schema.table` | Direct database query |
| `save-rule` | Dataset logical name | Attaches to registered dataset |
| `run-dq-job` | Dataset logical name | Creates/runs the dataset |
| `search-catalog` | N/A | Lists all registered datasets |

Example:

```bash
# ✓ Correct: Use actual table name with run-sql
python lib/client.py run-sql --sql "SELECT * FROM samples.customers LIMIT 5"

# ✗ Wrong: Don't use logical name with run-sql
python lib/client.py run-sql --sql "SELECT * FROM MY_CUSTOMERS"

# ✓ Correct: Use logical name for rules
python lib/client.py save-rule --dataset "MY_CUSTOMERS" ...

# ✗ Wrong: Don't use table name for rules
python lib/client.py save-rule --dataset "samples.customers" ...
```

---

## Next Steps

1. **See Examples**: Read [EXAMPLE_PROMPTS.md](./EXAMPLE_PROMPTS.md) for multi-step workflows
2. **Automate Tasks**: Use `/auto-cdq` skill for guided automation (Claude Code)
3. **Generate Test Data**: Use `/fake-data-generator` for realistic test datasets
4. **Scale Operations**: See workflow examples for batch processing
5. **Monitor Quality**: Set up alerts for continuous data quality monitoring

---

## Getting Help

- **Command Syntax**: `python lib/client.py <command> --help`
- **API Docs**: Embedded in each SKILL.md file
- **Examples**: See [EXAMPLE_PROMPTS.md](./EXAMPLE_PROMPTS.md)
- **Issues**: Check configuration first, then review logs

---

## System Requirements

### Tested Environments

- Python 3.8, 3.9, 3.10, 3.11, 3.12
- macOS (10.14+)
- Linux (Ubuntu 18.04+, CentOS 7+)
- Windows 10/11 (WSL or native)

### Network Requirements

- HTTP/HTTPS access to Collibra DQ instance
- Outbound port 443 (HTTPS)
- Network access to configured database connections

---

**For more details, see:**
- [README.md](./README.md) - Complete documentation
- [EXAMPLE_PROMPTS.md](./EXAMPLE_PROMPTS.md) - Workflow templates
- [LICENSE](./LICENSE) - MIT License

