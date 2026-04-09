#!/usr/bin/env python3
"""
Auto-CDQ Wizard Orchestrator

Manages multi-section header batching and workflow orchestration for Collibra DQ.
Calls existing CDQ skills via Skill tool. Tracks state in .auto-cdq-state.json.

Entry point: /auto-cdq [discovery|onboarding|rules]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# State file location
STATE_FILE = Path.home() / ".claude" / "projects" / "-Users-brian-github-cdq-skills" / ".auto-cdq-state.json"
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_state() -> dict[str, Any]:
    """Load state from .auto-cdq-state.json"""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_state(state: dict[str, Any]) -> None:
    """Save state to .auto-cdq-state.json"""
    STATE_FILE.write_text(json.dumps(state, indent=2))


def prompt_workflow_selection() -> str:
    """
    Phase 1: Present workflow selection menu.

    Output:
    ☐ Workflow

    Returns: "discovery" | "onboarding" | "rules" | "exit"
    """
    print("\n" + "="*70)
    print("AUTO-CDQ WIZARD: Workflow Selection")
    print("="*70)

    options_text = """
    1) Discovery (Recommended)     — Find and preview tables with guided search
    2) Onboarding                   — Register a dataset and run a DQ job
    3) Rules                        — Analyze data and create quality rules
    4) Exit                         — Finish the session

    Choose an option (1-4):
    """
    print(options_text)

    # Try to read from stdin, but default to discovery if not available (non-interactive)
    try:
        choice = input("→ ").strip()
    except EOFError:
        print("(Non-interactive mode: defaulting to Discovery)")
        return "discovery"

    mapping = {
        "1": "discovery",
        "2": "onboarding",
        "3": "rules",
        "4": "exit",
    }

    return mapping.get(choice, "discovery")


def safe_input(prompt: str, default: str = "") -> str:
    """Safe input wrapper that handles EOF in non-interactive mode."""
    try:
        return input(prompt).strip() or default
    except EOFError:
        return default


def discovery_workflow(schema: str | None = None, table: str | None = None, search_term: str | None = None, limit: int | None = None) -> None:
    """
    Discovery Workflow: Find and preview tables.

    Can accept optional CLI arguments for non-interactive mode:
    - schema: schema name (default: 'samples')
    - table: table name to preview
    - search_term: search pattern for tables
    - limit: number of rows to preview (default: 5)

    Flow:
    1. Ask for schema (or use provided)
    2. List tables (calls /cdq-list-tables)
    3. Choose table (or use provided)
    4. Preview data (calls /cdq-run-sql)
    5. Confirm or search again
    """
    print("\n" + "="*70)
    print("DISCOVERY WORKFLOW: Find and Preview Tables")
    print("="*70)

    state = load_state()
    state["workflow"] = "discovery"
    save_state(state)

    # Phase 1: Schema Selection
    print("\n[Phase 1/2] Schema Selection")
    print("-" * 70)

    if schema is None:
        schema = safe_input("Enter schema name (or press Enter for 'samples'): ", "samples")
    print(f"✓ Schema selected: {schema}")

    state["discovery_schema"] = schema
    save_state(state)

    # Phase 2: Table Search & Selection
    print("\n[Phase 2/2] Table Discovery & Selection")
    print("-" * 70)

    if search_term is None:
        search_term = safe_input("Search for tables (optional, or press Enter to skip): ", None) or None

    if search_term:
        print(f"✓ Searching for tables matching: {search_term}")
    else:
        print("✓ Listing all tables")

    state["discovery_search"] = search_term
    save_state(state)

    # Call /cdq-list-tables
    print("\nCalling /cdq-list-tables to fetch available tables...")
    print(f"  Schema: {schema}")
    if search_term:
        print(f"  Search: {search_term}")
    print("\n[Table list would be displayed here from skill output]\n")

    # Table choice - in non-interactive mode, list available tables and auto-select first one
    if table is None:
        table_input = safe_input("Enter table name to preview: ")
        if not table_input:
            # In non-interactive mode, auto-select first available table (e.g., from samples schema)
            print("(Non-interactive mode: auto-selecting first available table)")
            table = "CollibraEmployees"  # sensible default from samples schema
        else:
            table = table_input

    if not table:
        print("No table selected. Exiting discovery.")
        return

    print(f"✓ Table selected: {table}")
    state["discovery_table"] = table
    save_state(state)

    # Phase 3: Data Preview
    print("\n[Phase 3/3] Data Preview")
    print("-" * 70)

    if limit is None:
        limit_str = safe_input("Number of rows to preview (default: 5): ", "5")
        try:
            limit = int(limit_str)
            if limit <= 0:
                limit = 5
        except ValueError:
            limit = 5

    print(f"✓ Preview limit: {limit} rows")
    print(f"\nCalling /cdq-run-sql to preview data...")
    print(f"  Schema: {schema}")
    print(f"  Table: {table}")
    print(f"  Limit: {limit}")
    print("\n[Preview data would be displayed here from skill output]\n")

    state["discovery_limit"] = limit
    save_state(state)

    # Next steps
    print("\n[Phase 4/4] What's Next?")
    print("-" * 70)

    next_options = """
    1) Search for another table     — Continue discovery
    2) Proceed to Onboarding        — Register this dataset and run DQ
    3) Return to Workflow Menu      — Choose a different workflow
    4) Exit                         — Finish the session

    Choose an option (1-4):
    """
    print(next_options)

    try:
        next_choice = input("→ ").strip()
    except EOFError:
        print("(Non-interactive mode: defaulting to exit)")
        return

    if next_choice == "1":
        discovery_workflow()
    elif next_choice == "2":
        onboarding_workflow()
    elif next_choice == "3":
        main()
    else:
        return


def onboarding_workflow(schema: str | None = None, table: str | None = None, dataset_name: str | None = None, limit: int | None = None) -> None:
    """
    Onboarding Workflow: Register dataset and run DQ job.

    Can accept optional CLI arguments for non-interactive mode:
    - schema: schema name
    - table: table name
    - dataset_name: logical dataset name (default: {table}_dq)
    - limit: row limit (default: 10000)

    Flow:
    1. Ask for dataset name (or use provided)
    2. Choose data size limit (or use provided)
    3. Verify connection (calls /cdq-test-connection)
    4. Register dataset (calls /cdq-run-dq-job)
    5. Check results (calls /cdq-get-results)
    """
    print("\n" + "="*70)
    print("ONBOARDING WORKFLOW: Register Dataset and Run DQ Job")
    print("="*70)

    state = load_state()
    state["workflow"] = "onboarding"

    # Check if discovery data available
    if schema is None:
        schema = state.get("discovery_schema")
    if table is None:
        table = state.get("discovery_table")

    if schema and table:
        print(f"\n✓ Using data from Discovery:")
        print(f"  Schema: {schema}")
        print(f"  Table: {table}")
    else:
        print("\nNo discovery data available. Enter dataset details:")
        schema = safe_input("Schema: ", "samples")
        table = safe_input("Table: ")
        if not table:
            print("No table specified. Returning to workflow menu.")
            return

    # Phase 1: Dataset Configuration
    print("\n[Phase 1/2] Dataset Configuration")
    print("-" * 70)

    if dataset_name is None:
        dataset_name = safe_input("Dataset name (logical name, not schema.table): ")
    if not dataset_name:
        dataset_name = f"{table}_dq"

    print(f"✓ Dataset name: {dataset_name}")
    state["onboarding_dataset"] = dataset_name

    # Size limit
    if limit is None:
        print("\nData size limit for DQ job:")
        size_options = """
    1) Small        (LIMIT 1000 - quick validation)
    2) Medium       (LIMIT 10000 - balanced)
    3) Large        (LIMIT 50000 - comprehensive)
    4) Full Dataset (no limit - production)

    Choose an option (1-4):
    """
        print(size_options)

        try:
            size_choice = input("→ ").strip()
        except EOFError:
            size_choice = "2"

        size_mapping = {
            "1": 1000,
            "2": 10000,
            "3": 50000,
            "4": None,  # None = no limit
        }
        limit = size_mapping.get(size_choice, 10000)

    print(f"✓ Size limit: {limit if limit else 'No limit (full dataset)'}")
    state["onboarding_limit"] = limit

    # Connection test
    print("\n[Phase 2/2] Validation & Execution")
    print("-" * 70)

    print("\nTesting connection to CDQ API...")
    print("Calling /cdq-test-connection...")
    print("\n[Connection test would show result here from skill output]\n")

    # Run job
    try:
        proceed = input("Ready to register dataset and run DQ job? (y/n): ").strip().lower()
    except EOFError:
        proceed = "y"

    if proceed != "y":
        print("Skipping job execution. Returning to workflow menu.")
        return

    print(f"\nRegistering dataset and running DQ job...")
    print(f"Calling /cdq-run-dq-job...")
    print(f"  Dataset: {dataset_name}")
    print(f"  Schema: {schema}")
    print(f"  Table: {table}")
    if limit:
        print(f"  Limit: {limit}")
    print("\n[Job execution status would be shown here from skill output]\n")

    state["onboarding_executed"] = True
    save_state(state)

    # Results check
    print("\n[Phase 3/3] Check Results")
    print("-" * 70)

    try:
        check_results = input("Check job results? (y/n): ").strip().lower()
    except EOFError:
        check_results = "n"

    if check_results == "y":
        print(f"\nCalling /cdq-get-results for dataset: {dataset_name}")
        print("\n[Job results would be displayed here from skill output]\n")

    # Next steps
    next_options = """
    1) Create DQ Rules              — Set up quality checks
    2) Return to Workflow Menu      — Choose a different workflow
    3) Exit                         — Finish the session

    Choose an option (1-3):
    """
    print(next_options)

    try:
        next_choice = input("→ ").strip()
    except EOFError:
        next_choice = "2"

    if next_choice == "1":
        rules_workflow()
    elif next_choice == "2":
        main()
    else:
        print("\nSession ended. Goodbye!")
        sys.exit(0)


def rules_workflow(dataset_name: str | None = None) -> None:
    """
    Rules Workflow: Analyze data and create quality rules.

    Can accept optional CLI argument for non-interactive mode:
    - dataset_name: dataset to create rules for

    Phase 1 (Batched): ☐ Analysis | ☐ Suggestions | ☐ Review
    Phase 2 (Batched): ☐ Testing | ☐ Refinement | ☐ Save

    Flow:
    1. Get dataset info (calls /cdq-get-dataset)
    2. Suggest rules (calls /cdq-workflow-suggest-rules)
    3. Review suggestions
    4. Test rule SQL (calls /cdq-run-sql)
    5. Save rules (calls /cdq-save-rule)
    """
    print("\n" + "="*70)
    print("RULES WORKFLOW: Analyze Data and Create Quality Rules")
    print("="*70)

    state = load_state()
    state["workflow"] = "rules"

    if dataset_name is None:
        dataset_name = state.get("onboarding_dataset") or safe_input("Dataset name: ")
    if not dataset_name:
        print("No dataset specified. Returning to workflow menu.")
        return

    print(f"\n✓ Working with dataset: {dataset_name}")

    # Phase 1: Data Analysis
    print("\n[Phase 1/3] Data Analysis & Rule Suggestions")
    print("-" * 70)

    schema = state.get("discovery_schema", "samples")
    table = state.get("discovery_table")

    if table:
        print(f"\nAnalyzing dataset for rule opportunities...")
        print(f"Calling /cdq-workflow-suggest-rules...")
        print(f"  Dataset: {dataset_name}")
        print(f"  Schema: {schema}")
        print(f"  Table: {table}")
        print("\n[Suggested rules would be displayed here from skill output]\n")

    # Phase 2: Rule Selection & Testing
    print("\n[Phase 2/3] Rule Testing & Refinement")
    print("-" * 70)

    rule_options = """
    1) Use suggested rules          — Apply analyzed recommendations
    2) Create custom rule           — Write custom SQL
    3) Skip rules                   — Don't create rules now

    Choose an option (1-3):
    """
    print(rule_options)

    try:
        rule_choice = input("→ ").strip()
    except EOFError:
        rule_choice = "3"

    if rule_choice == "1":
        print("\nUsing suggested rules...")
        print("Testing rules against data...")
        print("Calling /cdq-run-sql to validate rule queries...")
        print("\n[Rule validation results would be shown here]\n")

        # Save rules
        print("\n[Phase 3/3] Save Rules")
        print("-" * 70)

        try:
            save_choice = input("Save these rules? (y/n): ").strip().lower()
        except EOFError:
            save_choice = "n"

        if save_choice == "y":
            print(f"Saving rules to dataset: {dataset_name}")
            print("Calling /cdq-save-rule for each validated rule...")
            print("\n[Rule save status would be shown here]\n")
            state["rules_saved"] = True

    elif rule_choice == "2":
        print("\nEnter custom rule SQL:")
        try:
            rule_sql = input("SQL: ").strip()
        except EOFError:
            rule_sql = ""

        if rule_sql:
            print("\nTesting custom rule...")
            print("Calling /cdq-run-sql to validate...")
            print("\n[Test results would be shown here]\n")

            try:
                save_choice = input("Save this rule? (y/n): ").strip().lower()
            except EOFError:
                save_choice = "n"

            if save_choice == "y":
                try:
                    rule_name = input("Rule name: ").strip() or "custom_rule"
                except EOFError:
                    rule_name = "custom_rule"

                print(f"\nSaving rule: {rule_name}")
                print("Calling /cdq-save-rule...")
                print("\n[Rule save status would be shown here]\n")
                state["rules_saved"] = True

    save_state(state)

    # Next steps
    next_options = """
    1) Create another rule          — Add more rules
    2) Return to Workflow Menu      — Choose a different workflow
    3) Exit                         — Finish the session

    Choose an option (1-3):
    """
    print(next_options)

    try:
        next_choice = input("→ ").strip()
    except EOFError:
        next_choice = "2"

    if next_choice == "1":
        rules_workflow()
    elif next_choice == "2":
        main()
    else:
        print("\nSession ended. Goodbye!")
        sys.exit(0)


def main() -> None:
    """Entry point: parse args and route to workflows."""
    parser = argparse.ArgumentParser(
        description="Auto-CDQ Wizard — Interactive CDQ workflow orchestrator"
    )
    parser.add_argument(
        "workflow",
        nargs="?",
        choices=["discovery", "onboarding", "rules"],
        help="Skip workflow selection and go directly to specified workflow",
    )

    # Discovery workflow arguments
    parser.add_argument("--schema", help="Schema name (discovery/onboarding)")
    parser.add_argument("--table", help="Table name (discovery/onboarding)")
    parser.add_argument("--search", help="Search term for tables (discovery)")
    parser.add_argument("--limit", type=int, help="Row limit for preview (discovery)")

    # Onboarding workflow arguments
    parser.add_argument("--dataset", help="Dataset name (onboarding/rules)")
    parser.add_argument("--size", type=int, help="Row limit for DQ job (onboarding)")

    # Rules workflow arguments
    parser.add_argument("--rule-type", choices=["suggested", "custom"], help="Rule type (rules)")

    args = parser.parse_args()

    if args.workflow == "discovery":
        discovery_workflow(schema=args.schema, table=args.table, search_term=args.search, limit=args.limit)
    elif args.workflow == "onboarding":
        onboarding_workflow(schema=args.schema, table=args.table, dataset_name=args.dataset, limit=args.size)
    elif args.workflow == "rules":
        rules_workflow(dataset_name=args.dataset)
    else:
        # Show workflow menu
        choice = prompt_workflow_selection()

        if choice == "discovery":
            discovery_workflow()
        elif choice == "onboarding":
            onboarding_workflow()
        elif choice == "rules":
            rules_workflow()
        else:
            print("\nSession ended. Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()
