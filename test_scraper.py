import asyncio
import csv
from playwright.async_api import async_playwright

async def run():
    print("Opening browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("Navigating to HDD Broker search listings...")
        await page.goto("https://www.hddbroker.com/en/listings/search.php?catid=1", wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        
        links = await page.locator("a").all()
        equipment_listings = []
        
        for link in links:
            text = await link.inner_text()
            href = await link.get_attribute("href")
            
            if text and href:
                clean_text = " ".join(text.split())
                
                # Check for drill model indicators
                has_year_or_brand = any(brand in clean_text.upper() for brand in ["VERMEER", "DITCH", "WITCH", "JT", "UNIVERSAL", "201", "202"])
                
                if has_year_or_brand and len(clean_text) > 8:
                    # Fix relative path formatting (removes '..' from URLs)
                    clean_href = href.replace("..", "")
                    full_url = clean_href if clean_href.startswith("http") else f"https://www.hddbroker.com{clean_href}"
                    
                    if not any(item["URL"] == full_url for item in equipment_listings):
                        equipment_listings.append({
                            "Title": clean_text,
                            "URL": full_url
                        })
        
        await browser.close()
        
        # Save to CSV
        csv_file = "hdd_listings.csv"
        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["Title", "URL"])
            writer.writeheader()
            writer.writerows(equipment_listings)
            
        print("\n" + "="*60)
        print(f"SUCCESS! Saved {len(equipment_listings)} drill listings with clean URLs.")
        print("="*60)

asyncio.run(run())