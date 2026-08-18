import csv
import os
from firecrawl import FirecrawlApp

# Initialize Firecrawl with your API key
# Pass FIRECRAWL_API_KEY as an Environment Variable in Render
app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY", "your_firecrawl_api_key_here"))

def run_scrapers():
    print("Starting Firecrawl cloud scraping suite...")
    master_listings = []

    urls = [
        ("HDD Broker", "https://www.hddbroker.com/listings/search"),
        ("Machinery Trader", "https://www.machinerytrader.com/listings/search?Category=1031"),
        ("Equipment Trader", "https://www.equipmenttrader.com/Directional-Drill/equipment-for-sale?category=Directional%20Drill%7C644247801")
    ]

    for source, url in urls:
        print(f"Scraping {source} via Firecrawl...")
        try:
            # Scrape page and extract markdown/links
            scrape_result = app.scrape_url(url, params={'formats': ['markdown', 'links']})
            links = scrape_result.get('links', [])

            for link in links:
                if "/listing/" in link.lower() or "directional-drill" in link.lower():
                    # Clean display title from URL structure
                    title_part = link.split('/')[-1].replace('-', ' ').title()
                    if len(title_part) > 5 and not any(item['URL'] == link for item in master_listings):
                        master_listings.append({
                            "Source": source,
                            "Title": title_part,
                            "URL": link
                        })
        except Exception as e:
            print(f"Error scraping {source}: {e}")

    # Save to master CSV
    with open('all_listings.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Source", "Title", "URL"])
        writer.writeheader()
        writer.writerows(master_listings)

    print(f"\nSUCCESS! Aggregated {len(master_listings)} listings into 'all_listings.csv'")

if __name__ == "__main__":
    run_scrapers()
