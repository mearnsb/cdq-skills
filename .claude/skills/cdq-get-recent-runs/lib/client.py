#!/usr/bin/env python3
"""Thin wrapper that imports and runs cdq_skills client."""
import sys
from cdq_skills.client import main

if __name__ == "__main__":
    sys.exit(main())
