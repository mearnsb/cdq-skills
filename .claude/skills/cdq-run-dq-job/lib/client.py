#!/usr/bin/env python3
"""CDQ List Tables - Thin wrapper to project-level client"""
import os
import sys
from pathlib import Path


def find_project_root():
    """Find project root by looking for .env and lib/client.py"""
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


project_root = find_project_root()
if project_root:
    # Change to project root so imports work correctly
    os.chdir(project_root)
    # Add lib to path for the auth module import
    sys.path.insert(0, str(project_root / "lib"))
    try:
        from client import main
        sys.argv[0] = "lib/client.py"
        main()
    except ImportError as e:
        print(f"Error: Cannot import client from {project_root}: {e}", file=sys.stderr)
        sys.exit(1)
else:
    print("Error: Cannot find cdq-skills project root with .env and lib/client.py", file=sys.stderr)
    print("Ensure you're running from the project directory or a subdirectory.", file=sys.stderr)
    sys.exit(1)
