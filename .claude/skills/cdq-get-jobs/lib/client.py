#!/usr/bin/env python3
"""CDQ Get Jobs - Thin wrapper using shared skill_wrapper module."""
import sys
from pathlib import Path

# Add .claude/skills/lib to path so we can import skill_wrapper
skill_lib = Path(__file__).parent.parent.parent / "lib"
sys.path.insert(0, str(skill_lib))

from skill_wrapper import run_skill

# Command is hardcoded - ignore any extra args to avoid argparse errors
run_skill("get-jobs")