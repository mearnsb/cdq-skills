---
name: fake-data-generator
description: Generate realistic fake data for testing, demos, and development using the Faker library. Supports 142+ field types across personal, customer, company, financial, and healthcare categories with CSV export.
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

Specify rows and save to CSV:

```
Generate 100 rows of fake user profile data and save to /tmp/users.csv
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

**E-commerce:**
- order_id, product_sku, product_name, price, quantity, shipping_address, tracking_number, transaction_id

**Healthcare:**
- patient_id, medical_record_number, insurance_provider, policy_number, diagnosis_code, prescription, doctor_name

**Finance:**
- account_number, routing_number, tax_id, invoice_number, transaction_type, balance, credit_limit

## Implementation

```python
import pandas as pd
from faker import Faker
import argparse
import os

fake = Faker()

# Define field mappings
FIELD_MAP = {
    # Personal
    "first_name": fake.first_name,
    "last_name": fake.last_name,
    "full_name": fake.name,
    "email": fake.email,
    "safe_email": fake.safe_email,
    "phone": fake.phone_number,
    "ssn": fake.ssn,
    "date_of_birth": lambda: fake.date_of_birth(minimum_age=18, maximum_age=80),
    "job": fake.job,
    
    # Address
    "street_address": fake.street_address,
    "city": fake.city,
    "state": fake.state,
    "state_abbr": fake.state_abbr,
    "zipcode": fake.zipcode,
    "country": fake.country,
    "latitude": fake.latitude,
    "longitude": fake.longitude,
    
    # Company
    "company_name": fake.company,
    "company_email": fake.company_email,
    "company_suffix": fake.company_suffix,
    
    # Financial
    "credit_card": fake.credit_card_number,
    "card_provider": fake.credit_card_provider,
    "card_expiry": fake.credit_card_expire,
    "card_cvv": fake.credit_card_security_code,
    "bank": fake.bank,
    "iban": fake.iban,
    "currency": fake.currency,
    "pricetag": fake.pricetag,
    
    # Security
    "username": fake.user_name,
    "password": fake.password,
    "md5": fake.md5,
    "sha256": fake.sha256,
    "uuid": fake.uuid4,
    "ipv4": fake.ipv4,
    "ipv6": fake.ipv6,
    "mac_address": fake.mac_address,
    "hostname": fake.hostname,
    "domain": fake.domain_name,
    "url": fake.url,
    
    # Dates
    "date": fake.date,
    "datetime": fake.date_time,
    "time": fake.time,
    "timezone": fake.timezone,
    "year": fake.year,
    "month": fake.month_name,
    "day_of_week": fake.day_of_week,
    
    # Text
    "sentence": fake.sentence,
    "paragraph": fake.paragraph,
    "text": fake.text,
    "word": fake.word,
    "catch_phrase": fake.catch_phrase,
    "bs": fake.bs,
}

def generate_fake_data(fields, num_rows=10, seed=None):
    """Generate fake data for specified fields."""
    if seed:
        Faker.seed(seed)
    
    items = []
    for _ in range(num_rows):
        row = {}
        for field in fields:
            if field in FIELD_MAP:
                row[field] = FIELD_MAP[field]()
            else:
                row[field] = f"unknown_field_{field}"
        items.append(row)
    
    return pd.DataFrame(items)

def save_to_csv(df, path):
    """Save DataFrame to CSV."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    df.to_csv(path, index=False)
    return path

# Example usage
if __name__ == "__main__":
    fields = ["first_name", "last_name", "email", "phone", "company_name", "job"]
    df = generate_fake_data(fields, num_rows=100)
    save_to_csv(df, "fake_data.csv")
    print(df.head())
```

## CLI Script

Save as `scripts/generate_fake_data.py`:

```bash
#!/usr/bin/env python3
import pandas as pd
from faker import Faker
import argparse
import os
import sys

fake = Faker()

# Field mappings
FIELDS = {
    # Identity
    "first_name": lambda: fake.first_name(),
    "last_name": lambda: fake.last_name(),
    "full_name": lambda: fake.name(),
    "email": lambda: fake.email(),
    "safe_email": lambda: fake.safe_email(),
    "phone": lambda: fake.phone_number(),
    "ssn": lambda: fake.ssn(),
    "job": lambda: fake.job(),
    # Address
    "street_address": lambda: fake.street_address(),
    "city": lambda: fake.city(),
    "state": lambda: fake.state(),
    "state_abbr": lambda: fake.state_abbr(),
    "zipcode": lambda: fake.zipcode(),
    "country": lambda: fake.country(),
    "latitude": lambda: fake.latitude(),
    "longitude": lambda: fake.longitude(),
    # Company
    "company": lambda: fake.company(),
    "company_email": lambda: fake.company_email(),
    # Financial
    "credit_card": lambda: fake.credit_card_number(),
    "card_provider": lambda: fake.credit_card_provider(),
    "card_expiry": lambda: fake.credit_card_expire(),
    "bank": lambda: fake.bank(),
    "iban": lambda: fake.iban(),
    "currency": lambda: fake.currency(),
    # Security
    "username": lambda: fake.user_name(),
    "password": lambda: fake.password(),
    "md5": lambda: fake.md5(),
    "sha256": lambda: fake.sha256(),
    "uuid": lambda: str(fake.uuid4()),
    "ipv4": lambda: fake.ipv4(),
    "ipv6": lambda: fake.ipv6(),
    "mac_address": lambda: fake.mac_address(),
    "hostname": lambda: fake.hostname(),
    "domain": lambda: fake.domain_name(),
    "url": lambda: fake.url(),
    # Dates
    "date": lambda: str(fake.date()),
    "datetime": lambda: str(fake.date_time()),
    "time": lambda: fake.time(),
    "timezone": lambda: fake.timezone(),
    # Text
    "sentence": lambda: fake.sentence(),
    "paragraph": lambda: fake.paragraph(),
    "catch_phrase": lambda: fake.catch_phrase(),
    "bs": lambda: fake.bs(),
}

PRESETS = {
    "user": ["first_name", "last_name", "email", "phone", "street_address", "city", "state_abbr", "zipcode"],
    "customer": ["first_name", "last_name", "email", "phone", "company", "job"],
    "employee": ["full_name", "email", "job", "company", "phone", "ssn"],
    "address": ["street_address", "city", "state", "state_abbr", "zipcode", "country"],
    "company": ["company", "company_email", "domain", "url", "catch_phrase"],
    "financial": ["credit_card", "card_provider", "card_expiry", "bank", "iban", "currency"],
    "security": ["username", "password", "md5", "sha256", "uuid", "ipv4", "mac_address"],
}

def generate(fields, rows=10, seed=None):
    if seed:
        fake.seed_instance(seed)
    
    data = []
    for _ in range(rows):
        row = {f: FIELDS[f]() for f in fields if f in FIELDS}
        data.append(row)
    
    return pd.DataFrame(data)

def main():
    parser = argparse.ArgumentParser(description="Generate fake data with Faker")
    parser.add_argument("-n", "--rows", type=int, default=10, help="Number of rows")
    parser.add_argument("-o", "--output", type=str, help="Output CSV path")
    parser.add_argument("-s", "--seed", type=int, help="Random seed")
    parser.add_argument("-l", "--list", action="store_true", help="List available fields and presets")
    parser.add_argument("-p", "--preset", type=str, help="Use a preset (user, customer, employee, address, company, financial, security)")
    parser.add_argument("fields", nargs="*", help="Fields to generate")
    
    args = parser.parse_args()
    
    if args.list:
        print("=== Available Fields ===")
        for f in sorted(FIELDS):
            print(f"  {f}")
        print("\n=== Presets ===")
        for p, f in PRESETS.items():
            print(f"  {p}: {', '.join(f)}")
        return
    
    # Determine fields
    if args.preset:
        if args.preset not in PRESETS:
            print(f"Unknown preset: {args.preset}")
            sys.exit(1)
        fields = PRESETS[args.preset]
    elif args.fields:
        fields = args.fields
    else:
        fields = PRESETS["user"]  # Default
    
    # Generate
    df = generate(fields, args.rows, args.seed)
    
    # Output
    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        df.to_csv(args.output, index=False)
        print(f"Saved {len(df)} rows to {args.output}")
    else:
        print(df.to_string())

if __name__ == "__main__":
    main()
```

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