#!/usr/bin/env python3
"""Render pi example HTML cards via shared _lib/render.py."""
import subprocess
import sys
from pathlib import Path

# examples/pi/scripts/render.py → templates/_lib/render.py (5 levels up)
LIB = Path(__file__).resolve().parent.parent.parent.parent.parent / "_lib" / "render.py"
PROJ = Path(__file__).resolve().parent.parent
sys.exit(subprocess.call(
    [sys.executable, str(LIB), "--base-dir", str(PROJ), "--html-dir", "html", "--out-dir", "images"] + sys.argv[1:]
))