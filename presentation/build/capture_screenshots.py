"""Capture dashboard screenshots for the slides (optional; needs `pip install playwright` and
`playwright install chromium`). Start the app first:  streamlit run app/app.py --server.port 8599"""
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
PAGES = {"Overview": "dashboard_overview.png", "5. 2026 scenarios": "dashboard_scenarios.png"}


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1500, "height": 950}, device_scale_factor=1.5)
        await pg.goto("http://localhost:8599", wait_until="networkidle")
        await pg.wait_for_timeout(6000)
        for name, fn in PAGES.items():
            await pg.get_by_text(name, exact=True).first.click()
            await pg.wait_for_timeout(5000)
            await pg.screenshot(path=str(HERE / fn))
        await b.close()

asyncio.run(main())
