---
name: fake-data-generator
description: Generate realistic fake data for testing, demos, and development using the Faker library. Supports 150+ field types across personal, customer, company, financial, and healthcare categories with CSV/JSON export, null injection, and seed-based reproducibility.
---

# Fake Data Generator Skill

Generate realistic fake data using the Faker library. Supports multiple categories (personal, customer, HR, sales, etc.), configurable row counts, and CSV export.

## When to Use

- **Testing and development** - Generate sample data for databases, APIs, or applications
- **Demo and presentation data** - Create realistic-looking datasets for demos
- **Data analysis practice** - Generate datasets for SQL, Python, or analytics exercises
- **Privacy-safe data** - Use fake data instead of real PII for testing
- **Quick prototyping** - When you need sample data fast without manual entry

## When NOT to Use

- **Production data** - This is for testing/demo only, not real user data
- **When you need real, specific data** - Use actual APIs or data sources
- **Complex data relationships** - Faker generates independent fields, not relational data
- **When data quality/accuracy is critical** - Fake data has realistic patterns but not real information

## Alternatives

| Use Case | Alternative Approach | Why Choose It |
|----------|---------------------|---------------|
| Real customer data | Use actual business data sources | Authenticity and accuracy |
| Complex relational data | Database dumps or synthetic data generators | Better relationship modeling |
| Specific industry data | Domain-specific data generators | More realistic industry patterns |
| Large-scale synthetic data | Python scripts with NumPy/pandas | More control over distributions |

## Installation

```bash
pip install faker pandas
```

## Usage

### Basic Generation

Generate fake data with default settings (10 rows, no save):

```
Generate fake customer data
```

### With Options

Specify rows, null percentage, JSON output, and save to CSV:

```
Generate 100 rows of fake user profile data with 10% nulls and save to /tmp/users.csv
```

```
Generate 50 rows of fake sales data in JSON format and save to /tmp/sales.json
```

### Available Data Categories

#### 👤 Personal Identity
| Field | Faker Method | Description |
|-------|--------------|-------------|
| first_name | `first_name` | First name |
| last_name | `last_name` | Last name |
| full_name | `name` | Full name |
| email | `email` | Email address |
| safe_email | `safe_email` | Safe email (no real domains) |
| phone | `phone_number` | Phone number |
| ssn | `ssn` | Social Security Number |
| date_of_birth | `date_of_birth` | DOB |
| job | `job` | Job title |

#### 🏠 Address & Location
| Field | Faker Method | Description |
|-------|--------------|-------------|
| street_address | `street_address` | Street address |
| city | `city` | City |
| state | `state` | Full state name |
| state_abbr | `state_abbr` | State abbreviation |
| zipcode | `zipcode` | ZIP code |
| country | `country` | Country name |
| latitude | `latitude` | Latitude |
| longitude | `longitude` | Longitude |

#### 💼 Company & Work
| Field | Faker Method | Description |
|-------|--------------|-------------|
| company_name | `company` | Company name |
| company_email | `company_email` | Company email |
| job | `job` | Job title |
| department | `catch_phrase` | Department/catch phrase |
| company_suffix | `company_suffix` | Inc, LLC, etc. |

#### 💳 Financial
| Field | Faker Method | Description |
|-------|--------------|-------------|
| credit_card | `credit_card_number` | Credit card number |
| card_provider | `credit_card_provider` | Visa, MC, etc. |
| card_expiry | `credit_card_expire` | Expiration date |
| card_cvv | `credit_card_security_code` | CVV |
| bank_name | `bank` | Bank name |
| iban | `iban` | IBAN |
| bban | `bban` | BBAN |
| currency | `currency` | Currency code |
| pricetag | `pricetag` | Price tag |

#### 🔐 Security & Tech
| Field | Faker Method | Description |
|-------|--------------|-------------|
| username | `user_name` | Username |
| password | `password` | Random password |
| md5 | `md5` | MD5 hash |
| sha256 | `sha256` | SHA256 hash |
| uuid | `uuid4` | UUID |
| ipv4 | `ipv4` | IPv4 address |
| ipv6 | `ipv6` | IPv6 address |
| mac_address | `mac_address` | MAC address |
| hostname | `hostname` | Hostname |
| domain | `domain_name` | Domain name |
| url | `url` | URL |

#### 📅 Dates & Time
| Field | Faker Method | Description |
|-------|--------------|-------------|
| date | `date` | Random date |
| datetime | `date_time` | Date and time |
| time | `time` | Time |
| timezone | `timezone` | Timezone |
| year | `year` | Year |
| month | `month_name` | Month name |
| day | `day_of_week` | Day of week |

#### 📝 Text & Content
| Field | Faker Method | Description |
|-------|--------------|-------------|
| sentence | `sentence` | Random sentence |
| paragraph | `paragraph` | Paragraph |
| text | `text` | Full text |
| word | `word` | Single word |
| words | `words` | Multiple words |
| catch_phrase | `catch_phrase` | Marketing catch phrase |
| bs | `bs` | Business jargon |

#### 🏭 Industry-Specific

**HR / Employee Data:**
- employee_id, hire_date, job_title, department, salary, supervisor, termination_date, employment_status

**Sales / CRM:**
- customer_id, account_number, deal_value, probability, close_date, lead_source, sales_rep, territory
- **Preset:** `sales` - transaction_id, full_name, email, amount, price, quantity, company, invoice_number, date, country

**E-commerce:**
- order_id, product_sku, product_name, price, quantity, shipping_address, tracking_number, transaction_id

**Healthcare:**
- patient_id, medical_record_number, insurance_provider, policy_number, diagnosis_code, prescription, doctor_name

**Finance:**
- account_number, routing_number, tax_id, invoice_number, transaction_type, balance, credit_limit

## Implementation

```python
import json
import pandas as pd
from faker import Faker
import argparse
import os
import sys
import random

fake = Faker()

FIELDS = {
    "first_name": lambda: fake.first_name(),
    "last_name": lambda: fake.last_name(),
    "email": lambda: fake.email(),
    "phone": lambda: fake.phone_number(),
    "ssn": lambda: fake.ssn(),
    "date_of_birth": lambda: str(fake.date_of_birth(minimum_age=18, maximum_age=80)),
    "job": lambda: fake.job(),
    # ... 150+ fields total (address, company, financial, security, dates, text, internet)
}

PRESETS = {
    "user": {"Description": "Basic user profile", "fields": ["first_name", "last_name", "email", "phone", ...]},
    "customer": {"Description": "Customer/CRM data", "fields": [...]},
    "sales": {"Description": "Sales/transaction data", "fields": [...]},
    # ... 11 presets total
}

def generate(fields, rows=10, seed=None, null_pct=0):
    """Generate fake data with optional null injection."""
    if seed:
        fake.seed_instance(seed)
    data = []
    for _ in range(rows):
        row = {}
        for f in fields:
            if null_pct > 0 and random.random() * 100 < null_pct:
                row[f] = None
            else:
                row[f] = FIELDS[f]()
        data.append(row)
    return pd.DataFrame(data)

# CLI with --null-pct, --format json, -p preset, custom fields, seed support
```

## CLI Script

See `scripts/generate_fake_data.py` for the full implementation (150+ fields, 11 presets).

### CLI Options

| Flag | Description |
|------|-------------|
| `-n`, `--rows` | Number of rows (default: 10) |
| `-o`, `--output` | Output file path |
| `-s`, `--seed` | Random seed for reproducibility |
| `-p`, `--preset` | Use a preset: user, customer, employee, address, company, financial, security, personal, ecommerce, healthcare, sales |
| `-l`, `--list` | List all available fields and presets |
| `-v`, `--verbose` | Show preset descriptions |
| `--null-pct` | Percentage chance each field is null (0-100) |
| `--format` | Output format: csv (default) or json |

## Examples

```bash
# List available fields
python3 generate_fake_data.py --list

# Generate 10 users (default)
python3 generate_fake_data.py -p user

# Generate 100 customers and save
python3 generate_fake_data.py -p customer -n 100 -o ~/fake_customers.csv

# Custom fields
python3 generate_fake_data.py first_name last_name email job company -n 50

# With seed for reproducibility
python3 generate_fake_data.py -p user -n 100 -s 42 -o test.csv

# With 15% null values (realistic missing data)
python3 generate_fake_data.py -p user -n 20 --null-pct 15 -o /tmp/users_with_nulls.csv

# JSON output
python3 generate_fake_data.py -p sales -n 5 --format json

# Save as JSON
python3 generate_fake_data.py -p customer -n 10 -o /tmp/customers.json --format json
```

## Integration with Spark SQL

Load generated CSV into Spark SQL:

```bash
# Generate data
python3 generate_fake_data.py -p user -n 1000 -o /tmp/users.csv

# Load with spark-sql-playground
python3 ~/.openclaw/workspace/skills/spark-sql-playground/scripts/spark_sql.py load "/tmp/users.csv" users
python3 ~/.openclaw/workspace/skills/spark-sql-playground/scripts/spark_sql.py query "SELECT * FROM users LIMIT 5"
```