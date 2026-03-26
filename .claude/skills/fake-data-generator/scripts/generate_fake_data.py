#!/usr/bin/env python3
"""
Fake Data Generator using Faker library.
Generates realistic fake data for testing, demos, and development.
"""
import pandas as pd
from faker import Faker
import argparse
import os
import sys

fake = Faker()

# Field mappings organized by category
FIELDS = {
    # === Identity ===
    "first_name": lambda: fake.first_name(),
    "last_name": lambda: fake.last_name(),
    "full_name": lambda: fake.name(),
    "first_name_female": lambda: fake.first_name_female(),
    "first_name_male": lambda: fake.first_name_male(),
    "name_female": lambda: fake.name_female(),
    "name_male": lambda: fake.name_male(),
    "email": lambda: fake.email(),
    "ascii_email": lambda: fake.ascii_email(),
    "safe_email": lambda: fake.safe_email(),
    "free_email": lambda: fake.free_email(),
    "phone": lambda: fake.phone_number(),
    "basic_phone_number": lambda: fake.basic_phone_number(),
    "msisdn": lambda: fake.msisdn(),
    "ssn": lambda: fake.ssn(),
    "ein": lambda: fake.ein(),
    "itin": lambda: fake.itin(),
    "date_of_birth": lambda: str(fake.date_of_birth(minimum_age=18, maximum_age=80)),
    "age": lambda: fake.random_int(min=18, max=80),
    "job": lambda: fake.job(),
    "job_female": lambda: fake.job_female(),
    "job_male": lambda: fake.job_male(),
    
    # === Address & Location ===
    "street_address": lambda: fake.street_address(),
    "street_name": lambda: fake.street_name(),
    "building_number": lambda: fake.building_number(),
    "city": lambda: fake.city(),
    "city_prefix": lambda: fake.city_prefix(),
    "city_suffix": lambda: fake.city_suffix(),
    "state": lambda: fake.state(),
    "state_abbr": lambda: fake.state_abbr(),
    "zipcode": lambda: fake.zipcode(),
    "postcode": lambda: fake.postcode(),
    "postalcode": lambda: fake.postalcode(),
    "country": lambda: fake.country(),
    "country_code": lambda: fake.country_code(),
    "latitude": lambda: fake.latitude(),
    "longitude": lambda: fake.longitude(),
    "coordinate": lambda: str(fake.coordinate()),
    "locale": lambda: fake.locale(),
    "timezone": lambda: fake.timezone(),
    
    # === Company & Work ===
    "company": lambda: fake.company(),
    "company_name": lambda: fake.company(),
    "company_suffix": lambda: fake.company_suffix(),
    "company_email": lambda: fake.company_email(),
    "ascii_company_email": lambda: fake.ascii_company_email(),
    "catch_phrase": lambda: fake.catch_phrase(),
    "bs": lambda: fake.bs(),
    "department": lambda: fake.catch_phrase(),
    "domain": lambda: fake.domain_name(),
    "domain_word": lambda: fake.domain_word(),
    "tld": lambda: fake.tld(),
    
    # === Financial ===
    "credit_card_number": lambda: fake.credit_card_number(),
    "credit_card": lambda: fake.credit_card_number(),
    "card_provider": lambda: fake.credit_card_provider(),
    "card_expiry": lambda: fake.credit_card_expire(),
    "card_expire": lambda: fake.credit_card_expire(),
    "card_cvv": lambda: fake.credit_card_security_code(),
    "card_security_code": lambda: fake.credit_card_security_code(),
    "bank": lambda: fake.bank(),
    "bank_country": lambda: fake.bank_country(),
    "iban": lambda: fake.iban(),
    "bban": lambda: fake.bban(),
    "swift": lambda: fake.swift(),
    "swift11": lambda: fake.swift11(),
    "swift8": lambda: fake.swift8(),
    "currency": lambda: fake.currency(),
    "currency_code": lambda: fake.currency_code(),
    "currency_name": lambda: fake.currency_name(),
    "currency_symbol": lambda: fake.currency_symbol(),
    "pricetag": lambda: fake.pricetag(),
    "credit_card_full": lambda: fake.credit_card_full(),
    
    # === Security & Tech ===
    "username": lambda: fake.user_name(),
    "password": lambda: fake.password(),
    "md5": lambda: fake.md5(),
    "sha1": lambda: fake.sha1(),
    "sha256": lambda: fake.sha256(),
    "uuid": lambda: str(fake.uuid4()),
    "uuid4": lambda: str(fake.uuid4()),
    "ipv4": lambda: fake.ipv4(),
    "ipv4_public": lambda: fake.ipv4_public(),
    "ipv4_private": lambda: fake.ipv4_private(),
    "ipv6": lambda: fake.ipv6(),
    "mac_address": lambda: fake.mac_address(),
    "hostname": lambda: fake.hostname(),
    "domain_name": lambda: fake.domain_name(),
    "url": lambda: fake.url(),
    "uri": lambda: fake.uri(),
    "uri_extension": lambda: fake.uri_extension(),
    "file_extension": lambda: fake.file_extension(),
    "file_name": lambda: fake.file_name(),
    "file_path": lambda: fake.file_path(),
    "mime_type": lambda: fake.mime_type(),
    "port_number": lambda: fake.port_number(),
    
    # === Dates & Time ===
    "date": lambda: str(fake.date()),
    "datetime": lambda: str(fake.date_time()),
    "date_time": lambda: str(fake.date_time()),
    "time": lambda: fake.time(),
    "time_object": lambda: str(fake.time_object()),
    "year": lambda: fake.year(),
    "month": lambda: fake.month(),
    "month_name": lambda: fake.month_name(),
    "day_of_month": lambda: fake.day_of_month(),
    "day_of_week": lambda: fake.day_of_week(),
    "unix_time": lambda: fake.unix_time(),
    "iso8601": lambda: fake.iso8601(),
    "past_date": lambda: str(fake.past_date()),
    "future_date": lambda: str(fake.future_date()),
    "past_datetime": lambda: str(fake.past_datetime()),
    "future_datetime": lambda: str(fake.future_datetime()),
    
    # === Text & Content ===
    "sentence": lambda: fake.sentence(),
    "sentences": lambda: fake.sentences(),
    "paragraph": lambda: fake.paragraph(),
    "paragraphs": lambda: fake.paragraphs(),
    "text": lambda: fake.text(),
    "word": lambda: fake.word(),
    "words": lambda: fake.words(),
    "catch_phrase": lambda: fake.catch_phrase(),
    "bs": lambda: fake.bs(),
    "hex_color": lambda: fake.hex_color(),
    "color_name": lambda: fake.color_name(),
    "rgb_color": lambda: fake.rgb_color(),
    "emoji": lambda: fake.emoji(),
    
    # === Internet ===
    "user_agent": lambda: fake.user_agent(),
    "chrome": lambda: fake.chrome(),
    "firefox": lambda: fake.firefox(),
    "safari": lambda: fake.safari(),
    "opera": lambda: fake.opera(),
    "internet_explorer": lambda: fake.internet_explorer(),
    "android_platform_token": lambda: fake.android_platform_token(),
    "ios_platform_token": lambda: fake.ios_platform_token(),
    "linux_platform_token": lambda: fake.linux_platform_token(),
    "windows_platform_token": lambda: fake.windows_platform_token(),
    
    # === Miscellaneous ===
    "boolean": lambda: fake.boolean(),
    "null_boolean": lambda: fake.null_boolean(),
    "binary": lambda: str(fake.binary()),
    "uuid4": lambda: str(fake.uuid4()),
    "isbn10": lambda: fake.isbn10(),
    "isbn13": lambda: fake.isbn13(),
    "ean": lambda: fake.ean(),
    "ean13": lambda: fake.ean13(),
    "ean8": lambda: fake.ean8(),
    "vin": lambda: fake.vin(),
    "license_plate": lambda: fake.license_plate(),
    "profile": lambda: str(fake.profile()),
    "simple_profile": lambda: str(fake.simple_profile()),
    "license_plate": lambda: fake.license_plate(),
}

# Preset configurations
PRESETS = {
    "user": {
        "description": "Basic user profile",
        "fields": ["first_name", "last_name", "email", "phone", "street_address", "city", "state_abbr", "zipcode", "date_of_birth"]
    },
    "customer": {
        "description": "Customer/CRM data",
        "fields": ["first_name", "last_name", "email", "phone", "company", "job", "street_address", "city", "state_abbr", "zipcode"]
    },
    "employee": {
        "description": "HR/Employee records",
        "fields": ["full_name", "email", "job", "company", "phone", "ssn", "street_address", "city", "state_abbr", "zipcode"]
    },
    "address": {
        "description": "Address data",
        "fields": ["street_address", "street_name", "building_number", "city", "city_suffix", "state", "state_abbr", "zipcode", "country", "latitude", "longitude"]
    },
    "company": {
        "description": "Company/business data",
        "fields": ["company", "company_suffix", "company_email", "domain", "catch_phrase", "bs", "street_address", "city", "state_abbr", "zipcode", "phone"]
    },
    "financial": {
        "description": "Financial/payment data",
        "fields": ["credit_card_number", "card_provider", "card_expiry", "card_cvv", "bank", "iban", "bban", "currency", "swift"]
    },
    "security": {
        "description": "Security/authentication",
        "fields": ["username", "password", "email", "md5", "sha256", "uuid", "ipv4", "ipv6", "mac_address", "hostname"]
    },
    "address_full": {
        "description": "Complete address",
        "fields": ["street_address", "street_name", "building_number", "secondary_address", "city", "city_prefix", "city_suffix", "state", "state_abbr", "zipcode", "postcode", "country", "country_code", "latitude", "longitude"]
    },
    "personal": {
        "description": "Personal identity",
        "fields": ["first_name", "last_name", "full_name", "email", "safe_email", "phone", "ssn", "date_of_birth", "job", "company"]
    },
    "ecommerce": {
        "description": "E-commerce order",
        "fields": ["order_id", "customer_id", "product_name", "quantity", "price", "credit_card_number", "street_address", "city", "state_abbr", "zipcode", "date"]
    },
    "healthcare": {
        "description": "Healthcare/patient",
        "fields": ["patient_id", "full_name", "date_of_birth", "ssn", "insurance_provider", "street_address", "city", "state_abbr", "zipcode", "phone"]
    },
}

# Add more preset-friendly aliases
PRESETS["address"] = PRESETS["address_full"]

def generate(fields, rows=10, seed=None):
    """Generate fake data for specified fields."""
    if seed:
        fake.seed_instance(seed)
    
    # Clean field names
    clean_fields = [f for f in fields if f in FIELDS]
    unknown = [f for f in fields if f not in FIELDS]
    if unknown:
        print(f"Warning: Unknown fields: {unknown}", file=sys.stderr)
    
    if not clean_fields:
        print("Error: No valid fields specified", file=sys.stderr)
        sys.exit(1)
    
    data = []
    for _ in range(rows):
        row = {f: FIELDS[f]() for f in clean_fields}
        data.append(row)
    
    return pd.DataFrame(data)

def main():
    parser = argparse.ArgumentParser(
        description="Generate fake data with Faker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list
  %(prog)s -p user
  %(prog)s -p customer -n 100 -o ~/fake_customers.csv
  %(prog)s first_name last_name email job -n 50
  %(prog)s -p user -n 1000 -s 42 -o test.csv
        """
    )
    parser.add_argument("-n", "--rows", type=int, default=10, help="Number of rows (default: 10)")
    parser.add_argument("-o", "--output", type=str, help="Output CSV path")
    parser.add_argument("-S", "--save", action="store_true", help="Save to default data/csv location for spark-sql")
    parser.add_argument("-s", "--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("-l", "--list", action="store_true", help="List available fields and presets")
    parser.add_argument("-p", "--preset", type=str, help="Use a preset (user, customer, employee, address, company, financial, security, personal, ecommerce, healthcare)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show preset descriptions")
    parser.add_argument("fields", nargs="*", help="Fields to generate")
    
    args = parser.parse_args()
    
    if args.list:
        print("=== Available Fields ({} total) ===".format(len(FIELDS)))
        for f in sorted(FIELDS):
            print(f"  {f}")
        print("\n=== Presets ===")
        for p, info in PRESETS.items():
            fields = ", ".join(info["fields"][:5]) + ("..." if len(info["fields"]) > 5 else "")
            if args.verbose:
                print(f"  {p}:")
                print(f"    Description: {info['description']}")
                print(f"    Fields: {fields}")
            else:
                print(f"  {p} ({info['description']}): {fields}")
        return
    
    # Determine fields
    if args.preset:
        if args.preset not in PRESETS:
            print(f"Unknown preset: {args.preset}")
            print("Available presets: " + ", ".join(PRESETS.keys()))
            sys.exit(1)
        fields = PRESETS[args.preset]["fields"]
    elif args.fields:
        fields = args.fields
    else:
        fields = PRESETS["user"]["fields"]  # Default
    
    # Generate
    df = generate(fields, args.rows, args.seed)
    
    # Output
    default_output = os.path.expanduser("~/.openclaw/workspace/data/csv/fake_data.csv")
    
    # Determine output: explicit -o flag, -S flag for default location, or stdout
    if args.output:
        output_path = args.output
        save_file = True
    elif args.save:
        output_path = default_output
        save_file = True
    else:
        save_file = False
    
    if save_file:
        dir_path = os.path.dirname(output_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"✓ Saved {len(df)} rows to {output_path}")
    else:
        print(df.to_string())

if __name__ == "__main__":
    main()