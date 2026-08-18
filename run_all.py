import csv
import os
import re
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY", ""))

def run_scrapers():
    print("Starting Firecrawl cloud scraper with prices & improved link parsing...")
    master_listings = []

    # 1. HDD BROKER SCRAPER
    try:
        print("Scraping HDD Broker...")
        hdd_res = app.scrape_url("https://www.hddbroker.com/listings/search", params={'formats': ['markdown']})
        markdown_text = hdd_res.get('markdown', '')

        # Extract items line by line from HDD Broker markdown output
        for line in markdown_text.split('\n'):
            if "Ref" in line or "Vermeer" in line or "Ditch Witch" in line:
                ref_match = re.search(r'(\d{4,5})', line)
                price_match = re.search(r'\$[\d,]+', line)
                
                if ref_match:
                    ref_id = ref_match.group(1)
                    title = re.sub(r'[#\*\|]', '', line).strip()
                    # Clean up price if found
                    price = price_match.group(0) if price_match else "Call for Price"
                    
                    # Direct link structure for HDD Broker items
                    clean_url = f"https://www.hddbroker.com/en/listings/view.php?ref={ref_id}"

                    if not any(item['URL'] == clean_url for item in master_listings):
                        master_listings.append({
                            "Source": "HDD Broker",
                            "Title": title[:80],  # Keep title concise
                            "Price": price,
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
            res = app.scrape_url(url, params={'formats': ['markdown', 'links']})
            markdown_text = res.get('markdown', '')
            links = res.get('links', [])

            # Extract prices and links
            for link in links:
                if "/listing/" in link.lower() or "directional-drill" in link.lower() or "listing" in link.lower():
                    # Parse title from link slug
                    title_slug = link.split('/')[-1].split('?')[0].replace('-', ' ').title()
                    if len(title_slug) > 5 and not any(item['URL'] == link for item in master_listings):
                        
                        # Look for price near the title in markdown if available
                        price_match = re.search(r'\$[\d,]{4,}', markdown_text)
                        price = price_match.group(0) if price_match else "Call for Price"

                        master_listings.append({
                            "Source": source,
                            "Title": title_slug[:80],
                            "Price": price,
                            "URL": link
                        })
        except Exception as e:
            print(f"Error scraping {source}: {e}")

    # Save to CSV
    with open('all_listings.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Source", "Title", "Price", "URL"])
        writer.writeheader()
        writer.writerows(master_listings)

    print(f"Done! Saved {len(master_listings)} listings to 'all_listings.csv'.")

if __name__ == "__main__":
    run_scrapers()
