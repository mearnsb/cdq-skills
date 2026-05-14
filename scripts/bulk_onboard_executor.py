#!/usr/bin/env python3
"""
Bulk onboarding executor - processes all tables through complete workflow.

Executes Phase 1-3 for each table:
1. Preview (LIMIT 5)
2. Onboard (register dataset + run job with LIMIT 10000)
3. Rules (save 10 context-specific rules)

Tracks progress and handles failures gracefully.
"""

import json
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

class BulkOnboardExecutor:
    """Executes bulk onboarding workflow."""

    PROGRESS_FILE = ".onboarding-progress.json"
    MANIFEST_FILE = "onboarding-manifest.json"
    LOG_FILE = "onboarding-execution.log"

    def __init__(self):
        self.progress = self._load_progress()
        self.manifest = self._load_manifest()
        self.log_lines = []

    def _log(self, msg: str, end: str = "\n"):
        """Log message to console and file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {msg}"
        print(log_entry, end=end)
        self.log_lines.append(log_entry)

    def _save_log(self):
        """Save log to file."""
        with open(self.LOG_FILE, "a") as f:
            for line in self.log_lines:
                f.write(line + "\n")

    def _load_progress(self) -> Dict[str, Any]:
        """Load progress from file."""
        if os.path.exists(self.PROGRESS_FILE):
            with open(self.PROGRESS_FILE) as f:
                return json.load(f)
        return {
            "start_time": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "completed": [],
            "in_progress": None,
            "failed": [],
            "pending": [],
            "summary": {"total": 0, "completed": 0, "in_progress": 0, "pending": 0, "failed": 0},
        }

    def _save_progress(self):
        """Save progress to file."""
        self.progress["last_updated"] = datetime.now().isoformat()
        with open(self.PROGRESS_FILE, "w") as f:
            json.dump(self.progress, f, indent=2)

    def _load_manifest(self) -> Dict[str, Any]:
        """Load manifest."""
        if os.path.exists(self.MANIFEST_FILE):
            with open(self.MANIFEST_FILE) as f:
                return json.load(f)
        return {"tables": []}

    def run_sql(self, sql: str) -> Optional[Dict]:
        """Execute SQL query."""
        try:
            result = subprocess.run(
                ["python", "lib/client.py", "run-sql", "--sql", sql],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            return None
        except Exception as e:
            self._log(f"SQL error: {e}")
            return None

    def run_dq_job(self, dataset: str, sql: str) -> bool:
        """Run DQ job (onboarding phase)."""
        try:
            result = subprocess.run(
                ["python", "lib/client.py", "run-dq-job", "--dataset", dataset, "--sql", sql],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if "registration" in data and "dataset" in data["registration"]:
                    return True
            return False
        except Exception as e:
            self._log(f"Job error: {e}")
            return False

    def save_rule(self, dataset: str, rule_name: str, rule_sql: str) -> bool:
        """Save a single rule."""
        try:
            result = subprocess.run(
                ["python", "lib/client.py", "save-rule",
                 "--dataset", dataset, "--name", rule_name, "--sql", rule_sql],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                return True
            return False
        except Exception as e:
            self._log(f"Rule save error: {e}")
            return False

    def phase1_preview(self, table: str) -> Optional[Dict]:
        """Phase 1: Preview table."""
        sql = f"SELECT * FROM samples.{table} LIMIT 5"
        return self.run_sql(sql)

    def phase2_onboard(self, table: str) -> bool:
        """Phase 2: Onboard table."""
        logical_name = f"ONBOARD_CDQ_AUTO_samples.{table}"
        sql = f"SELECT * FROM samples.{table} LIMIT 10000"
        return self.run_dq_job(logical_name, sql)

    def phase3_rules(self, table: str, preview_data: Dict) -> int:
        """Phase 3: Save 10 rules for table."""
        logical_name = f"ONBOARD_CDQ_AUTO_samples.{table}"
        phys_table = f"samples.{table}"
        columns = preview_data.get("schema", [])
        col_names = [c.get("name") for c in columns if c.get("name")]

        rules = [
            {
                "name": f"{col_names[0]}_not_null" if col_names else "col1_not_null",
                "sql": f"SELECT * FROM {phys_table} WHERE {col_names[0]} IS NULL LIMIT 100" if col_names else f"SELECT * FROM {phys_table} LIMIT 1"
            },
            {
                "name": f"{col_names[1]}_not_null" if len(col_names) > 1 else "col2_not_null",
                "sql": f"SELECT * FROM {phys_table} WHERE {col_names[1]} IS NULL LIMIT 100" if len(col_names) > 1 else f"SELECT * FROM {phys_table} LIMIT 1"
            },
            {
                "name": "duplicate_rows",
                "sql": f"SELECT * FROM {phys_table} t1 WHERE (SELECT COUNT(*) FROM {phys_table} t2 WHERE t1.* = t2.*) > 1 LIMIT 100"
            },
            {
                "name": "null_distribution",
                "sql": f"SELECT COUNT(*) as total_rows, COUNT({col_names[0]}) as non_null FROM {phys_table} LIMIT 1" if col_names else f"SELECT COUNT(*) as total_rows FROM {phys_table} LIMIT 1"
            },
            {
                "name": "row_count_summary",
                "sql": f"SELECT COUNT(*) as total_rows, COUNT(DISTINCT 1) as unique_rows FROM {phys_table} LIMIT 1"
            },
            {
                "name": "empty_string_check",
                "sql": f"SELECT * FROM {phys_table} WHERE {col_names[0]} = '' OR TRIM({col_names[0]}) = '' LIMIT 100" if col_names else f"SELECT * FROM {phys_table} LIMIT 1"
            },
            {
                "name": "data_length_check",
                "sql": f"SELECT * FROM {phys_table} WHERE LENGTH({col_names[0]}) > 50000 OR LENGTH({col_names[0]}) < 1 LIMIT 100" if col_names else f"SELECT * FROM {phys_table} LIMIT 1"
            },
            {
                "name": "control_character_check",
                "sql": f"SELECT * FROM {phys_table} WHERE {col_names[0]} REGEXP '[\\\\x00-\\\\x08\\\\x0B-\\\\x0C\\\\x0E-\\\\x1F\\\\x7F]' LIMIT 100" if col_names else f"SELECT * FROM {phys_table} LIMIT 1"
            },
            {
                "name": "whitespace_validation",
                "sql": f"SELECT * FROM {phys_table} WHERE REGEXP_LIKE({col_names[0]}, '^\\\\s+\$') LIMIT 100" if col_names else f"SELECT * FROM {phys_table} LIMIT 1"
            },
            {
                "name": "column_cardinality",
                "sql": f"SELECT {col_names[0]}, COUNT(*) as cnt FROM {phys_table} GROUP BY {col_names[0]} ORDER BY cnt DESC LIMIT 20" if col_names else f"SELECT * FROM {phys_table} LIMIT 1"
            }
        ]

        saved_count = 0
        for rule in rules:
            if self.save_rule(logical_name, rule["name"], rule["sql"]):
                saved_count += 1
                self._log(f"  ✓ Rule {saved_count}/10: {rule['name']}")
            else:
                self._log(f"  ✗ Rule failed: {rule['name']}")

        return saved_count

    def process_table(self, table: str) -> bool:
        """Process single table through all 3 phases."""
        self._log(f"\n{'='*80}")
        self._log(f"Processing: {table}")
        self._log(f"{'='*80}")

        self.progress["in_progress"] = table
        self._save_progress()

        # Phase 1: Preview
        self._log(f"[Phase 1] Previewing table...")
        preview = self.phase1_preview(table)
        if not preview:
            self._log(f"✗ Preview failed - skipping table")
            self.progress["failed"].append(table)
            self.progress["in_progress"] = None
            self._save_progress()
            return False

        row_count = preview.get("rowCount", 0)
        col_count = len(preview.get("schema", []))
        self._log(f"✓ Preview complete: {row_count} rows, {col_count} columns")

        # Phase 2: Onboard
        self._log(f"[Phase 2] Onboarding dataset...")
        if not self.phase2_onboard(table):
            self._log(f"✗ Onboarding failed - skipping table")
            self.progress["failed"].append(table)
            self.progress["in_progress"] = None
            self._save_progress()
            return False

        self._log(f"✓ Dataset registered: ONBOARD_CDQ_AUTO_samples.{table}")

        # Phase 3: Rules
        self._log(f"[Phase 3] Saving 10 rules...")
        rules_saved = self.phase3_rules(table, preview)
        self._log(f"✓ Rules saved: {rules_saved}/10")

        # Mark complete
        self.progress["completed"].append(table)
        if table in self.progress.get("pending", []):
            self.progress["pending"].remove(table)
        self.progress["in_progress"] = None
        self._save_progress()

        self._log(f"✅ Table complete: {table}")
        return True

    def execute_all(self, start_index: int = 0):
        """Execute all tables."""
        tables = self.manifest.get("tables", [])
        if not tables:
            self._log("No tables in manifest")
            return

        total = len(tables)
        completed = len(self.progress.get("completed", []))
        failed = len(self.progress.get("failed", []))

        self._log(f"\n{'='*80}")
        self._log(f"BULK ONBOARDING EXECUTOR")
        self._log(f"{'='*80}")
        self._log(f"Total tables: {total}")
        self._log(f"Already completed: {completed}")
        self._log(f"Failed: {failed}")
        self._log(f"Starting from index: {start_index}")

        for i, table_info in enumerate(tables[start_index:], start=start_index):
            # Skip if already completed
            table_name = table_info.get("name") if isinstance(table_info, dict) else table_info
            if table_name in self.progress["completed"]:
                self._log(f"[{i+1}/{total}] SKIPPED (already done): {table_name}")
                continue

            if table_name in self.progress["failed"]:
                self._log(f"[{i+1}/{total}] SKIPPED (previously failed): {table_name}")
                continue

            self._log(f"[{i+1}/{total}]", end=" ")
            success = self.process_table(table_name)

            # Update summary
            self.progress["summary"]["total"] = total
            self.progress["summary"]["completed"] = len(self.progress["completed"])
            self.progress["summary"]["failed"] = len(self.progress["failed"])
            self.progress["summary"]["pending"] = total - len(self.progress["completed"]) - len(self.progress["failed"])
            self._save_progress()

            # Print progress
            pct = (len(self.progress["completed"]) / total) * 100
            self._log(f"Progress: {len(self.progress['completed'])}/{total} ({pct:.1f}%)")

        self._log(f"\n{'='*80}")
        self._log(f"EXECUTION COMPLETE")
        self._log(f"Completed: {len(self.progress['completed'])}")
        self._log(f"Failed: {len(self.progress['failed'])}")
        self._log(f"Success rate: {(len(self.progress['completed'])/total)*100:.1f}%")
        self._log(f"{'='*80}\n")

        self._save_log()

def main():
    """Main entry point."""
    executor = BulkOnboardExecutor()

    # Determine start index (resume from where we left off)
    completed_count = len(executor.progress.get("completed", []))
    start_idx = completed_count

    # Execute all tables
    executor.execute_all(start_index=start_idx)

if __name__ == "__main__":
    main()
