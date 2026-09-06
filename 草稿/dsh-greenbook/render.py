#!/usr/bin/env python3
"""Render dsh-greenbook cards.html → 6 × 1080×1440 PNG"""
import pathlib
from playwright.sync_api import sync_playwright

BASE = pathlib.Path("/home/ubuntu/.openclaw/workspace/wechat_helper/草稿/dsh-greenbook")
HTML = BASE / "cards.html"
OUT = BASE / "images"

def main():
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1440}, device_scale_factor=1)
        page.goto(HTML.as_uri())
        page.wait_for_timeout(800)
        cards = page.query_selector_all(".card")
        print(f"found {len(cards)} cards")
        for i, card in enumerate(cards, 1):
            path = OUT / f"card_{i:02d}.png"
            card.screenshot(path=str(path))
            print(f"saved {path}")
        browser.close()

if __name__ == "__main__":
    main()
