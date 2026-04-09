#!/usr/bin/env python3
"""Auto-CDQ skill wrapper - invokes the wizard via the skill_wrapper pattern."""

import subprocess
import sys
from pathlib import Path

# Get project root and wizard script path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
WIZARD_SCRIPT = PROJECT_ROOT / ".claude" / "bin" / "auto-cdq-wizard.py"

# Pass all CLI arguments directly to the wizard
result = subprocess.run(
    [sys.executable, str(WIZARD_SCRIPT)] + sys.argv[1:],
    cwd=PROJECT_ROOT,
)

sys.exit(result.returncode)


def test_cdq_connection() -> dict[str, Any]:
    """Validate CDQ connectivity using the shared client."""
    returncode, stdout, stderr = _run_root_client("test-connection")

    if returncode != 0:
        return {
            "success": False,
            "message": "Connection test failed.",
            "stderr": stderr.strip(),
        }

    payload = _parse_json_output(stdout)
    if not payload.get("success"):
        return {
            "success": False,
            "message": "Connection test returned an unsuccessful result.",
            "details": payload,
        }

    return {
        "success": True,
        "message": "Connection successful.",
        "details": payload,
    }


def list_tables(schema: str, search_term: str | None = None, limit: int = 20) -> dict[str, Any]:
    """List tables using the shared client implementation."""
    if not schema:
        raise ValueError("A schema is required for discovery.")
    if limit <= 0:
        raise ValueError("Limit must be greater than zero.")

    command = ["list-tables", "--schema", schema, "--limit", str(limit)]
    if search_term:
        command.extend(["--search", search_term])

    returncode, stdout, stderr = _run_root_client(*command)

    if returncode != 0:
        return {
            "success": False,
            "message": "Table discovery failed.",
            "stderr": stderr.strip(),
            "request": {
                "schema": schema,
                "search": search_term,
                "limit": limit,
            },
        }

    payload = _parse_json_output(stdout)
    return {
        "success": True,
        "message": "Table discovery completed.",
        "request": {
            "schema": schema,
            "search": search_term,
            "limit": limit,
        },
        "response": payload,
    }


def resolve_schema(explicit_schema: str | None) -> str:
    """Resolve the schema with safe defaults."""
    if explicit_schema:
        return explicit_schema

    config = get_config()
    return config.get("schema") or "samples"


def preview_data(schema: str, table: str, limit: int = 5) -> dict[str, Any]:
    """Preview sample rows from a table using the shared client."""
    if not schema or not table:
        raise ValueError("Both schema and table are required for preview.")
    if limit <= 0:
        raise ValueError("Limit must be greater than zero.")

    # Build SQL query - handle BigQuery format
    if "." in schema:
        full_table = f"`{schema}.{table}`"
    else:
        full_table = f"`{schema}.{table}`"

    sql = f"SELECT * FROM {full_table} LIMIT {limit}"
    returncode, stdout, stderr = _run_root_client("run-sql", "--sql", sql)

    if returncode != 0:
        return {
            "success": False,
            "message": "Preview failed.",
            "stderr": stderr.strip(),
            "request": {"schema": schema, "table": table, "limit": limit},
        }

    payload = _parse_json_output(stdout)
    return {
        "success": True,
        "message": "Preview completed.",
        "request": {"schema": schema, "table": table, "limit": limit},
        "response": payload,
    }


def get_schemas(connection: str | None = None) -> dict[str, Any]:
    """Fetch unique schemas from the catalog."""
    config = get_config()
    cxn = connection or config.get("cxn", "")

    # Query to get distinct schemas from INFORMATION_SCHEMA
    sql = """
    SELECT DISTINCT table_schema
    FROM INFORMATION_SCHEMA.TABLES
    WHERE table_type = 'BASE TABLE'
    ORDER BY table_schema
    LIMIT 50
    """
    returncode, stdout, stderr = _run_root_client("run-sql", "--sql", sql, "--connection", cxn)

    if returncode != 0:
        return {
            "success": False,
            "message": "Schema discovery failed.",
            "stderr": stderr.strip(),
        }

    payload = _parse_json_output(stdout)
    schemas = []
    if payload.get("rows"):
        for row in payload["rows"]:
            if row and len(row) > 0:
                schema_val = row[0].get("colValue")
                if schema_val:
                    schemas.append(schema_val)

    return {
        "success": True,
        "message": "Schema discovery completed.",
        "schemas": schemas,
        "count": len(schemas),
    }


def get_table_columns(schema: str, table: str) -> dict[str, Any]:
    """Get column metadata for a specific table."""
    if not schema or not table:
        raise ValueError("Both schema and table are required.")

    # Build SQL for column info
    if "." in schema:
        full_table = f"`{schema}.{table}`"
    else:
        full_table = f"`{schema}.{table}`"

    sql = f"""
    SELECT column_name, data_type, is_nullable
    FROM {full_table}
    LIMIT 100
    """
    # Use INFORMATION_SCHEMA.COLUMNS instead
    sql = f"""
    SELECT column_name, data_type, is_nullable
    FROM {schema.replace('.', '`.')}.INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = '{table}'
    ORDER BY ordinal_position
    """

    returncode, stdout, stderr = _run_root_client("run-sql", "--sql", sql)

    if returncode != 0:
        return {
            "success": False,
            "message": "Column discovery failed.",
            "stderr": stderr.strip(),
        }

    payload = _parse_json_output(stdout)
    columns = []
    if payload.get("rows"):
        for row in payload["rows"]:
            if row and len(row) >= 2:
                columns.append({
                    "name": row[0].get("colValue", ""),
                    "type": row[1].get("colValue", ""),
                    "nullable": row[2].get("colValue", "YES") if len(row) > 2 else "YES",
                })

    return {
        "success": True,
        "message": "Column discovery completed.",
        "columns": columns,
        "count": len(columns),
    }


def analyze_columns_for_rules(schema: str, table: str, limit: int = 1000) -> dict[str, Any]:
    """Analyze columns to suggest data quality rules.

    Checks for:
    - NULL counts (completeness)
    - Distinct counts (uniqueness)
    - Pattern detection (emails, phones, etc.)
    - Numeric ranges
    """
    if not schema or not table:
        raise ValueError("Both schema and table are required.")

    # First get column info
    cols_result = get_table_columns(schema, table)
    if not cols_result.get("success"):
        return cols_result

    columns = cols_result.get("columns", [])
    if not columns:
        return {
            "success": False,
            "message": "No columns found to analyze.",
        }

    # Build analysis query
    if "." in schema:
        full_table = f"`{schema}.{table}`"
    else:
        full_table = f"`{schema}.{table}`"

    # Build SELECT with aggregations for each column
    select_parts = []
    for col in columns:
        col_name = col["name"]
        # Skip columns with special chars that might break SQL
        safe_name = col_name.replace("`", "``")
        select_parts.append(f"COUNT(`{safe_name}`) as cnt_{safe_name}")
        select_parts.append(f"COUNT(DISTINCT `{safe_name}`) as uniq_{safe_name}")
        select_parts.append(f"SUM(CASE WHEN `{safe_name}` IS NULL THEN 1 ELSE 0 END) as nulls_{safe_name}")

    sql = f"SELECT {', '.join(select_parts)} FROM {full_table} LIMIT {limit}"

    returncode, stdout, stderr = _run_root_client("run-sql", "--sql", sql)

    if returncode != 0:
        return {
            "success": False,
            "message": "Column analysis failed.",
            "stderr": stderr.strip(),
        }

    payload = _parse_json_output(stdout)

    # Parse results and generate rule suggestions
    suggestions = []
    if payload.get("rows") and len(payload["rows"]) > 0:
        row = payload["rows"][0]
        total_rows = limit  # Approximate from LIMIT

        for col in columns:
            col_name = col["name"]
            safe_name = col_name.replace("`", "``")

            # Find the counts in the result row
            cnt_val = None
            nulls_val = None
            uniq_val = None

            for i, cell in enumerate(row):
                col_key = cell.get("colName", "") if isinstance(cell, dict) else ""
                if f"cnt_{safe_name}" in str(col_key):
                    cnt_val = int(cell.get("colValue", 0)) if cell.get("colValue") else total_rows
                elif f"nulls_{safe_name}" in str(col_key):
                    nulls_val = int(cell.get("colValue", 0)) if cell.get("colValue") else 0
                elif f"uniq_{safe_name}" in str(col_key):
                    uniq_val = int(cell.get("colValue", 0)) if cell.get("colValue") else 0

            # Use estimates if not found
            if cnt_val is None:
                cnt_val = total_rows
            if nulls_val is None:
                nulls_val = 0
            if uniq_val is None:
                uniq_val = cnt_val

            null_pct = (nulls_val / cnt_val * 100) if cnt_val > 0 else 0
            uniq_pct = (uniq_val / cnt_val * 100) if cnt_val > 0 else 100

            # Generate suggestions based on analysis
            col_type = col.get("type", "").upper()

            if null_pct > 0:
                suggestions.append({
                    "column": col_name,
                    "type": "completeness",
                    "priority": "high" if null_pct > 10 else "medium",
                    "null_count": nulls_val,
                    "null_pct": round(null_pct, 2),
                    "suggested_rule": f"SELECT * FROM {full_table} WHERE `{safe_name}` IS NULL",
                    "description": f"Check for NULL values in {col_name} ({null_pct:.1f}% null)",
                })

            if uniq_pct < 100 and cnt_val > 10:
                suggestions.append({
                    "column": col_name,
                    "type": "uniqueness",
                    "priority": "medium" if uniq_pct < 50 else "low",
                    "distinct_count": uniq_val,
                    "duplicate_pct": round(100 - uniq_pct, 2),
                    "suggested_rule": f"SELECT `{safe_name}`, COUNT(*) as cnt FROM {full_table} GROUP BY `{safe_name}` HAVING cnt > 1",
                    "description": f"Check for duplicates in {col_name} ({100 - uniq_pct:.1f}% duplicates)",
                })

            # Detect email pattern
            if "email" in col_name.lower() or "mail" in col_name.lower():
                suggestions.append({
                    "column": col_name,
                    "type": "validity",
                    "priority": "medium",
                    "suggested_rule": f"SELECT * FROM {full_table} WHERE `{safe_name}` NOT LIKE '%@%.%' OR `{safe_name}` IS NULL",
                    "description": f"Validate email format in {col_name}",
                })

            # Numeric range suggestions
            if col_type in ("INTEGER", "INT", "FLOAT", "DOUBLE", "NUMERIC", "DECIMAL"):
                suggestions.append({
                    "column": col_name,
                    "type": "range",
                    "priority": "low",
                    "suggested_rule": f"SELECT * FROM {full_table} WHERE `{safe_name}` < 0",
                    "description": f"Check for negative values in {col_name}",
                })

    return {
        "success": True,
        "message": "Column analysis completed.",
        "columns_analyzed": len(columns),
        "suggestions": suggestions,
        "suggestion_count": len(suggestions),
    }


def test_rule_sql(schema: str, table: str, rule_sql: str) -> dict[str, Any]:
    """Test a rule SQL to see how many rows it would flag."""
    if not schema or not table or not rule_sql:
        raise ValueError("Schema, table, and rule SQL are required.")

    # Run the rule SQL
    returncode, stdout, stderr = _run_root_client("run-sql", "--sql", rule_sql)

    if returncode != 0:
        return {
            "success": False,
            "message": "Rule SQL test failed.",
            "stderr": stderr.strip(),
            "sql": rule_sql,
        }

    payload = _parse_json_output(stdout)
    row_count = len(payload.get("rows", [])) if payload else 0

    return {
        "success": True,
        "message": "Rule SQL test completed.",
        "sql": rule_sql,
        "flagged_rows": row_count,
        "details": payload,
    }


def run_onboarding_job(dataset_name: str, schema: str, table: str, limit: int = 10000) -> dict[str, Any]:
    """Run a DQ onboarding job for a dataset."""
    if not dataset_name or not schema or not table:
        raise ValueError("Dataset name, schema, and table are required.")

    # Build source SQL
    if "." in schema:
        full_table = f"`{schema}.{table}`"
    else:
        full_table = f"`{schema}.{table}`"

    source_sql = f"SELECT * FROM {full_table} LIMIT {limit}"

    returncode, stdout, stderr = _run_root_client(
        "run-dq-job",
        "--dataset", dataset_name,
        "--sql", source_sql,
    )

    if returncode != 0:
        return {
            "success": False,
            "message": "Onboarding job failed.",
            "stderr": stderr.strip(),
        }

    payload = _parse_json_output(stdout)
    return {
        "success": True,
        "message": "Onboarding job started.",
        "dataset": dataset_name,
        "details": payload,
    }


def check_job_status(dataset_name: str, run_id: str = None) -> dict[str, Any]:
    """Check the status of a DQ job."""
    returncode, stdout, stderr = _run_root_client("get-jobs")

    if returncode != 0:
        return {
            "success": False,
            "message": "Job status check failed.",
            "stderr": stderr.strip(),
        }

    payload = _parse_json_output(stdout)
    jobs = payload.get("data", []) if isinstance(payload, dict) else payload

    # Find matching job
    matching_job = None
    for job in jobs:
        if job.get("dataset") == dataset_name:
            matching_job = job
            break

    return {
        "success": True,
        "message": "Job status retrieved.",
        "job": matching_job,
        "all_jobs": jobs[:10],  # Return recent jobs for context
    }


def get_rule_suggestions_for_table(schema: str, table: str) -> dict[str, Any]:
    """Get rule suggestions for a specific table (wrapper around analyze_columns_for_rules)."""
    return analyze_columns_for_rules(schema, table)


def save_rule_to_dataset(dataset_name: str, rule_name: str, rule_sql: str, points: int = 1, perc: int = 1) -> dict[str, Any]:
    """Save a rule to a dataset."""
    returncode, stdout, stderr = _run_root_client(
        "save-rule",
        "--dataset", dataset_name,
        "--name", rule_name,
        "--sql", rule_sql,
        "--points", str(points),
        "--perc", str(perc),
    )

    if returncode != 0:
        return {
            "success": False,
            "message": "Rule save failed.",
            "stderr": stderr.strip(),
        }

    payload = _parse_json_output(stdout)
    return {
        "success": True,
        "message": f"Rule '{rule_name}' saved successfully.",
        "details": payload,
    }


def get_existing_rules(dataset_name: str) -> dict[str, Any]:
    """Get existing rules for a dataset."""
    returncode, stdout, stderr = _run_root_client("get-rules", "--dataset", dataset_name)

    if returncode != 0:
        return {
            "success": False,
            "message": "Failed to get rules.",
            "stderr": stderr.strip(),
        }

    payload = _parse_json_output(stdout)
    return {
        "success": True,
        "message": "Rules retrieved.",
        "rules": payload.get("items", []),
        "count": len(payload.get("items", [])),
    }


def get_dataset_info(dataset_name: str) -> dict[str, Any]:
    """Get dataset configuration."""
    returncode, stdout, stderr = _run_root_client("get-dataset", "--dataset", dataset_name)

    if returncode != 0:
        return {
            "success": False,
            "message": "Failed to get dataset info.",
            "stderr": stderr.strip(),
        }

    payload = _parse_json_output(stdout)
    return {
        "success": True,
        "message": "Dataset info retrieved.",
        "dataset": payload,
    }


def get_dq_results(dataset_name: str, run_id: str) -> dict[str, Any]:
    """Get DQ job results."""
    returncode, stdout, stderr = _run_root_client(
        "get-results",
        "--dataset", dataset_name,
        "--run-id", run_id,
    )

    if returncode != 0:
        return {
            "success": False,
            "message": "Failed to get results.",
            "stderr": stderr.strip(),
        }

    payload = _parse_json_output(stdout)
    return {
        "success": True,
        "message": "Results retrieved.",
        "results": payload,
    }


def placeholder_next_steps() -> list[dict[str, str]]:
    """Return guided next-step options for the current slice."""
    return [
        {
            "label": "Preview sample rows",
            "status": "ready",
            "description": "Preview data using run-sql.",
        },
        {
            "label": "Start onboarding",
            "status": "ready",
            "description": "Register dataset using run-dq-job.",
        },
        {
            "label": "Refine search",
            "status": "ready",
            "description": "Run discovery again with a different search term.",
        },
        {
            "label": "Exit",
            "status": "ready",
            "description": "Finish the guided discovery session.",
        },
    ]


def run_discovery_workflow(args: argparse.Namespace) -> int:
    """Run the first implemented discovery slice."""
    schema = resolve_schema(args.schema)
    search_term = args.search or None
    limit = args.limit

    result: dict[str, Any] = {
        "workflow": "discovery",
        "schema": schema,
        "search": search_term,
        "limit": limit,
        "next_steps": placeholder_next_steps(),
    }

    try:
        connection = test_cdq_connection()
        result["connection_test"] = connection
        if not connection.get("success"):
            result["status"] = "failed"
            result["message"] = "Discovery stopped because the CDQ connection test failed."
            print(json.dumps(result, indent=2))
            return 1

        discovery = list_tables(schema=schema, search_term=search_term, limit=limit)
        result["list_tables"] = discovery

        if not discovery.get("success"):
            result["status"] = "failed"
            result["message"] = "Discovery stopped because list-tables failed."
            print(json.dumps(result, indent=2))
            return 1

        payload = discovery.get("response", {})
        tables = payload.get("tables", [])
        result["status"] = "ok"
        result["message"] = "Discovery completed successfully."
        result["summary"] = {
            "count": payload.get("count", len(tables)),
            "tables": tables,
        }
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        result["status"] = "failed"
        result["message"] = "Discovery failed unexpectedly."
        result["error"] = str(exc)
        print(json.dumps(result, indent=2))
        return 1


def run_placeholder_workflow(workflow: str) -> int:
    """Return a structured placeholder response for future increments."""
    payload = {
        "workflow": workflow,
        "status": "placeholder",
        "message": (
            f"The {workflow} workflow is not wired yet in auto-cdq-enhanced. "
            "Use the discovery workflow for the first end-to-end guided slice."
        ),
        "next_steps": [
            "Run discovery",
            "Exit",
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0


def run_onboarding_workflow(args: argparse.Namespace) -> int:
    """Run the onboarding workflow."""
    schema = resolve_schema(args.schema)
    table = args.table
    dataset_name = args.dataset or f"{table}_dq"
    limit = args.limit or 10000

    result: dict[str, Any] = {
        "workflow": "onboarding",
        "schema": schema,
        "table": table,
        "dataset": dataset_name,
        "limit": limit,
    }

    try:
        # Test the source query first
        if "." in schema:
            full_table = f"`{schema}.{table}`"
        else:
            full_table = f"`{schema}.{table}`"

        test_sql = f"SELECT * FROM {full_table} LIMIT 10"
        returncode, stdout, stderr = _run_root_client("run-sql", "--sql", test_sql)

        if returncode != 0:
            result["status"] = "failed"
            result["message"] = "Source query validation failed."
            result["stderr"] = stderr.strip()
            print(json.dumps(result, indent=2))
            return 1

        # Run the onboarding job
        job_result = run_onboarding_job(dataset_name, schema, table, limit)
        result["job"] = job_result

        if not job_result.get("success"):
            result["status"] = "failed"
            result["message"] = "Onboarding job failed."
            print(json.dumps(result, indent=2))
            return 1

        result["status"] = "ok"
        result["message"] = f"Onboarding job started for dataset '{dataset_name}'."
        print(json.dumps(result, indent=2))
        return 0

    except Exception as exc:
        result["status"] = "failed"
        result["message"] = "Onboarding failed unexpectedly."
        result["error"] = str(exc)
        print(json.dumps(result, indent=2))
        return 1


def run_rules_workflow(args: argparse.Namespace) -> int:
    """Run the rules analysis and suggestion workflow."""
    schema = resolve_schema(args.schema)
    table = args.table

    result: dict[str, Any] = {
        "workflow": "rules",
        "schema": schema,
        "table": table,
    }

    try:
        # Analyze columns for rule suggestions
        analysis = analyze_columns_for_rules(schema, table)
        result["analysis"] = analysis

        if not analysis.get("success"):
            result["status"] = "failed"
            result["message"] = "Rule analysis failed."
            print(json.dumps(result, indent=2))
            return 1

        result["status"] = "ok"
        result["message"] = f"Analyzed {analysis.get('columns_analyzed', 0)} columns, found {analysis.get('suggestion_count', 0)} rule suggestions."
        print(json.dumps(result, indent=2))
        return 0

    except Exception as exc:
        result["status"] = "failed"
        result["message"] = "Rules workflow failed unexpectedly."
        result["error"] = str(exc)
        print(json.dumps(result, indent=2))
        return 1


def run_preview_workflow(args: argparse.Namespace) -> int:
    """Run a data preview workflow."""
    schema = resolve_schema(args.schema)
    table = args.table
    limit = args.limit or 5

    result: dict[str, Any] = {
        "workflow": "preview",
        "schema": schema,
        "table": table,
        "limit": limit,
    }

    try:
        preview = preview_data(schema, table, limit)
        result["preview"] = preview

        if not preview.get("success"):
            result["status"] = "failed"
            result["message"] = "Preview failed."
            print(json.dumps(result, indent=2))
            return 1

        result["status"] = "ok"
        result["message"] = "Preview completed successfully."
        print(json.dumps(result, indent=2))
        return 0

    except Exception as exc:
        result["status"] = "failed"
        result["message"] = "Preview failed unexpectedly."
        result["error"] = str(exc)
        print(json.dumps(result, indent=2))
        return 1


def run_get_schemas_workflow(args: argparse.Namespace) -> int:
    """Run schema discovery workflow."""
    try:
        result = get_schemas(args.connection)

        if not result.get("success"):
            print(json.dumps(result, indent=2))
            return 1

        print(json.dumps(result, indent=2))
        return 0

    except Exception as exc:
        print(json.dumps({
            "status": "failed",
            "message": "Schema discovery failed.",
            "error": str(exc),
        }, indent=2))
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Auto-CDQ Enhanced - Guided CDQ workflow helper",
    )
    parser.add_argument(
        "workflow",
        nargs="?",
        default="discovery",
        choices=["discovery", "onboarding", "rules", "preview", "get-schemas"],
        help="Workflow to validate locally",
    )
    parser.add_argument("--schema", help="Schema for discovery")
    parser.add_argument("--search", help="Table search term for discovery")
    parser.add_argument("--table", help="Table name for onboarding/rules/preview")
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number (tables for discovery, rows for preview/onboarding)",
    )
    parser.add_argument("--dataset", help="Dataset name for onboarding")
    parser.add_argument("--connection", help="Connection name")
    args = parser.parse_args()

    if args.workflow == "discovery":
        return run_discovery_workflow(args)
    elif args.workflow == "onboarding":
        return run_onboarding_workflow(args)
    elif args.workflow == "rules":
        return run_rules_workflow(args)
    elif args.workflow == "preview":
        return run_preview_workflow(args)
    elif args.workflow == "get-schemas":
        return run_get_schemas_workflow(args)
    return run_placeholder_workflow(args.workflow)


if __name__ == "__main__":
    sys.exit(main())
