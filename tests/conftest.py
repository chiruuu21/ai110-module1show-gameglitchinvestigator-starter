"""Pytest configuration for the test suite.

logic_utils.py lives in the project root, one level above this folder.
Pytest only puts the test file's own directory on sys.path, so without
this the tests fail with "ModuleNotFoundError: No module named 'logic_utils'".

Adding the project root here means `pytest` works no matter which
directory you run it from.
"""

# FIX: created with agent mode to resolve "ModuleNotFoundError: No module named
# 'logic_utils'". Note that `pytest` and `python -m pytest` differ: only the
# latter puts the current directory on sys.path.
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
