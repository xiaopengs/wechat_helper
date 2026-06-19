"""
OpenRouter 12 张 3:4 截图脚本
- Playwright + Chromium headless
- 每张 .slide element 单独截 1080×1440
- 输出到 screenshots/slide-NN.png
"""
import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).parent
HTML = ROOT / "index.html"
OUT = ROOT / "screenshots"
OUT.mkdir(exist_ok=True)

WIDTH = 1080
HEIGHT = 1440

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path="/home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome",
        )
        ctx = await browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            device_scale_factor=1,
        )
        page = await ctx.new_page()
        url = "file://" + str(HTML.resolve())
        await page.goto(url, wait_until="networkidle")
        # 等字体加载
        await page.wait_for_timeout(800)

        slides = await page.locator(".slide").all()
        print(f"Found {len(slides)} slides", file=sys.stderr)

        for i, slide in enumerate(slides, 1):
            out_path = OUT / f"slide-{i:02d}.png"
            await slide.screenshot(path=str(out_path), omit_background=False)
            size = out_path.stat().st_size
            print(f"  slide-{i:02d}.png  {size:>7} bytes  {out_path.name}")

        await browser.close()

asyncio.run(main())
