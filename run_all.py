import csv
import os
import re
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY", ""))

def run_scrapers():
    print("Starting Firecrawl cloud scraper with price extraction...")
    master_listings = []

    # 1. HDD BROKER
    try:
        print("Scraping HDD Broker...")
        hdd_res = app.scrape_url("https://www.hddbroker.com/listings/search", params={'formats': ['markdown']})
        markdown_text = hdd_res.get('markdown', '')

        lines = markdown_text.split('\n')
        for i, line in enumerate(lines):
            ref_match = re.search(r'Ref\s*#?\s*(\d{4,5})', line, re.IGNORECASE)
            if ref_match and ("Ditch Witch" in line or "Vermeer" in line or "Rig" in line or "Drill" in line):
                ref_id = ref_match.group(1)
                title = line.strip().replace('*', '').replace('#', '')
                clean_url = f"https://www.hddbroker.com/en/listings/view.php?ref={ref_id}"

                # Extract dollar amount from line or adjacent markdown line
                price_match = re.search(r'\$[\d,]+', line)
                if not price_match and i + 1 < len(lines):
                    price_match = re.search(r'\$[\d,]+', lines[i+1])
                
                price = price_match.group(0) if price_match else "Call for Price"

                if not any(item['URL'] == clean_url for item in master_listings):
                    master_listings.append({
                        "Source": "HDD Broker",
                        "Title": title,
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

            for link in links:
                if "/listing/" in link.lower() or "directional-drill" in link.lower():
                    title_part = link.split('/')[-1].replace('-', ' ').title()
                    if len(title_part) > 5 and not any(item['URL'] == link for item in master_listings):
                        # Extract dollar amount
                        price_match = re.search(r'\$[\d,]+', markdown_text)
                        price = price_match.group(0) if price_match else "Call for Price"

                        master_listings.append({
                            "Source": source,
                            "Title": title_part,
                            "Price": price,
                            "URL": link
                        })
        except Exception as e:
            print(f"Error scraping {source}: {e}")

    # Save to CSV with Price field
    with open('all_listings.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Source", "Title", "Price", "URL"])
        writer.writeheader()
        writer.writerows(master_listings)

    print(f"Saved {len(master_listings)} listings with prices to 'all_listings.csv'.")

if __name__ == "__main__":
    run_scrapers()
