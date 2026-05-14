#!/usr/bin/env python3
"""
Bulk onboarding orchestrator for Collibra DQ.

Orchestrates systematic onboarding of tables from samples schema:
1. Gets list of tables
2. Previews each table (LIMIT 5)
3. Generates 10 rule suggestions
4. Creates manifest for Claude skill execution
5. Tracks progress

Usage:
  python scripts/bulk_onboard_loop.py --schema samples --action list-tables
  python scripts/bulk_onboard_loop.py --schema samples --action generate-manifest
  python scripts/bulk_onboard_loop.py --schema samples --action check-progress
"""

import json
import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any


class BulkOnboardOrchestrator:
    """Orchestrates bulk onboarding workflow."""

    PROGRESS_FILE = ".onboarding-progress.json"
    MANIFEST_FILE = "onboarding-manifest.json"

    def __init__(self, schema: str = "samples"):
        self.schema = schema
        self.progress = self._load_progress()

    def _load_progress(self) -> Dict[str, Any]:
        """Load progress from file or initialize."""
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

    def get_tables(self) -> List[str]:
        """Get list of tables from schema."""
        cmd = ["python", "lib/client.py", "list-tables", "--schema", self.schema, "--limit", "200"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error listing tables: {result.stderr}")
            sys.exit(1)
        data = json.loads(result.stdout)
        return data.get("tables", [])

    def get_table_preview(self, table: str) -> Optional[Dict[str, Any]]:
        """Get preview of table (LIMIT 5)."""
        cmd = [
            "python",
            "lib/client.py",
            "run-sql",
            "--sql",
            f"SELECT * FROM {self.schema}.{table} LIMIT 5",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return None
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return None

    def analyze_table_schema(self, preview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze table schema from preview."""
        schema_info = preview_data.get("schema")
        if not schema_info:
            return {"row_count": 0, "column_count": 0, "columns": []}

        row_count = preview_data.get("rowCount", 0)

        columns = []
        for col in schema_info:
            columns.append({
                "name": col.get("name"),
                "type": col.get("type"),
                "null_percent": col.get("nullPercent", 0),
                "empty_percent": col.get("emptyPercent", 0),
                "cardinality": col.get("cardinality", 0),
                "is_key": col.get("isKey", False),
            })

        return {
            "row_count": row_count,
            "column_count": len(columns),
            "columns": columns,
        }

    def suggest_rules(self, table: str, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate 10 rule suggestions based on table structure."""
        rules = []
        columns = analysis["columns"]

        # Rule 1: NULL check on first important-looking column
        if columns:
            col = columns[0]
            rules.append({
                "name": f"{col['name']}_not_null",
                "description": f"Check {col['name']} is not NULL",
                "sql": f"SELECT * FROM {self.schema}.{table} WHERE {col['name']} IS NULL",
            })

        # Rule 2: NULL check on second column if exists
        if len(columns) > 1:
            col = columns[1]
            rules.append({
                "name": f"{col['name']}_not_null",
                "description": f"Check {col['name']} is not NULL",
                "sql": f"SELECT * FROM {self.schema}.{table} WHERE {col['name']} IS NULL",
            })

        # Rule 3: Duplicate detection (all columns)
        if len(columns) > 1:
            rules.append({
                "name": "duplicate_rows_exact",
                "description": "Detect exact duplicate rows",
                "sql": f"SELECT * FROM {self.schema}.{table} t1 WHERE EXISTS (SELECT 1 FROM {self.schema}.{table} t2 WHERE t1.* = t2.* AND t1.rowid > t2.rowid) LIMIT 100",
            })

        # Rule 4: Low cardinality check (first column with reasonable cardinality)
        for col in columns:
            if col["cardinality"] > 0 and col["cardinality"] < 20:
                rules.append({
                    "name": f"{col['name']}_valid_values",
                    "description": f"Check {col['name']} has expected cardinality",
                    "sql": f"SELECT {col['name']}, COUNT(*) as cnt FROM {self.schema}.{table} GROUP BY {col['name']} ORDER BY cnt DESC LIMIT 20",
                })
                break

        # Rule 5: Empty string check on first text column
        if columns:
            col = columns[0]
            rules.append({
                "name": f"{col['name']}_not_empty",
                "description": f"Check {col['name']} is not empty string",
                "sql": f"SELECT * FROM {self.schema}.{table} WHERE {col['name']} = '' OR TRIM({col['name']}) = ''",
            })

        # Rule 6: Length validation on first column
        if columns:
            col = columns[0]
            rules.append({
                "name": f"{col['name']}_length_valid",
                "description": f"Check {col['name']} length is reasonable",
                "sql": f"SELECT *, LENGTH({col['name']}) as col_len FROM {self.schema}.{table} WHERE LENGTH({col['name']}) > 50000 OR LENGTH({col['name']}) < 1 LIMIT 100",
            })

        # Rule 7: Control characters check
        if columns:
            col = columns[0]
            rules.append({
                "name": "no_control_characters",
                "description": "Detect control characters in data",
                "sql": f"SELECT * FROM {self.schema}.{table} WHERE {col['name']} REGEXP '[\\\\x00-\\\\x08\\\\x0B-\\\\x0C\\\\x0E-\\\\x1F\\\\x7F]' LIMIT 100",
            })

        # Rule 8: Whitespace-only check
        if columns:
            col = columns[0]
            rules.append({
                "name": f"{col['name']}_no_whitespace_only",
                "description": f"Check {col['name']} is not whitespace only",
                "sql": f"SELECT * FROM {self.schema}.{table} WHERE REGEXP_LIKE({col['name']}, '^\\\\s+$') LIMIT 100",
            })

        # Rule 9: NULL percentage check across all columns
        null_checks = []
        for col in columns:
            if col["null_percent"] > 0.01:  # More than 1% nulls
                null_checks.append(f"{col['name']} ({col['null_percent']*100:.1f}% nulls)")

        if null_checks:
            rules.append({
                "name": "columns_with_nulls",
                "description": f"Columns with significant nulls: {', '.join(null_checks[:3])}",
                "sql": f"SELECT COUNT(*) as total, " + ", ".join([f"SUM(CASE WHEN {col['name']} IS NULL THEN 1 ELSE 0 END) as {col['name']}_nulls" for col in columns[:5]]) + f" FROM {self.schema}.{table}",
            })
        else:
            # Rule 9 alternative: Data type validation
            rules.append({
                "name": "schema_consistency",
                "description": "Check all columns exist and have expected types",
                "sql": f"SELECT COUNT(*) as total_rows, COUNT(DISTINCT 1) as distinct_rows FROM {self.schema}.{table} LIMIT 1",
            })

        # Rule 10: Unexpected values/patterns
        rules.append({
            "name": "data_quality_summary",
            "description": "Summary of data quality metrics",
            "sql": f"SELECT COUNT(*) as total_rows, COUNT(DISTINCT 1) as unique_rows, COUNT(DISTINCT CAST(* AS STRING)) as row_diversity FROM {self.schema}.{table} LIMIT 1",
        })

        return rules[:10]  # Ensure exactly 10 rules

    def generate_manifest(self, tables: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate onboarding manifest for all tables."""
        if tables is None:
            tables = self.get_tables()

        manifest = {
            "schema": self.schema,
            "generated": datetime.now().isoformat(),
            "tables": [],
            "summary": {"total": len(tables), "previewed": 0, "failed": 0},
        }

        for i, table in enumerate(tables):
            print(f"[{i+1}/{len(tables)}] Analyzing {table}...", end=" ", flush=True)

            try:
                preview = self.get_table_preview(table)
                if not preview:
                    print("FAILED (no preview)")
                    manifest["summary"]["failed"] += 1
                    continue

                analysis = self.analyze_table_schema(preview)
                if not analysis or (analysis["row_count"] == 0 and analysis["column_count"] == 0):
                    print("FAILED (empty)")
                    manifest["summary"]["failed"] += 1
                    continue
            except Exception as e:
                print(f"FAILED ({str(e)[:30]})")
                manifest["summary"]["failed"] += 1
                continue
                rules = self.suggest_rules(table, analysis)

                manifest["tables"].append({
                    "name": table,
                    "schema": self.schema,
                    "logical_name": f"ONBOARD_CDQ_AUTO_{self.schema}.{table}",
                    "row_count": analysis["row_count"],
                    "column_count": analysis["column_count"],
                    "columns": [c["name"] for c in analysis["columns"]],
                    "suggested_rules": rules,
                })

                manifest["summary"]["previewed"] += 1
                print(f"✓ ({analysis['row_count']} rows, {analysis['column_count']} cols)")

        # Save manifest
        with open(self.MANIFEST_FILE, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"\nManifest saved to {self.MANIFEST_FILE}")
        return manifest

    def check_progress(self):
        """Display current progress."""
        summary = self.progress["summary"]
        print("\n=== Onboarding Progress ===")
        print(f"Total tables: {summary['total']}")
        print(f"Completed: {summary['completed']}")
        print(f"In progress: {summary['in_progress']}")
        print(f"Pending: {summary['pending']}")
        print(f"Failed: {summary['failed']}")

        if self.progress["completed"]:
            print(f"\nCompleted tables: {', '.join(self.progress['completed'][:5])}")
            if len(self.progress["completed"]) > 5:
                print(f"  ...and {len(self.progress['completed']) - 5} more")

        if self.progress["failed"]:
            print(f"\nFailed tables: {', '.join(self.progress['failed'])}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Bulk onboarding orchestrator for Collibra DQ")
    parser.add_argument("--schema", default="samples", help="Schema to onboard (default: samples)")
    parser.add_argument(
        "--action",
        choices=["list-tables", "generate-manifest", "check-progress"],
        default="generate-manifest",
        help="Action to perform",
    )
    parser.add_argument("--limit", type=int, default=200, help="Limit number of tables (default: 200)")

    args = parser.parse_args()

    orchestrator = BulkOnboardOrchestrator(schema=args.schema)

    if args.action == "list-tables":
        tables = orchestrator.get_tables()
        print(f"Found {len(tables)} tables in {args.schema} schema:")
        for table in tables[:20]:
            print(f"  - {table}")
        if len(tables) > 20:
            print(f"  ...and {len(tables) - 20} more")

    elif args.action == "generate-manifest":
        tables = orchestrator.get_tables()
        if args.limit:
            tables = tables[: args.limit]
        orchestrator.generate_manifest(tables)

    elif args.action == "check-progress":
        orchestrator.check_progress()


if __name__ == "__main__":
    main()
