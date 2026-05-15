# Setup Guide - CDQ Skills

---

## Prerequisites

- Python 3.8 or later
- Collibra DQ instance with API access
- API credentials (username, password, tenant ID)

---

## Step 1: Install

```bash
pip install -e .
```

This installs the `cdq` CLI and all dependencies.

---

## Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
DQ_URL=https://your-collibra-instance.com
DQ_USERNAME=your_username
DQ_PASSWORD=your_password
DQ_ISS=your_tenant_id
DQ_CXN=BIGQUERY          # or SNOWFLAKE, etc.
DQ_VERIFY_SSL=true        # false if using self-signed certificates
```

| Variable | Description | Required |
|----------|-------------|----------|
| `DQ_URL` | Collibra DQ API base URL | Yes |
| `DQ_USERNAME` | Collibra username | Yes |
| `DQ_PASSWORD` | Collibra password | Yes |
| `DQ_ISS` | Tenant identifier | Yes |
| `DQ_CXN` | Default database connection | No (default: BIGQUERY) |
| `DQ_VERIFY_SSL` | SSL certificate verification | No (default: true) |

---

## Step 3: Test Connection

```bash
cdq test-connection
```

---

## Step 4: Use the CLI

```bash
# Search for datasets
cdq search-catalog --query "customer"

# Preview table data
cdq run-sql --sql "SELECT * FROM samples.customers LIMIT 5"

# Register a dataset and run a DQ job
cdq run-dq-job \
  --dataset "MY_CUSTOMERS" \
  --sql "SELECT * FROM samples.customers LIMIT 10000"

# Get results
cdq get-results --dataset "MY_CUSTOMERS" --run-id "2026-04-08"
```

---

## Step 5: Link Skills to Claude Code

```bash
mkdir -p ~/.claude/skills
ln -s /path/to/cdq-skills/.claude/skills/* ~/.claude/skills/
```

Then use slash commands in Claude Code:

```
/cdq-search-catalog --query "customer"
/cdq-run-sql --sql "SELECT * FROM table LIMIT 5"
/cdq-run-dq-job --dataset "MY_DATASET" --sql "SELECT * FROM table"
```

---

## Quick Examples

### Discover & Preview a Table

```bash
cdq search-catalog --query "customer"
cdq run-sql --sql "SELECT * FROM samples.customers LIMIT 5"
cdq run-sql --sql "SELECT COUNT(*) as row_count FROM samples.customers"
```

### Register & Run a DQ Job

```bash
cdq run-dq-job \
  --dataset "AI_CUSTOMERS_JOB" \
  --sql "SELECT * FROM samples.customers LIMIT 50000"

cdq get-results --dataset "AI_CUSTOMERS_JOB" --run-id "2026-04-08"
```

### Create a DQ Rule

```bash
cdq save-rule \
  --dataset "AI_CUSTOMERS_JOB" \
  --name "No Null Emails" \
  --description "Emails must not be NULL" \
  --sql "SELECT * FROM {dataset} WHERE email IS NULL"

cdq get-rules --dataset "AI_CUSTOMERS_JOB"
```

### Set Up a Monitoring Alert

```bash
cdq save-alert \
  --dataset "AI_CUSTOMERS_JOB" \
  --name "Low Quality Alert" \
  --condition "score < 85" \
  --email "team@company.com"

cdq get-alerts --dataset "AI_CUSTOMERS_JOB"
```

---

## Available Commands

| Command | Purpose |
|---------|---------|
| `cdq test-connection` | Verify API credentials |
| `cdq search-catalog --query "..."` | Find registered datasets |
| `cdq list-tables --schema samples` | List available database tables |
| `cdq run-sql --sql "..."` | Execute direct SQL queries |
| `cdq run-dq-job --dataset "..." --sql "..."` | Register dataset and run DQ |
| `cdq get-rules --dataset "..."` | View DQ rules for dataset |
| `cdq save-rule --dataset "..." ...` | Create new DQ rule |
| `cdq get-results --dataset "..." --run-id "..."` | Get DQ job results |
| `cdq get-alerts --dataset "..."` | View alerts for dataset |
| `cdq save-alert --dataset "..." ...` | Create monitoring alert |
| `cdq get-jobs --limit 5` | List DQ jobs in queue |
| `cdq get-recent-runs` | Get recent job execution IDs |

---

## Troubleshooting

**"Required environment variable DQ_URL is not set"**
- Verify `.env` exists and variables are filled in
- Ensure you're running from the cdq-skills directory

**"SSL: CERTIFICATE_VERIFY_FAILED"**
- Add `DQ_VERIFY_SSL=false` to `.env`

**"Authentication failed"**
- Verify credentials in `.env`
- Confirm account has API access and tenant ID is correct

**"Dataset not found"**
- Run `cdq search-catalog --query ""` to list all datasets
- Use the exact logical name shown in the catalog

**Skills not found in Claude Code**
- Verify symlinks: `ls -la ~/.claude/skills/ | grep cdq`
- Restart Claude Code after linking

---

**For more details, see [README.md](./README.md)**
