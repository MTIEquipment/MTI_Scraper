import asyncio
import csv
from playwright.async_api import async_playwright


async def run():
    print("Opening browser for MachineryTrader...")
    async with async_playwright() as p:
        # Launch browser with realistic screen dimensions
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()

        print("Navigating to MachineryTrader directional drills...")
        await page.goto(
            "https://www.machinerytrader.com/listings/search?Category=1031",
            wait_until="domcontentloaded",
        )

        # Wait for equipment listings grid to render
        print("Waiting for page items to populate...")
        await page.wait_for_timeout(6000)

        # Scroll to ensure elements load into the DOM
        await page.evaluate("window.scrollTo(0, 1000)")
        await page.wait_for_timeout(2000)

        links = await page.locator("a").all()
        equipment_listings = []

        for link in links:
            text = await link.inner_text()
            href = await link.get_attribute("href")

            if text and href:
                clean_text = " ".join(text.split())

                # Target equipment detail URL patterns
                if (
                    "/listing/for-sale/" in href.lower()
                    and len(clean_text) > 8
                ):
                    full_url = (
                        href
                        if href.startswith("http")
                        else f"https://www.machinerytrader.com{href}"
                    )

                    if not any(
                        item["URL"] == full_url for item in equipment_listings
                    ):
                        equipment_listings.append(
                            {"Title": clean_text, "URL": full_url}
                        )

        await browser.close()

        # Save to a dedicated CSV for MachineryTrader
        csv_file = "machinery_trader_listings.csv"
        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["Title", "URL"])
            writer.writeheader()
            writer.writerows(equipment_listings)

        print("\n" + "=" * 60)
        print(
            f"SUCCESS! Saved {len(equipment_listings)} MachineryTrader"
            f" listings to '{csv_file}'"
        )
        print("=" * 60)


asyncio.run(run())