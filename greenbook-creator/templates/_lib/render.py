#!/usr/bin/env python3
"""Render HTML cards to PNG via Playwright + Chromium.

Shared script for all greenbook HTML card templates.
Reads html/card_*.html from a project, writes images/card_*.png.

Usage:
  render.py --base-dir /path/to/project
  render.py --base-dir . --html-dir html --out-dir images
  render.py --base-dir . --width 1080 --height 1440 --dpr 2

Defaults: WIDTH=1080 HEIGHT=1440 DPR=2 (3:4 retina PNG 2160x2880).

Required: playwright + Chromium installed (pip install playwright && playwright install chromium).
"""
import argparse
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def render_cards(html_dir: Path, out_dir: Path, width: int, height: int, dpr: int) -> int:
    cards = sorted(html_dir.glob("card_*.html"))
    if not cards:
        print(f"No card_*.html found in {html_dir}", file=sys.stderr)
        return 1
    print(f"Found {len(cards)} cards in {html_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)
    errors = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
        ctx = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=dpr,
        )
        page = ctx.new_page()
        for html in cards:
            out = out_dir / (html.stem + ".png")
            print(f"Rendering {html.name}...")
            try:
                page.goto(f"file://{html.resolve()}", wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(1500)  # font settle
                page.screenshot(
                    path=str(out),
                    clip={"x": 0, "y": 0, "width": width, "height": height},
                    omit_background=False,
                    type="png",
                )
                print(f"  ✓ {out.name}")
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                errors += 1
        ctx.close()
        browser.close()

    print(f"\n{'✓ All cards rendered' if errors == 0 else f'⚠ {errors} card(s) failed'}")
    return 0 if errors == 0 else 2


def main():
    parser = argparse.ArgumentParser(description="Render HTML cards to PNG via Playwright")
    parser.add_argument("--base-dir", required=True, help="Project root (html/ + images/ live here)")
    parser.add_argument("--html-dir", default="html", help="HTML source dir (relative to base-dir)")
    parser.add_argument("--out-dir",  default="images", help="Output PNG dir (relative to base-dir)")
    parser.add_argument("--width",  type=int, default=1080, help="Viewport width (default 1080)")
    parser.add_argument("--height", type=int, default=1440, help="Viewport height (default 1440)")
    parser.add_argument("--dpr",    type=int, default=2,    help="device_scale_factor (default 2)")
    args = parser.parse_args()

    base = Path(args.base_dir).resolve()
    html_dir = base / args.html_dir
    out_dir = base / args.out_dir

    sys.exit(render_cards(html_dir, out_dir, args.width, args.height, args.dpr))


if __name__ == "__main__":
    main()