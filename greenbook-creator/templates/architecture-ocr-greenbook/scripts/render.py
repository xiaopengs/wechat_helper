#!/usr/bin/env python3
"""Render architecture-ocr-greenbook HTML cards via shared _lib/render.py.

Usage:
  python3 scripts/render.py            # use defaults (base-dir = .)
  python3 scripts/render.py --html-dir html --out-dir images
"""
import subprocess
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent.parent / "_lib" / "render.py"
PROJ = Path(__file__).resolve().parent.parent
sys.exit(subprocess.call(
    [sys.executable, str(LIB), "--base-dir", str(PROJ)] + sys.argv[1:]
))