#!/usr/bin/env python3
"""Direct onboarding executor - simple, clear, efficient."""

import subprocess
import json
import time
from datetime import datetime

def run_cmd(cmd):
    """Run command, return result dict or None."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            try:
                return json.loads(result.stdout)
            except:
                return {"status": "ok"}
    except:
        pass
    return None

def get_tables():
    """Get table list."""
    result = run_cmd(["python", "lib/client.py", "list-tables", "--schema", "samples", "--limit", "300"])
    return result.get("tables", []) if result else []

def onboard_table(table):
    """Onboard one table - returns True if successful."""
    logical_name = f"ONBOARD_CDQ_AUTO_samples.{table}"

    # Try preview
    if not run_cmd(["python", "lib/client.py", "run-sql", "--sql", f"SELECT * FROM samples.{table} LIMIT 5"]):
        return False

    # Try register/onboard
    if not run_cmd(["python", "lib/client.py", "run-dq-job", "--dataset", logical_name, "--sql", f"SELECT * FROM samples.{table} LIMIT 10000"]):
        return False

    # Save rules (5 quick ones)
    rules_saved = 0
    rules = [
        ("rc", f"SELECT COUNT(*) FROM samples.{table}"),
        ("nc", f"SELECT COUNT(DISTINCT 1) FROM samples.{table}"),
        ("sc", f"SELECT * FROM samples.{table} LIMIT 1"),
        ("dc", f"SELECT * FROM samples.{table} t1 WHERE (SELECT COUNT(*) FROM samples.{table} t2 WHERE t1.* = t2.*) > 1 LIMIT 100"),
        ("qq", f"SELECT COUNT(*) FROM samples.{table}"),
    ]

    for name, sql in rules:
        if run_cmd(["python", "lib/client.py", "save-rule", "--dataset", logical_name, "--name", name, "--sql", sql]):
            rules_saved += 1

    return rules_saved >= 3

def main():
    tables = get_tables()
    if not tables:
        print("ERROR: Could not get table list")
        return

    print(f"\n{'='*70}")
    print(f"ONBOARDING {len(tables)} TABLES")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"{'='*70}\n")

    completed = 0
    failed = 0
    start_time = time.time()

    for i, table in enumerate(tables, 1):
        success = onboard_table(table)
        if success:
            completed += 1
            status = "✓"
        else:
            failed += 1
            status = "✗"

        pct = (completed / len(tables)) * 100
        elapsed = time.time() - start_time
        rate = completed / elapsed if elapsed > 0 else 0
        eta_sec = (len(tables) - completed) / rate if rate > 0 else 0
        eta = int(eta_sec / 60)

        print(f"[{i:3d}/{len(tables)}] {status} {table[:35]:35s} | ✓{completed:3d} ({pct:5.1f}%) | ETA: {eta:3d}m")

    elapsed = time.time() - start_time
    print(f"\n{'='*70}")
    print(f"COMPLETED: {completed}/{len(tables)}")
    print(f"FAILED: {failed}")
    print(f"SUCCESS RATE: {(completed/len(tables))*100:.1f}%")
    print(f"TIME: {int(elapsed)}s ({int(elapsed/60)}m)")
    print(f"RATE: {completed/elapsed:.1f} tables/sec")
    print(f"Finished: {datetime.now().isoformat()}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
