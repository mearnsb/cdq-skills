#!/usr/bin/env python3
"""CDQ Workflow: Explore Dataset - Thin wrapper using shared skill_wrapper module.

This workflow skill uses: search-catalog, run-sql
"""
import sys
from pathlib import Path

# Add .claude/skills/lib to path so we can import skill_wrapper
skill_lib = Path(__file__).parent.parent.parent / "lib"
sys.path.insert(0, str(skill_lib))

from skill_wrapper import run_skill

run_skill()