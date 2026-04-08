#!/usr/bin/env python3
"""Lightweight CLI client for Collibra Data Quality API.

A single-file wrapper for all CDQ API operations. Each command maps to a skill.

Usage:
    python lib/client.py test-connection
    python lib/client.py run-sql --sql "SELECT 1"
    python lib/client.py get-rules --dataset "my_table"
    python lib/client.py save-rule --dataset "my_table" --name "Rule" --sql "SELECT 1"
    python lib/client.py run-dq-job --dataset "my_table" --run-id "2025-01-23" --sql "SELECT * FROM table"
    python lib/client.py search-catalog --query "customer"
    python lib/client.py get-jobs
    python lib/client.py get-dataset --dataset "my_table"
    python lib/client.py get-results --dataset "my_table" --run-id "2025-01-23"
    python lib/client.py get-alerts --dataset "my_table"
    python lib/client.py save-alert --dataset "my_table" --name "Alert" --condition "score < 90"
"""

import argparse
import json
import os
import sys
from datetime import datetime

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Import auth module from same directory
from auth import get_config, get_headers, get_token, test_connection


def _api_get(endpoint: str, params: dict = None) -> dict:
    """Make GET request to CDQ API."""
    config = get_config()
    url = f"{config['url']}{endpoint}"
    response = requests.get(
        url,
        headers=get_headers(),
        params=params,
        timeout=60,
        verify=config["verify_ssl"]
    )
    response.raise_for_status()
    return response.json()


def _api_post(endpoint: str, payload: dict, params: dict = None) -> dict:
    """Make POST request to CDQ API."""
    config = get_config()
    url = f"{config['url']}{endpoint}"
    response = requests.post(
        url,
        headers=get_headers(),
        json=payload,
        params=params,
        timeout=60,
        verify=config["verify_ssl"]
    )
    response.raise_for_status()
    return response.json()


def _api_put(endpoint: str, payload: dict) -> dict:
    """Make PUT request to CDQ API."""
    config = get_config()
    url = f"{config['url']}{endpoint}"
    response = requests.put(
        url,
        headers=get_headers(),
        json=payload,
        timeout=60,
        verify=config["verify_ssl"]
    )
    response.raise_for_status()
    return response.json()


# Command implementations


def cmd_test_connection(args):
    """Test connection to CDQ API."""
    result = test_connection()
    _print_json(result)
    return 0 if result["success"] else 1


def cmd_run_sql(args):
    """Execute SQL query against configured datasource."""
    config = get_config()
    params = {
        "sql": args.sql,
        "cxn": args.connection or config["cxn"],
    }
    result = _api_post("/v2/getsqlresult", payload={}, params=params)
    _print_json(result)


def cmd_list_tables(args):
    """List tables in a schema by querying INFORMATION_SCHEMA."""
    config = get_config()
    schema = args.schema or config.get("schema", "")
    connection = args.connection or config["cxn"]
    limit = args.limit or 20
    search = args.search

    if not schema:
        print("Error: --schema is required (or set DQ_SCHEMA in .env)", file=sys.stderr)
        return 1

    # Build SQL query - BigQuery uses backticks and project.dataset format
    # PostgreSQL/MySQL use regular quotes
    # Default to BigQuery-style for now as that's what's been tested
    sql_parts = [
        "SELECT table_name FROM",
    ]

    # BigQuery format: `project.schema.INFORMATION_SCHEMA.TABLES`
    # Check if schema contains project.dataset format
    if "." in schema:
        sql_parts.append(f"`{schema}.INFORMATION_SCHEMA.TABLES`")
    else:
        # Assume just dataset, use default project
        sql_parts.append(f"`{schema}.INFORMATION_SCHEMA.TABLES`")

    sql_parts.append("WHERE table_type = 'BASE TABLE'")

    if search:
        # If user provides explicit wildcards (%, _), use as-is; otherwise wrap with % for substring match
        if '%' in search or '_' in search:
            sql_parts.append(f"AND LOWER(table_name) LIKE '{search.lower()}'")
        else:
            sql_parts.append(f"AND LOWER(table_name) LIKE '%{search.lower()}%'")

    sql_parts.append("ORDER BY table_name")
    sql_parts.append(f"LIMIT {limit}")

    sql = " ".join(sql_parts)

    params = {
        "sql": sql,
        "cxn": connection,
    }

    result = _api_post("/v2/getsqlresult", payload={}, params=params)

    # Parse the result - extract table names from the nested format
    if result.get("rows"):
        tables = []
        for row in result["rows"]:
            if row and len(row) > 0:
                table_name = row[0].get("colValue")
                if table_name:
                    tables.append(table_name)

        output = {
            "tables": tables,
            "count": len(tables),
            "schema": schema,
            "search": search,
            "limit": limit,
        }
        _print_json(output)
    else:
        _print_json({
            "tables": [],
            "count": 0,
            "schema": schema,
            "search": search,
            "error": result.get("exception", "No tables found")
        })

    return 0


def _apply_limit(result, limit, item_name="items"):
    """Apply limit to list result and notify if limit was hit."""
    if limit and isinstance(result, list) and len(result) >= limit:
        print(f"# Note: Showing {limit} {item_name}. There may be more. Remove --limit to see all.", file=sys.stderr)
        return result[:limit]
    return result


def _print_json(result, max_chars=500000):
    """Print JSON with truncation if too large."""
    json_str = json.dumps(result, indent=2)
    if len(json_str) > max_chars:
        truncated = json_str[:max_chars]
        print(f"# Note: Output truncated to {max_chars:,} characters. There may be more.", file=sys.stderr)
        print(truncated)
    else:
        print(json_str)


def cmd_get_rules(args):
    """Get DQ rules for a dataset."""
    result = _api_get(f"/v3/rules/{args.dataset}")
    result = _apply_limit(result, args.limit, "rules")
    _print_json(result)


def cmd_save_rule(args):
    """Create a new DQ rule."""
    payload = {
        "dataset": args.dataset,
        "ruleNm": args.name,
        "ruleType": "SQLF",
        "ruleValue": args.sql,
        "points": args.points or 1,
        "perc": args.perc or 1,
        "ruleRepo": "",
        "columnName": "",
        "businessCategory": "",
        "businessDesc": "",
        "dimId": None,
    }
    result = _api_post("/v3/rules", payload)
    _print_json(result)


def cmd_run_dq_job(args):
    """Run DQ job on a dataset."""
    config = get_config()
    run_id = args.run_id or datetime.now().strftime("%Y-%m-%d")

    # Step 1: Register dataset definition
    reg_data = {
        "dataset": args.dataset,
        "runId": run_id,
        "pushdown": {
            "sourceQuery": args.sql,
            "connectionName": args.connection or config["cxn"],
        },
        "agentId": {"id": 0},
        "profile": {"on": True},
    }

    reg_result = _api_put("/v3/datasetDefs", reg_data)

    # Step 2: Run the job
    params = {"dataset": args.dataset, "runDate": run_id}
    run_result = _api_post("/v3/jobs/run", payload={}, params=params)

    _print_json({"registration": reg_result, "job": run_result})


def cmd_search_catalog(args):
    """Search data catalog."""
    config = get_config()
    limit = args.limit or 50
    params = {
        "draw": "3",
        "start": "0",
        "length": str(limit),
        "search[value]": args.query,
        "filterPushdownPullup": "1",
        "order[0][column]": "0",
        "order[0][dir]": "asc",
        "filterSource": args.connection or config["cxn"],
    }
    result = _api_get("/v2/getdataassetsarrforserversidewithmultifilters", params)
    # Notify if there may be more results
    if isinstance(result, dict) and result.get("recordsFiltered", 0) >= limit:
        print(f"# Note: Showing {limit} datasets. There may be more. Remove --limit to see all.", file=sys.stderr)
    _print_json(result)


def cmd_get_jobs(args):
    """List queued DQ jobs."""
    limit = args.limit or 10
    params = {
        "jobStatus": args.status or "",
        "limit": str(limit),
    }
    result = _api_get("/v2/getowlcheckq", params)
    # Handle dict response with "data" key
    data_list = result.get("data", result) if isinstance(result, dict) else result
    if isinstance(data_list, list) and len(data_list) >= limit:
        print(f"# Note: Showing {limit} jobs. There may be more. Remove --limit to see all.", file=sys.stderr)
    _print_json(result)


def cmd_get_dataset(args):
    """Get dataset definition."""
    params = {"dataset": args.dataset}
    result = _api_get("/v2/owl-options/get", params)
    _print_json(result)


def cmd_get_results(args):
    """Get DQ job results (hoot)."""
    params = {"dataset": args.dataset, "runId": args.run_id}
    result = _api_get("/v2/gethoot", params)
    _print_json(result)


def cmd_get_alerts(args):
    """Get alerts for a dataset."""
    params = {"dataset": args.dataset}
    result = _api_get("/v2/getalerts", params)
    _print_json(result)


def cmd_save_alert(args):
    """Create new alert."""
    payload = {
        "dataset": args.dataset,
        "alertNm": args.name,
        "alertCond": args.condition,
        "alertFormat": "EMAIL",
        "alertFormatValue": args.email,
        "alertMsg": args.message or f"{args.condition} for {args.dataset}",
        "batchName": "",
        "addRuleDetails": True,
        "active": True,
        "alertTypes": ["CONDITION"],
    }
    result = _api_post("/v3/alerts", payload)
    _print_json(result)


def cmd_get_recent_runs(args):
    """Get recent DQ job runs."""
    result = _api_get("/v2/getrecentruns")
    _print_json(result)


def cmd_auto_cdq(args):
    """Run the auto-cdq guided workflow."""
    # This will invoke the auto-cdq skill
    print("Launching Auto-CDQ guided workflow...")
    print("Use /auto-cdq directly for the interactive experience.")
    # In a real implementation, this would launch the interactive workflow
    # For now, we'll just point to the skill
    print("Available workflows:")
    print("  /auto-cdq discovery  - Discover and preview tables")
    print("  /auto-cdq onboarding - Register datasets with validation")
    print("  /auto-cdq rules      - Generate and save quality rules")
    print("  /auto-cdq monitor    - Monitor job performance")
    print("  /auto-cdq alerts     - Configure quality alerts")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Collibra Data Quality API Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # test-connection
    p_test = subparsers.add_parser("test-connection", help="Test API connection")
    p_test.set_defaults(func=cmd_test_connection)

    # run-sql
    p_sql = subparsers.add_parser("run-sql", help="Execute SQL query")
    p_sql.add_argument("--sql", required=True, help="SQL query string")
    p_sql.add_argument("--connection", help="Datasource connection name")
    p_sql.set_defaults(func=cmd_run_sql)

    # list-tables
    p_list = subparsers.add_parser("list-tables", help="List tables in a schema")
    p_list.add_argument("--schema", help="Schema/dataset name (e.g., samples)")
    p_list.add_argument("--search", help="Filter tables by name substring")
    p_list.add_argument("--limit", type=int, default=20, help="Max tables to return (default: 20)")
    p_list.add_argument("--connection", help="Datasource connection name")
    p_list.set_defaults(func=cmd_list_tables)

    # get-rules
    p_rules = subparsers.add_parser("get-rules", help="Get DQ rules for dataset")
    p_rules.add_argument("--dataset", required=True, help="Dataset name")
    p_rules.add_argument("--limit", type=int, help="Limit number of rules returned")
    p_rules.set_defaults(func=cmd_get_rules)

    # save-rule
    p_save_rule = subparsers.add_parser("save-rule", help="Create DQ rule")
    p_save_rule.add_argument("--dataset", required=True, help="Dataset name")
    p_save_rule.add_argument("--name", required=True, help="Rule name")
    p_save_rule.add_argument("--sql", required=True, help="Rule SQL")
    p_save_rule.add_argument("--points", type=int, default=1, help="Rule points")
    p_save_rule.add_argument("--perc", type=int, default=1, help="Percentage threshold")
    p_save_rule.set_defaults(func=cmd_save_rule)

    # run-dq-job
    p_run_job = subparsers.add_parser("run-dq-job", help="Run DQ job on dataset")
    p_run_job.add_argument("--dataset", required=True, help="Dataset name")
    p_run_job.add_argument("--run-id", help="Run ID (default: today's date)")
    p_run_job.add_argument("--sql", required=True, help="Source SQL query")
    p_run_job.add_argument("--connection", help="Datasource connection name")
    p_run_job.set_defaults(func=cmd_run_dq_job)

    # search-catalog
    p_search = subparsers.add_parser("search-catalog", help="Search data catalog")
    p_search.add_argument("--query", required=True, help="Search query")
    p_search.add_argument("--limit", type=int, default=50, help="Max results")
    p_search.add_argument("--connection", help="Datasource connection name")
    p_search.set_defaults(func=cmd_search_catalog)

    # get-jobs
    p_jobs = subparsers.add_parser("get-jobs", help="List queued DQ jobs")
    p_jobs.add_argument("--status", help="Filter by status")
    p_jobs.add_argument("--limit", type=int, default=10, help="Max results")
    p_jobs.set_defaults(func=cmd_get_jobs)

    # get-dataset
    p_dataset = subparsers.add_parser("get-dataset", help="Get dataset definition")
    p_dataset.add_argument("--dataset", required=True, help="Dataset name")
    p_dataset.set_defaults(func=cmd_get_dataset)

    # get-results
    p_results = subparsers.add_parser("get-results", help="Get DQ job results")
    p_results.add_argument("--dataset", required=True, help="Dataset name")
    p_results.add_argument("--run-id", required=True, help="Run ID")
    p_results.set_defaults(func=cmd_get_results)

    # get-alerts
    p_alerts = subparsers.add_parser("get-alerts", help="Get alerts for dataset")
    p_alerts.add_argument("--dataset", required=True, help="Dataset name")
    p_alerts.set_defaults(func=cmd_get_alerts)

    # save-alert
    p_save_alert = subparsers.add_parser("save-alert", help="Create new alert")
    p_save_alert.add_argument("--dataset", required=True, help="Dataset name")
    p_save_alert.add_argument("--name", required=True, help="Alert name")
    p_save_alert.add_argument("--condition", required=True, help="Alert condition")
    p_save_alert.add_argument("--email", required=True, help="Email address")
    p_save_alert.add_argument("--message", help="Alert message")
    p_save_alert.set_defaults(func=cmd_save_alert)

    # auto-cdq
    p_auto_cdq = subparsers.add_parser("auto-cdq", help="Guided CDQ workflow assistant")
    p_auto_cdq.add_argument("workflow", nargs="?", help="Specific workflow to run (discovery, onboarding, rules, monitor, alerts)")
    p_auto_cdq.set_defaults(func=cmd_auto_cdq)

    # get-recent-runs
    p_recent = subparsers.add_parser("get-recent-runs", help="Get recent DQ runs")
    p_recent.set_defaults(func=cmd_get_recent_runs)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        return args.func(args)
    except requests.HTTPError as e:
        print(f"API Error: {e.response.status_code} - {e.response.text}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())