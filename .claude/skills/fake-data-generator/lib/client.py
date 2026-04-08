#!/usr/bin/env python3
"""Fake Data Generator CLI wrapper for CDQ Skills."""
import sys
from pathlib import Path

skill_root = Path(__file__).parent.parent
skill_lib = skill_root.parent / "lib"
sys.path.insert(0, str(skill_lib))

from skill_wrapper import run_skill

run_skill("fake-data-generator")
