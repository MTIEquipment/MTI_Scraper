import csv
import os
import re
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY", ""))

def run_scrapers():
    print("Starting scraper execution...")
    master_listings = []

    # 1. HDD BROKER SCRAPER
    try:
        print("Scraping HDD Broker...")
        hdd_res = app.scrape_url("https://www.hddbroker.com/listings/search", params={'formats': ['markdown', 'links']})
        
        # Pull direct listing links from Firecrawl response
        for link in hdd_res.get('links', []):
            if "ref=" in link.lower() or "/view.php" in link.lower():
                # Extract ref number
                ref_match = re.search(r'ref=(\d+)', link, re.IGNORECASE)
                if ref_match:
                    ref_id = ref_match.group(1)
                    clean_url = f"https://www.hddbroker.com/en/listings/view.php?ref={ref_id}"
                    
                    if not any(item['URL'] == clean_url for item in master_listings):
                        master_listings.append({
                            "Source": "HDD Broker",
                            "Title": f"HDD Rig Ref #{ref_id}",
                            "URL": clean_url
                        })

        # Fallback: Parse markdown text if links array was filtered
        if not master_listings:
            markdown_text = hdd_res.get('markdown', '')
            matches = re.findall(r'\[([^\]]+)\]\(([^\)]*ref=(\d+)[^\)]*)\)', markdown_text, re.IGNORECASE)
            for title, raw_url, ref_id in matches:
                clean_url = f"https://www.hddbroker.com/en/listings/view.php?ref={ref_id}"
                if not any(item['URL'] == clean_url for item in master_listings):
                    master_listings.append({
                        "Source": "HDD Broker",
                        "Title": title.strip(),
                        "URL": clean_url
                    })
    except Exception as e:
        print(f"Error scraping HDD Broker: {e}")

    # 2. OTHER SOURCES
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

    # Save output CSV
    with open('all_listings.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Source", "Title", "URL"])
        writer.writeheader()
        writer.writerows(master_listings)

    print(f"Scrape completed successfully. {len(master_listings)} total items saved.")

if __name__ == "__main__":
    run_scrapers()
