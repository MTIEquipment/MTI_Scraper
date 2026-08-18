import csv
import os
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY", ""))

def run_scrapers():
    print("Starting AI-powered extraction scraper...")
    master_listings = []

    # Schema definition telling Firecrawl exactly what fields to extract
    json_schema = {
        "type": "object",
        "properties": {
            "listings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "price": {"type": "string"},
                        "url": {"type": "string"}
                    },
                    "required": ["title", "url"]
                }
            }
        }
    }

    sources = [
        ("HDD Broker", "https://www.hddbroker.com/listings/search"),
        ("Machinery Trader", "https://www.machinerytrader.com/listings/search?Category=1031"),
        ("Equipment Trader", "https://www.equipmenttrader.com/Directional-Drill/equipment-for-sale?category=Directional%20Drill%7C644247801")
    ]

    for source_name, target_url in sources:
        print(f"Extracting structured data from {source_name}...")
        try:
            # Use Firecrawl AI Extraction
            res = app.scrape_url(
                target_url,
                params={
                    'formats': ['extract'],
                    'extract': {
                        'schema': json_schema,
                        'prompt': "Extract all equipment listings with their full title, price (or 'Call for Price' if unlisted), and absolute URL link."
                    }
                }
            )

            extracted_data = res.get('extract', {}).get('listings', [])

            for item in extracted_data:
                title = item.get('title', 'Unknown Equipment').strip()
                price = item.get('price', 'Call for Price').strip()
                url = item.get('url', '').strip()

                if url:
                    # Fix relative URLs for HDD Broker if necessary
                    if source_name == "HDD Broker" and not url.startswith("http"):
                        url = f"https://www.hddbroker.com{url}"

                    if not any(entry['URL'] == url for entry in master_listings):
                        master_listings.append({
                            "Source": source_name,
                            "Title": title,
                            "Price": price if price else "Call for Price",
                            "URL": url
                        })

        except Exception as e:
            print(f"Error extracting from {source_name}: {e}")

    # Save structured results to CSV
    with open('all_listings.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Source", "Title", "Price", "URL"])
        writer.writeheader()
        writer.writerows(master_listings)

    print(f"Extraction complete! Saved {len(master_listings)} listings.")

if __name__ == "__main__":
    run_scrapers()
