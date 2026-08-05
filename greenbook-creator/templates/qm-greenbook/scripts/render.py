#!/usr/bin/env python3
"""Render qm-greenbook HTML cards via shared _lib/render.py."""
import subprocess, sys
from pathlib import Path
LIB  = Path(__file__).resolve().parent.parent.parent / "_lib" / "render.py"
PROJ = Path(__file__).resolve().parent.parent
sys.exit(subprocess.call(
    [sys.executable, str(LIB), "--base-dir", str(PROJ)] + sys.argv[1:]
))