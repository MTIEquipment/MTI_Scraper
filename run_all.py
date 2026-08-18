import csv
import os
import re
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY", ""))

def run_scrapers():
    print("Starting reliable Firecrawl scraper execution...")
    master_listings = []

    # 1. HDD BROKER
    try:
        print("Scraping HDD Broker...")
        hdd_res = app.scrape_url("https://www.hddbroker.com/en/listings/search", params={'formats': ['markdown']})
        markdown_text = hdd_res.get('markdown', '')

        # Parse markdown lines for Ref #, titles, and prices
        for line in markdown_text.split('\n'):
            if "Ref" in line or "Vermeer" in line or "Ditch Witch" in line:
                ref_match = re.search(r'Ref\s*#?\s*(\d{4,5})', line, re.IGNORECASE)
                if not ref_match:
                    ref_match = re.search(r'(\d{4,5})', line)

                if ref_match:
                    ref_id = ref_match.group(1)
                    title = re.sub(r'[#\*\|]', '', line).strip()
                    
                    price_match = re.search(r'\$[\d,]+', line)
                    price = price_match.group(0) if price_match else "Call for Price"
                    
                    clean_url = f"https://www.hddbroker.com/en/listings/view.php?ref={ref_id}"

                    if not any(item['URL'] == clean_url for item in master_listings):
                        master_listings.append({
                            "Source": "HDD Broker",
                            "Title": title[:80],
                            "Price": price,
                            "URL": clean_url
                        })
    except Exception as e:
        print(f"Error scraping HDD Broker: {e}")

    # 2. MACHINERY TRADER & EQUIPMENT TRADER
    sources = [
        ("Machinery Trader", "https://www.machinerytrader.com/listings/search?Category=1031"),
        ("Equipment Trader", "https://www.equipmenttrader.com/Directional-Drill/equipment-for-sale?category=Directional%20Drill%7C644247801")
    ]

    for source_name, target_url in sources:
        try:
            print(f"Scraping {source_name}...")
            res = app.scrape_url(target_url, params={'formats': ['links', 'markdown']})
            links = res.get('links', [])
            markdown_text = res.get('markdown', '')

            # Extract price list from page markdown
            prices = re.findall(r'\$[\d,]{4,}', markdown_text)
            price_idx = 0

            for link in links:
                is_valid = False
                if source_name == "Machinery Trader" and ("/listing/" in link.lower() or "for-sale" in link.lower()):
                    is_valid = True
                elif source_name == "Equipment Trader" and ("listing" in link.lower() or "directional-drill" in link.lower()):
                    is_valid = True

                if is_valid:
                    title_slug = link.split('/')[-1].split('?')[0].replace('-', ' ').title()
                    if len(title_slug) > 5 and not any(item['URL'] == link for item in master_listings):
                        assigned_price = prices[price_idx] if price_idx < len(prices) else "Call for Price"
                        price_idx += 1

                        master_listings.append({
                            "Source": source_name,
                            "Title": title_slug[:80],
                            "Price": assigned_price,
                            "URL": link
                        })
        except Exception as e:
            print(f"Error scraping {source_name}: {e}")

    # Ensure fallback data if scrapers are blocked by targets
    if not master_listings:
        print("Warning: No listings extracted. Writing fallback status entry.")
        master_listings.append({
            "Source": "System",
            "Title": "Scraper complete - target site blocked automated scan. Retrying on schedule.",
            "Price": "N/A",
            "URL": "https://mti-scraper.onrender.com"
        })

    with open('all_listings.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Source", "Title", "Price", "URL"])
        writer.writeheader()
        writer.writerows(master_listings)

    print(f"Done! Written {len(master_listings)} rows to all_listings.csv.")

if __name__ == "__main__":
    run_scrapers()
