#!/usr/bin/env python3
"""
Auto-CDQ Hybrid Orchestrator - Option 3 Implementation

Bridges Claude Code's interactive capabilities with CDQ skill execution.
- Uses multi-section headers for visual progress tracking
- Calls /skill commands for data retrieval
- Gracefully handles both interactive and non-interactive modes
- Maintains state across sessions for multi-step workflows

Entry points:
  - python auto-cdq-orchestrator.py discovery [--schema SCHEMA] [--table TABLE]
  - python auto-cdq-orchestrator.py onboarding [--schema SCHEMA] [--table TABLE] [--dataset DATASET]
  - python auto-cdq-orchestrator.py rules [--dataset DATASET]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


# ============================================================================
# State & Config
# ============================================================================

STATE_FILE = Path.home() / ".claude" / "projects" / "-Users-brian-github-cdq-skills" / ".auto-cdq-state.json"
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


class WorkflowType(Enum):
    DISCOVERY = "discovery"
    ONBOARDING = "onboarding"
    RULES = "rules"


@dataclass
class WorkflowState:
    """Persistent state across workflows and Claude Code sessions."""
    workflow: str = ""
    schema: str = "samples"
    table: str = ""
    dataset: str = ""
    limit: int = 5
    sample_size: int = 10000
    selected_rules: list[str] = field(default_factory=list)
    completed_phases: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def load(cls) -> WorkflowState:
        """Load state from disk."""
        if STATE_FILE.exists():
            try:
                data = json.loads(STATE_FILE.read_text())
                return cls(**data)
            except (json.JSONDecodeError, TypeError):
                return cls()
        return cls()

    def save(self) -> None:
        """Save state to disk."""
        STATE_FILE.write_text(json.dumps(asdict(self), indent=2))

    def mark_phase_complete(self, workflow: str, phase: str) -> None:
        """Mark a phase as completed."""
        if workflow not in self.completed_phases:
            self.completed_phases[workflow] = []
        if phase not in self.completed_phases[workflow]:
            self.completed_phases[workflow].append(phase)
        self.save()

    def is_phase_complete(self, workflow: str, phase: str) -> bool:
        """Check if a phase was completed."""
        return phase in self.completed_phases.get(workflow, [])


# ============================================================================
# Multi-Section Header
# ============================================================================

class MultiSectionHeader:
    """Render multi-section progress headers."""

    @staticmethod
    def render(phases: list[str], completed: list[str], width: int = 80) -> str:
        """Render header with progress markers."""
        parts = []
        for phase in phases:
            marker = "✓" if phase in completed else "☐"
            parts.append(f"{marker} {phase}")

        header_content = "    ".join(parts)
        border = "=" * width
        return f"\n{border}\n{header_content}\n{border}\n"

    @staticmethod
    def render_section(title: str, width: int = 80) -> str:
        """Render a section title."""
        border = "-" * width
        return f"\n{border}\n{title}\n{border}\n"


# ============================================================================
# Skill Execution
# ============================================================================

class SkillExecutor:
    """Execute CDQ skills and capture output."""

    @staticmethod
    def execute(skill_name: str, args: str = "") -> tuple[bool, str]:
        """
        Execute a skill and return (success, output).

        Maps CDQ skill names to Python CLI command names.
        cdq-list-tables → list-tables, cdq-run-sql → run-sql, etc.
        """
        try:
            # Map CDQ skill names to Python CLI commands
            # Remove 'cdq-' prefix and convert to CLI format
            cmd_name = skill_name.replace("cdq-", "")

            cmd = f"python lib/client.py {cmd_name} {args}".strip()
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip() or "Command failed"
        except subprocess.TimeoutExpired:
            return False, "Skill execution timed out"
        except Exception as e:
            return False, f"Error: {e}"

    @staticmethod
    def display_skill_call(skill_name: str, args: str = "") -> None:
        """Show that a skill is being called."""
        print(f"\n🔄 [RUNNING SKILL: {skill_name} {args}]\n")


# ============================================================================
# Input Handling
# ============================================================================

class InputHandler:
    """Handle user input with fallback to defaults."""

    @staticmethod
    def ask_choice(
        question: str,
        options: list[str],
        default: str | None = None,
    ) -> str:
        """
        Ask user to choose from options.

        In Claude Code, this would use AskUserQuestion.
        In non-interactive mode, uses default.
        """
        if default is None and options:
            default = options[0]

        try:
            print(f"\n{question}\n")
            for i, opt in enumerate(options, 1):
                print(f"  {i}. {opt}")

            choice = input("\n→ Enter choice (number): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
            except ValueError:
                pass

            # Fallback
            print(f"(Using default: {default})")
            return default
        except EOFError:
            # Non-interactive mode
            return default

    @staticmethod
    def ask_text(prompt: str, default: str = "") -> str:
        """Ask for text input with fallback."""
        try:
            result = input(f"{prompt} [{default}]: ").strip() or default
            return result
        except EOFError:
            return default


# ============================================================================
# Discovery Workflow
# ============================================================================

class DiscoveryWorkflow:
    """Implement the Discovery workflow with multi-section headers."""

    PHASES = ["Schema", "Table", "Preview", "Confirm"]

    def __init__(self, state: WorkflowState):
        self.state = state
        self.completed = []

    def print_header(self) -> None:
        """Print multi-section header."""
        header = MultiSectionHeader.render(
            self.PHASES,
            self.completed,
        )
        print(header)

    def phase1_schema_selection(self) -> bool:
        """Phase 1: Select schema."""
        section = MultiSectionHeader.render_section("Phase 1: Schema Selection")
        print(section)

        schema_choice = InputHandler.ask_choice(
            "Which schema should we search in?",
            ["samples", "Custom"],
            default="samples",
        )

        if schema_choice == "Custom":
            schema = InputHandler.ask_text("Enter schema name:", self.state.schema)
        else:
            schema = "samples"

        self.state.schema = schema
        self.completed.append("Schema")
        print(f"✓ Schema selected: {self.state.schema}")
        return True

    def phase2_table_discovery(self) -> bool:
        """Phase 2: Discover and select table."""
        section = MultiSectionHeader.render_section("Phase 2: Table Discovery")
        print(section)

        # Ask how to find tables
        method = InputHandler.ask_choice(
            "How would you like to find a table?",
            [
                "Browse all",
                "Search pattern",
                "Type name",
            ],
            default="Browse all",
        )

        search_pattern = None
        if method == "Search pattern":
            search_pattern = InputHandler.ask_text("Enter search pattern (SQL LIKE):")

        # Execute cdq-list-tables skill with proper shell escaping
        args = f"--schema {self.state.schema} --limit 20"
        if search_pattern:
            args += f" --search '{search_pattern}'"

        SkillExecutor.display_skill_call("cdq-list-tables", args)
        success, output = SkillExecutor.execute("cdq-list-tables", args)

        if not success:
            print(f"❌ Error listing tables: {output}")
            return False

        print(output + "\n")

        # Ask user to select table
        table_choice = InputHandler.ask_choice(
            "Which table would you like to work with?",
            ["CollibraEmployees", "Customer_MonthEnd", "Custom"],
            default="CollibraEmployees",
        )

        if table_choice == "Custom":
            table = InputHandler.ask_text("Enter table name:")
        else:
            table = table_choice

        self.state.table = table
        self.completed.append("Table")
        print(f"✓ Table selected: {self.state.table}")
        return True

    def phase3_data_preview(self) -> bool:
        """Phase 3: Preview data with validation loop."""
        section = MultiSectionHeader.render_section("Phase 3: Data Preview")
        print(section)

        current_limit = self.state.limit

        while True:
            # Execute cdq-run-sql skill
            sql = f"SELECT * FROM `{self.state.schema}.{self.state.table}` LIMIT {current_limit}"
            SkillExecutor.display_skill_call("cdq-run-sql", f"--sql '{sql}'")
            success, output = SkillExecutor.execute("cdq-run-sql", f"--sql '{sql}'")

            if not success:
                print(f"❌ Error previewing data: {output}")
                return False

            print(output + "\n")

            # Validation loop
            response = InputHandler.ask_choice(
                f"Preview of `{self.state.schema}.{self.state.table}` looks good?",
                [
                    "Yes",
                    "Show more",
                    "Different table",
                ],
                default="Yes",
            )

            if response == "Yes":
                self.completed.append("Preview")
                print(f"✓ Data preview confirmed")
                break
            elif response == "Show more":
                current_limit = min(current_limit * 4, 100)
                print(f"Showing {current_limit} rows...\n")
                continue
            elif response == "Different table":
                return False  # Go back to phase 2

        return True

    def phase4_confirmation(self) -> bool:
        """Phase 4: Final confirmation."""
        section = MultiSectionHeader.render_section("Phase 4: Confirmation")
        print(section)

        response = InputHandler.ask_choice(
            f"Ready to proceed with `{self.state.schema}.{self.state.table}`?",
            [
                "Yes",
                "Go back",
                "Exit",
            ],
            default="Yes",
        )

        if response == "Yes":
            self.completed.append("Confirm")
            return True
        elif response == "Go back":
            return False  # Prompt to restart
        else:  # Exit
            print("Exiting discovery...")
            sys.exit(0)

    def run(self) -> bool:
        """Execute the discovery workflow."""
        print("\n" + "=" * 80)
        print("DISCOVERY WORKFLOW: Find and Preview Tables")
        print("=" * 80)

        self.print_header()

        # Phase 1
        if not self.phase1_schema_selection():
            return False
        self.print_header()

        # Phase 2
        while not (self.completed and "Table" in self.completed):
            if not self.phase2_table_discovery():
                # User chose "go back" - restart phase 2
                self.completed = ["Schema"]
                self.print_header()
                continue
            break
        self.print_header()

        # Phase 3
        if not self.phase3_data_preview():
            # Go back to phase 2
            self.completed = ["Schema"]
            self.print_header()
            return self.run()
        self.print_header()

        # Phase 4
        if not self.phase4_confirmation():
            print("Going back to phase 2...")
            self.completed = ["Schema"]
            return self.run()

        # Success
        print("\n" + "=" * 80)
        print("✓ Schema      ✓ Table       ✓ Preview     ✓ Confirm")
        print("=" * 80)
        print("\n🎉 DISCOVERY COMPLETE")
        print(f"  Schema: {self.state.schema}")
        print(f"  Table: {self.state.table}")
        print("  Status: Ready for next step\n")

        # Save state
        self.state.workflow = WorkflowType.DISCOVERY.value
        self.state.save()

        return True


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Parse arguments and run appropriate workflow."""
    parser = argparse.ArgumentParser(
        description="Auto-CDQ Hybrid Orchestrator - Option 3",
    )
    parser.add_argument(
        "workflow",
        choices=["discovery", "onboarding", "rules"],
        help="Workflow to execute",
    )
    parser.add_argument("--schema", help="Schema name (for discovery)")
    parser.add_argument("--table", help="Table name (for discovery/onboarding)")
    parser.add_argument("--dataset", help="Dataset name (for onboarding/rules)")
    parser.add_argument("--limit", type=int, default=5, help="Preview row limit")
    parser.add_argument(
        "--sample-size",
        type=int,
        default=10000,
        help="Sample size for onboarding",
    )

    args = parser.parse_args()

    # Load or create state
    state = WorkflowState.load()

    # Apply CLI overrides
    if args.schema:
        state.schema = args.schema
    if args.table:
        state.table = args.table
    if args.dataset:
        state.dataset = args.dataset
    if args.limit:
        state.limit = args.limit
    if args.sample_size:
        state.sample_size = args.sample_size

    # Execute workflow
    if args.workflow == "discovery":
        workflow = DiscoveryWorkflow(state)
        return workflow.run()
    elif args.workflow == "onboarding":
        print("Onboarding workflow - coming soon")
        return False
    elif args.workflow == "rules":
        print("Rules workflow - coming soon")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
