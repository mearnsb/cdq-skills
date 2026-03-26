#!/usr/bin/env python3
"""CDQ List Tables - Thin wrapper using shared skill_wrapper module.

This is a thin wrapper that redirects to the project-level lib/client.py.
For direct usage, run: python lib/client.py list-tables

The actual implementation is in:
    /lib/client.py
"""
import sys
from pathlib import Path

# Add .claude/skills/lib to path so we can import skill_wrapper
skill_lib = Path(__file__).parent.parent.parent / "lib"
sys.path.insert(0, str(skill_lib))

from skill_wrapper import run_skill

run_skill("list-tables")