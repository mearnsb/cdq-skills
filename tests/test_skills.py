#!/usr/bin/env python3
"""Fast, lightweight tests for CDQ skills.

Tests wrapper functionality and each command skill.
Run: python tests/test_skills.py

All tests should complete in < 30 seconds total.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Project root
ROOT = Path(__file__).parent.parent
LIB_CLIENT = ROOT / "lib" / "client.py"
SKILLS_DIR = ROOT / ".claude" / "skills"

# Command skills that should have lib/client.py wrappers
COMMAND_SKILLS = [
    "cdq-get-alerts",
    "cdq-get-dataset",
    "cdq-get-jobs",
    "cdq-get-recent-runs",
    "cdq-get-results",
    "cdq-get-rules",
    "cdq-list-tables",
    "cdq-run-dq-job",
    "cdq-run-sql",
    "cdq-save-alert",
    "cdq-save-rule",
    "cdq-search-catalog",
    "cdq-test-connection",
]

# Workflow skills (documentation-only, no wrapper needed after refactor)
WORKFLOW_SKILLS = [
    "cdq-workflow-explore-dataset",
    "cdq-workflow-run-complete-job",
    "cdq-workflow-save-complete-rule",
    "cdq-workflow-suggest-rules",
]


def run_command(cmd, timeout=30):
    """Run a command and return (success, output, error)."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=ROOT
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)


def test_wrapper_structure(skill_name):
    """Test that a skill has proper wrapper structure."""
    skill_path = SKILLS_DIR / skill_name
    lib_path = skill_path / "lib" / "client.py"
    skill_md = skill_path / "SKILL.md"

    issues = []

    # Check SKILL.md exists
    if not skill_md.exists():
        issues.append(f"Missing SKILL.md")

    # Check lib/client.py exists
    if not lib_path.exists():
        issues.append(f"Missing lib/client.py")
    else:
        # Check wrapper contains key patterns (new shared wrapper pattern)
        content = lib_path.read_text()
        if "skill_wrapper" not in content:
            issues.append("Wrapper missing skill_wrapper import")
        if "run_skill" not in content:
            issues.append("Wrapper missing run_skill call")

    return len(issues) == 0, issues


def test_test_connection():
    """Test cdq-test-connection command."""
    cmd = f"python lib/client.py test-connection"
    success, output, error = run_command(cmd, timeout=10)

    if not success:
        return False, f"Command failed: {error}"

    try:
        result = json.loads(output)
        if not result.get("success"):
            return False, "Connection test failed"
        return True, "Connection OK"
    except json.JSONDecodeError:
        return False, "Invalid JSON output"


def test_search_catalog():
    """Test cdq-search-catalog command (fast query)."""
    cmd = f'python lib/client.py search-catalog --query "samples" --limit 3'
    success, output, error = run_command(cmd, timeout=15)

    if not success:
        return False, f"Command failed: {error}"

    try:
        result = json.loads(output)
        data = result.get("dataAssetList", [])
        if len(data) == 0:
            return False, "No results found"
        return True, f"Found {len(data)} datasets"
    except json.JSONDecodeError:
        return False, "Invalid JSON output"


def test_get_rules():
    """Test cdq-get-rules command."""
    cmd = 'python lib/client.py get-rules --dataset "samples_sales_data" --limit 5'
    success, output, error = run_command(cmd, timeout=15)

    if not success:
        return False, f"Command failed: {error}"

    try:
        result = json.loads(output)
        if isinstance(result, list):
            return True, f"Got {len(result)} rules"
        elif isinstance(result, dict):
            return True, f"Got rules (dict format)"
        return False, "Unexpected output format"
    except json.JSONDecodeError:
        return False, "Invalid JSON output"


def test_run_sql():
    """Test cdq-run-sql command (simple query)."""
    cmd = 'python lib/client.py run-sql --sql "SELECT 1 as test" --connection BIGQUERY'
    success, output, error = run_command(cmd, timeout=15)

    if not success:
        return False, f"Command failed: {error}"

    try:
        result = json.loads(output)
        if result.get("rows"):
            return True, "SQL execution OK"
        return False, "No rows in result"
    except json.JSONDecodeError:
        return False, "Invalid JSON output"


def test_get_jobs():
    """Test cdq-get-jobs command."""
    cmd = 'python lib/client.py get-jobs --limit 3'
    success, output, error = run_command(cmd, timeout=15)

    if not success:
        return False, f"Command failed: {error}"

    try:
        result = json.loads(output)
        return True, "Jobs query OK"
    except json.JSONDecodeError:
        return False, "Invalid JSON output"


def test_get_recent_runs():
    """Test cdq-get-recent-runs command."""
    cmd = 'python lib/client.py get-recent-runs'
    success, output, error = run_command(cmd, timeout=15)

    if not success:
        return False, f"Command failed: {error}"

    try:
        result = json.loads(output)
        return True, "Recent runs query OK"
    except json.JSONDecodeError:
        return False, "Invalid JSON output"


def test_list_tables_prefix_search():
    """Test cdq-list-tables with LIKE prefix search (d%)."""
    cmd = 'python lib/client.py list-tables --schema samples --search "d%" --limit 50'
    success, output, error = run_command(cmd, timeout=15)

    if not success:
        return False, f"Command failed: {error}"

    try:
        result = json.loads(output)
        tables = result.get("tables", [])
        count = len(tables)
        # Should return tables starting with 'd' - expect at least 10
        if count >= 10:
            return True, f"Prefix search returned {count} tables"
        else:
            return False, f"Expected >=10 tables starting with 'd', got {count}"
    except json.JSONDecodeError:
        return False, "Invalid JSON output"


def test_wrapper_import(skill_name):
    """Test that a skill wrapper can import and run the main client."""
    skill_path = SKILLS_DIR / skill_name
    lib_path = skill_path / "lib" / "client.py"

    if not lib_path.exists():
        return False, "lib/client.py missing"

    # Try running the wrapper with --help to test import
    cmd = f"python {lib_path} --help"
    success, output, error = run_command(cmd, timeout=5)

    if not success:
        return False, f"Wrapper execution failed: {error}"

    if "Collibra" in output or "client.py" in output:
        return True, "Wrapper imports correctly"

    return False, "Wrapper did not produce expected output"


def main():
    print("=" * 60)
    print("CDQ Skills Test Suite")
    print("=" * 60)

    all_passed = True
    results = []

    # Test 1: Wrapper structure for command skills
    print("\n[1] Testing wrapper structure...")
    for skill in COMMAND_SKILLS:
        passed, issues = test_wrapper_structure(skill)
        status = "PASS" if passed else "FAIL"
        results.append((f"wrapper:{skill}", passed))
        if not passed:
            print(f"  {skill}: {status} - {issues}")
            all_passed = False
        else:
            print(f"  {skill}: {status}")

    # Test 2: Wrapper import test (spot check a few skills)
    print("\n[2] Testing wrapper imports (spot check)...")
    for skill in ["cdq-test-connection", "cdq-get-rules", "cdq-search-catalog"]:
        passed, msg = test_wrapper_import(skill)
        status = "PASS" if passed else "FAIL"
        results.append((f"import:{skill}", passed))
        if not passed:
            print(f"  {skill}: {status} - {msg}")
            all_passed = False
        else:
            print(f"  {skill}: {status}")

    # Test 3: Main client commands
    print("\n[3] Testing main client commands...")

    # test-connection
    passed, msg = test_test_connection()
    status = "PASS" if passed else "FAIL"
    results.append(("cmd:test-connection", passed))
    print(f"  test-connection: {status} - {msg}")
    if not passed:
        all_passed = False

    # search-catalog
    passed, msg = test_search_catalog()
    status = "PASS" if passed else "FAIL"
    results.append(("cmd:search-catalog", passed))
    print(f"  search-catalog: {status} - {msg}")
    if not passed:
        all_passed = False

    # get-rules
    passed, msg = test_get_rules()
    status = "PASS" if passed else "FAIL"
    results.append(("cmd:get-rules", passed))
    print(f"  get-rules: {status} - {msg}")
    if not passed:
        all_passed = False

    # run-sql
    passed, msg = test_run_sql()
    status = "PASS" if passed else "FAIL"
    results.append(("cmd:run-sql", passed))
    print(f"  run-sql: {status} - {msg}")
    if not passed:
        all_passed = False

    # get-jobs
    passed, msg = test_get_jobs()
    status = "PASS" if passed else "FAIL"
    results.append(("cmd:get-jobs", passed))
    print(f"  get-jobs: {status} - {msg}")
    if not passed:
        all_passed = False

    # get-recent-runs
    passed, msg = test_get_recent_runs()
    status = "PASS" if passed else "FAIL"
    results.append(("cmd:get-recent-runs", passed))
    print(f"  get-recent-runs: {status} - {msg}")
    if not passed:
        all_passed = False

    # list-tables prefix search (LIKE d%)
    passed, msg = test_list_tables_prefix_search()
    status = "PASS" if passed else "FAIL"
    results.append(("cmd:list-tables-prefix", passed))
    print(f"  list-tables prefix: {status} - {msg}")
    if not passed:
        all_passed = False

    # Summary
    print("\n" + "=" * 60)
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    print(f"Results: {passed_count}/{total_count} tests passed")

    if all_passed:
        print("ALL TESTS PASSED")
        return 0
    else:
        print("SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())