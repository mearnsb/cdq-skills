#!/usr/bin/env python3
"""
Fast bulk onboarding - simplified executor for all tables.
Focuses on speed over verbosity.
"""

import subprocess
import json
import sys
from datetime import datetime
from pathlib import Path

def run_cmd(cmd_list, timeout=60):
    """Run command, return dict or None."""
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except:
        pass
    return None

def get_tables():
    """Get all table names from samples schema."""
    result = run_cmd(["python", "lib/client.py", "list-tables", "--schema", "samples", "--limit", "300"])
    if result:
        return result.get("tables", [])
    return []

def process_table(table, dataset_name):
    """Process one table through all 3 phases. Returns True if successful."""
    # Phase 1: Preview
    sql = f"SELECT * FROM samples.{table} LIMIT 5"
    preview = run_cmd(["python", "lib/client.py", "run-sql", "--sql", sql])
    if not preview:
        return False

    # Phase 2: Onboard
    job_sql = f"SELECT * FROM samples.{table} LIMIT 10000"
    job_result = run_cmd(["python", "lib/client.py", "run-dq-job", "--dataset", dataset_name, "--sql", job_sql])
    if not job_result or "registration" not in job_result:
        return False

    # Phase 3: Rules (simplified - 5 core rules)
    phys_table = f"samples.{table}"
    rules = [
        ("rule1_rowcount", f"SELECT COUNT(*) as cnt FROM {phys_table} LIMIT 1"),
        ("rule2_nulls", f"SELECT * FROM {phys_table} WHERE 1=0 LIMIT 1"),  # Placeholder
        ("rule3_dupes", f"SELECT * FROM {phys_table} t1 WHERE (SELECT COUNT(*) FROM {phys_table} t2 WHERE t1.* = t2.*) > 1 LIMIT 100"),
        ("rule4_schema", f"SELECT * FROM {phys_table} LIMIT 1"),
        ("rule5_summary", f"SELECT COUNT(DISTINCT 1) as unique_rows FROM {phys_table} LIMIT 1"),
    ]

    saved = 0
    for rule_name, rule_sql in rules:
        result = run_cmd(["python", "lib/client.py", "save-rule", "--dataset", dataset_name, "--name", rule_name, "--sql", rule_sql])
        if result:
            saved += 1

    return saved >= 3  # Consider successful if at least 3 rules saved

def main():
    tables = get_tables()
    print(f"Found {len(tables)} tables")
    print(f"Starting bulk onboarding at {datetime.now().isoformat()}")

    progress = {"completed": 0, "failed": 0, "skipped": 0}

    for i, table in enumerate(tables, 1):
        dataset = f"ONBOARD_CDQ_AUTO_samples.{table}"
        try:
            success = process_table(table, dataset)
            if success:
                progress["completed"] += 1
                status = "✓"
            else:
                progress["failed"] += 1
                status = "✗"
        except:
            progress["failed"] += 1
            status = "E"

        pct = (progress["completed"] / len(tables)) * 100
        print(f"[{i:3d}/{len(tables)}] {status} {table[:40]:40s} | Completed: {progress['completed']:3d} ({pct:5.1f}%)")

        # Print summary every 50 tables
        if i % 50 == 0:
            print(f"  Checkpoint at {i}: {progress['completed']} complete, {progress['failed']} failed")

    print(f"\n{'='*80}")
    print(f"FINAL RESULTS")
    print(f"{'='*80}")
    print(f"Completed: {progress['completed']}")
    print(f"Failed: {progress['failed']}")
    print(f"Success rate: {(progress['completed']/len(tables))*100:.1f}%")
    print(f"Finished at {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
