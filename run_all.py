import csv
import os
import re
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY", ""))

def run_scrapers():
    print("Starting Firecrawl cloud scraping suite...")
    master_listings = []

    urls = [
        ("HDD Broker", "https://www.hddbroker.com/listings/search"),
        ("Machinery Trader", "https://www.machinerytrader.com/listings/search?Category=1031"),
        ("Equipment Trader", "https://www.equipmenttrader.com/Directional-Drill/equipment-for-sale?category=Directional%20Drill%7C644247801")
    ]

    for source, url in urls:
        print(f"Scraping {source}...")
        try:
            scrape_result = app.scrape_url(url, params={'formats': ['markdown', 'links']})
            
            if source == "HDD Broker":
                markdown_text = scrape_result.get('markdown', '')
                # Extract titles and reference numbers directly from markdown text
                for line in markdown_text.split('\n'):
                    ref_match = re.search(r'Ref\s*#?\s*(\d{4,5})', line, re.IGNORECASE)
                    if ref_match and ("Ditch Witch" in line or "Vermeer" in line):
                        ref_num = ref_match.group(1)
                        title = line.strip().replace('*', '').replace('#', '')
                        listing_url = f"https://www.hddbroker.com/en/listings/view.php?ref={ref_num}"
                        
                        if not any(item['URL'] == listing_url for item in master_listings):
                            master_listings.append({
                                "Source": source,
                                "Title": title,
                                "URL": listing_url
                            })
            else:
                links = scrape_result.get('links', [])
                for link in links:
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

    with open('all_listings.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Source", "Title", "URL"])
        writer.writeheader()
        writer.writerows(master_listings)

    print(f"Done! Saved {len(master_listings)} listings.")

if __name__ == "__main__":
    run_scrapers()
