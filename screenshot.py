# /// script
# dependencies = ["playwright"]
# ///

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

FLAVORS = ["mocha"]


async def capture_screenshot(flavor: str):
    async with async_playwright() as playwright_manager:
        browser_instance = await playwright_manager.chromium.launch()
        browser_page = await browser_instance.new_page()

        absolute_file_path = Path("test/_site/index.html").resolve()

        await browser_page.goto(f"file://{absolute_file_path}")
        await browser_page.screenshot(path=f"assets/{flavor}.png")
        await browser_instance.close()


if __name__ == "__main__":
    for flavor in FLAVORS:
        asyncio.run(capture_screenshot(flavor))
