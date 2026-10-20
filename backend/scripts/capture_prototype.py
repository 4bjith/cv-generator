import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    out_path = os.path.join(root, "screenshots", "17_unified_command_center_prototype.png")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1.5)
        await page.goto("http://localhost:3000/prototype.html")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=out_path)
        print("Captured prototype screenshot to:", out_path)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
