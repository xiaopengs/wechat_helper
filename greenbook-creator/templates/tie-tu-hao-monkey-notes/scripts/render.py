#!/usr/bin/env python3
"""Render 8 Superset HTML cards to PNG via Playwright + Chromium."""

import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path("/home/ubuntu/.openclaw/workspace/output/superset-greenbook/v2")
HTML_DIR = BASE_DIR / "html"
OUT_DIR = BASE_DIR / "images"
OUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 1080
HEIGHT = 1440
DPR = 2  # retina quality


def render_card(page, html_path: Path, out_path: Path):
    url = f"file://{html_path.resolve()}"
    page.goto(url, wait_until="networkidle", timeout=30000)
    # Wait for fonts to settle
    page.wait_for_timeout(1500)
    page.screenshot(
        path=str(out_path),
        clip={"x": 0, "y": 0, "width": WIDTH, "height": HEIGHT},
        omit_background=False,
        type="png",
    )
    print(f"  ✓ {out_path.name}")


def main():
    cards = sorted(HTML_DIR.glob("card_*.html"))
    if not cards:
        print("No card_*.html found")
        sys.exit(1)
    print(f"Found {len(cards)} cards")

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
        ctx = browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            device_scale_factor=DPR,
        )
        page = ctx.new_page()
        for html in cards:
            out = OUT_DIR / (html.stem + ".png")
            print(f"Rendering {html.name}...")
            try:
                render_card(page, html, out)
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
        ctx.close()
        browser.close()

    print("\n✓ All cards rendered")


if __name__ == "__main__":
    main()