#!/usr/bin/env python3
"""Shared skill wrapper for CDQ skills.

This module provides a common wrapper that all CDQ skills can use
to redirect to the project-level lib/client.py.

Usage in skill's lib/client.py:
    from skill_wrapper import run_skill
    run_skill('command-name')
"""

import os
import sys
from pathlib import Path


def find_project_root():
    """Find project root by looking for .env and lib/client.py."""
    start = Path.cwd()
    # Search from current directory upward
    for path in [start] + list(start.parents):
        if (path / ".env").exists() and (path / "lib" / "client.py").exists():
            return path
    # Fallback: common locations
    for path in [Path.home() / "github" / "cdq-skills", Path.home() / "cdq-skills"]:
        if (path / ".env").exists() and (path / "lib" / "client.py").exists():
            return path
    return None


def run_skill(command_name=None):
    """Run the project-level client.py with optional command.

    Args:
        command_name: Optional command to run (e.g., 'test-connection').
                     If None, passes through sys.argv.
    """
    project_root = find_project_root()

    if not project_root:
        print("Error: Cannot find cdq-skills project root with .env and lib/client.py", file=sys.stderr)
        print("Ensure you're running from the project directory or a subdirectory.", file=sys.stderr)
        sys.exit(1)

    # Change to project root so imports work correctly
    os.chdir(project_root)

    # Add lib to path for the auth module import
    sys.path.insert(0, str(project_root / "lib"))

    try:
        from client import main

        # Override argv if command specified
        if command_name:
            sys.argv = [str(project_root / "lib" / "client.py"), command_name] + sys.argv[1:]
        else:
            sys.argv[0] = str(project_root / "lib" / "client.py")

        main()
    except ImportError as e:
        print(f"Error: Cannot import client from {project_root}: {e}", file=sys.stderr)
        sys.exit(1)


# Default behavior when run directly
if __name__ == "__main__":
    run_skill()