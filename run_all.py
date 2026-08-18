import csv
import os
import re
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY", ""))

def run_scrapers():
    print("Starting Firecrawl cloud scraper...")
    master_listings = []

    # 1. HDD BROKER SCRAPER
    try:
        print("Scraping HDD Broker...")
        hdd_res = app.scrape_url("https://www.hddbroker.com/listings/search", params={'formats': ['markdown']})
        markdown_text = hdd_res.get('markdown', '')

        # Extract [Title](URL) pattern from Markdown directly
        matches = re.findall(r'\[([^\]]+)\]\((https?://[^\)]+)\)', markdown_text)
        
        for title, raw_url in matches:
            # Match HDD Broker listings that contain reference IDs or equipment keywords
            if "hddbroker.com" in raw_url and ("ref=" in raw_url or "view" in raw_url or "listings" in raw_url):
                # Ensure HTTPS and remove trailing parameters
                clean_url = raw_url.replace("http://", "https://")
                if not any(item['URL'] == clean_url for item in master_listings):
                    master_listings.append({
                        "Source": "HDD Broker",
                        "Title": title.strip().replace('\n', ' '),
                        "URL": clean_url
                    })
    except Exception as e:
        print(f"Error scraping HDD Broker: {e}")

    # 2. MACHINERY TRADER & EQUIPMENT TRADER
    other_sources = [
        ("Machinery Trader", "https://www.machinerytrader.com/listings/search?Category=1031"),
        ("Equipment Trader", "https://www.equipmenttrader.com/Directional-Drill/equipment-for-sale?category=Directional%20Drill%7C644247801")
    ]

    for source, url in other_sources:
        try:
            print(f"Scraping {source}...")
            res = app.scrape_url(url, params={'formats': ['links']})
            for link in res.get('links', []):
                if "/listing/" in link.lower() or "directional-drill" in link.lower():
                    title_part = link.split('/')[-1].replace('-', ' ').title()
                    if len(title_part) > 5 and not any(item['URL'] == link for item in master_listings):
                        master_listings.append({
                            "Source": source,
                            "Title": title_part,
                            "URL": link
                        })
        except Exception as e:
            print(f"Error scraping {source}: {e}")

    # Save to CSV
    with open('all_listings.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Source", "Title", "URL"])
        writer.writeheader()
        writer.writerows(master_listings)

    print(f"Successfully updated 'all_listings.csv' with {len(master_listings)} total items.")

if __name__ == "__main__":
    run_scrapers()
