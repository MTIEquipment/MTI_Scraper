import asyncio
import csv
from playwright.async_api import async_playwright


async def run():
    print("Opening browser for EquipmentTrader...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1400, "height": 900},
        )
        page = await context.new_page()

        # Direct search URL for Directional Drills
        url = "https://www.equipmenttrader.com/Directional-Drill/equipment-for-sale?category=Directional%20Drill%7C644247801"
        print("Navigating to EquipmentTrader drill listings...")
        await page.goto(url, wait_until="networkidle")

        # Give dynamic JavaScript elements time to hydrate
        print("Waiting for page items to populate...")
        await page.wait_for_timeout(5000)

        # Scroll incrementally to force lazy-loaded items to appear
        await page.evaluate("window.scrollBy(0, 600)")
        await page.wait_for_timeout(2000)
        await page.evaluate("window.scrollBy(0, 600)")
        await page.wait_for_timeout(2000)

        links = await page.locator("a").all()
        equipment_listings = []

        for link in links:
            text = await link.inner_text()
            href = await link.get_attribute("href")

            if text and href:
                clean_text = " ".join(text.split())

                # EquipmentTrader listing paths contain /listing/ or specific drill keywords
                is_listing = (
                    "/listing/" in href.lower()
                    or "directional-drill" in href.lower()
                )
                has_substance = len(clean_text) > 10 and not any(
                    skip in clean_text.lower()
                    for skip in ["search", "filter", "view all", "privacy"]
                )

                if is_listing and has_substance:
                    full_url = (
                        href
                        if href.startswith("http")
                        else f"https://www.equipmenttrader.com{href}"
                    )

                    if not any(
                        item["URL"] == full_url for item in equipment_listings
                    ):
                        equipment_listings.append(
                            {"Title": clean_text, "URL": full_url}
                        )

        await browser.close()

        # Save results
        csv_file = "equipment_trader_listings.csv"
        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["Title", "URL"])
            writer.writeheader()
            writer.writerows(equipment_listings)

        print("\n" + "=" * 60)
        print(
            f"SUCCESS! Saved {len(equipment_listings)} EquipmentTrader"
            f" listings to '{csv_file}'"
        )
        print("=" * 60)


asyncio.run(run())