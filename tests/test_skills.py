#!/usr/bin/env python3
"""Fast, lightweight tests for CDQ skills.

Tests wrapper functionality and each command skill.
Run: pytest

All tests should complete in < 30 seconds total.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
import pytest

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
        # success is True if returncode is 0, False otherwise
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

# Parameterized for all skills to check structure
@pytest.mark.parametrize("skill_name", COMMAND_SKILLS + WORKFLOW_SKILLS)
def test_wrapper_structure(skill_name):
    """Test that a skill has proper wrapper structure."""
    skill_path = SKILLS_DIR / skill_name
    lib_path = skill_path / "lib" / "client.py"
    skill_md = skill_path / "SKILL.md"

    issues = []

    # Check SKILL.md exists
    if not skill_md.exists():
        issues.append(f"Missing SKILL.md")

    # Check lib/client.py exists for command skills
    if skill_name in COMMAND_SKILLS: # Only check for command skills
        if not lib_path.exists():
            issues.append(f"Missing lib/client.py")
        else:
            # Check wrapper contains key patterns (new shared wrapper pattern)
            content = lib_path.read_text()
            if "skill_wrapper" not in content:
                issues.append("Wrapper missing skill_wrapper import")
            if "run_skill" not in content:
                issues.append("Wrapper missing run_skill call")

    assert len(issues) == 0, f"Issues found for {skill_name}: {issues}"


# Parameterized for COMMAND_SKILLS only, as they are expected to have lib/client.py
def test_wrapper_import(skill_name):
    """Test that a skill wrapper can import and run the main client."""
    skill_path = SKILLS_DIR / skill_name
    lib_path = skill_path / "lib" / "client.py"

    assert lib_path.exists(), f"lib/client.py missing for {skill_name}"

    # Extract subcommand name (e.g., "get-alerts" from "cdq-get-alerts")
    subcommand_name = skill_name.replace("cdq-", "")

    # Define placeholder arguments for skills that require them for --help
    # Using triple-quoted strings for outer Python string literals to correctly embed SQL.
    placeholder_args = {
        "cdq-get-alerts": "--dataset dummy_dataset",
        "cdq-get-dataset": "--dataset dummy_dataset",
        "cdq-get-results": "--dataset dummy_dataset --run-id dummy_run_id",
        "cdq-get-rules": "--dataset dummy_dataset",
        # Using single quotes for the SQL string literal, properly escaped within Python triple quotes.
        "cdq-run-dq-job": "--dataset dummy_dataset --sql 'SELECT 1'",
        "cdq-run-sql": "--sql 'SELECT 1'",
        "cdq-save-alert": "--dataset dummy_dataset --name dummy_name --condition 'True' --email dummy@example.com",
        "cdq-save-rule": "--dataset dummy_dataset --name dummy_name --sql 'SELECT 1'",
        "cdq-search-catalog": "--query dummy_query",
    }

    # Construct the command: always include --help, and add placeholders if available.
    cmd_parts = [f"python {lib_path}", subcommand_name, "--help"]
    if skill_name in placeholder_args:
        cmd_parts.append(placeholder_args[skill_name])
    
    cmd = " ".join(cmd_parts)

    success, output, error = run_command(cmd, timeout=5)

    # Check if the output contains help indicators.
    produced_help_output = (
        subcommand_name in output or
        "usage:" in output or
        "help" in output
    )

    # The test should pass if the command *either* ran successfully *or* produced help output.
    # This assertion checks the overall validity of the execution (success or help output).
    assert success or produced_help_output, 
        f"Command execution failed for {skill_name} with command '{cmd}' and did not produce help output. Error: {error}. Output: {output}"

    # Additionally, we must ensure that it *did* produce help output, because a successful run
    # without help output might not be testing the intended scenario (i.e., what happens when arguments are missing).
    assert produced_help_output, 
        f"Wrapper did not produce expected help output for {skill_name}. Output: {output}"


def test_test_connection():
    """Test cdq-test-connection command."""
    cmd = f"python lib/client.py test-connection"
    success, output, error = run_command(cmd, timeout=10)

    assert success, f"Command failed: {error}"

    try:
        result = json.loads(output)
        assert result.get("success"), "Connection test failed"
    except json.JSONDecodeError:
        pytest.fail("Invalid JSON output")


def test_search_catalog():
    """Test cdq-search-catalog command (fast query)."""
    cmd = f'python lib/client.py search-catalog --query "samples" --limit 3'
    success, output, error = run_command(cmd, timeout=15)

    assert success, f"Command failed: {error}"

    try:
        result = json.loads(output)
        data = result.get("dataAssetList", [])
        assert len(data) > 0, "No results found"
    except json.JSONDecodeError:
        pytest.fail("Invalid JSON output")


def test_get_rules():
    """Test cdq-get-rules command."""
    cmd = 'python lib/client.py get-rules --dataset "samples_sales_data" --limit 5'
    success, output, error = run_command(cmd, timeout=15)

    assert success, f"Command failed: {error}"

    try:
        result = json.loads(output)
        assert isinstance(result, list) or isinstance(result, dict), "Unexpected output format"
    except json.JSONDecodeError:
        pytest.fail("Invalid JSON output")


def test_run_sql():
    """Test cdq-run-sql command (simple query)."""
    cmd = 'python lib/client.py run-sql --sql "SELECT 1 as test" --connection BIGQUERY'
    success, output, error = run_command(cmd, timeout=15)

    assert success, f"Command failed: {error}"

    try:
        result = json.loads(output)
        assert result.get("rows"), "No rows in result"
    except json.JSONDecodeError:
        pytest.fail("Invalid JSON output")


def test_get_jobs():
    """Test cdq-get-jobs command."""
    cmd = 'python lib/client.py get-jobs --limit 3'
    success, output, error = run_command(cmd, timeout=15)

    assert success, f"Command failed: {error}"

    try:
        json.loads(output) # Ensure it's valid JSON
    except json.JSONDecodeError:
        pytest.fail("Invalid JSON output")


def test_get_recent_runs():
    """Test cdq-get-recent-runs command."""
    cmd = 'python lib/client.py get-recent-runs'
    success, output, error = run_command(cmd, timeout=15)

    assert success, f"Command failed: {error}"

    try:
        json.loads(output) # Ensure it's valid JSON
    except json.JSONDecodeError:
        pytest.fail("Invalid JSON output")


def test_list_tables_prefix_search():
    """Test cdq-list-tables with LIKE prefix search (d%)."""
    cmd = 'python lib/client.py list-tables --schema samples --search "d%" --limit 50'
    success, output, error = run_command(cmd, timeout=15)

    assert success, f"Command failed: {error}"

    try:
        result = json.loads(output)
        tables = result.get("tables", [])
        count = len(tables)
        # Should return tables starting with 'd' - expect at least 10
        assert count >= 10, f"Expected >=10 tables starting with 'd', got {count}"
    except json.JSONDecodeError:
        pytest.fail("Invalid JSON output")
