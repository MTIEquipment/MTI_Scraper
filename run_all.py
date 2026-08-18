import asyncio
import csv
import os
import subprocess


def run_scrapers():
    print("Starting master scraper suite...")

    # Run each script
    subprocess.run(["python", "test_scraper.py"])
    subprocess.run(["python", "machinery_trader.py"])
    subprocess.run(["python", "equipment_trader.py"])

    master_listings = []

    # Read and combine CSVs
    files = [
        ("HDD Broker", "hdd_listings.csv"),
        ("Machinery Trader", "machinery_trader_listings.csv"),
        ("Equipment Trader", "equipment_trader_listings.csv"),
    ]

    for source, filename in files:
        if os.path.exists(filename):
            with open(filename, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Filter out header feedback links
                    if "feedback" not in row["URL"].lower():
                        master_listings.append(
                            {
                                "Source": source,
                                "Title": row["Title"],
                                "URL": row["URL"],
                            }
                        )

    # Write combined file
    with open(
        "all_listings.csv", mode="w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=["Source", "Title", "URL"]
        )
        writer.writeheader()
        writer.writerows(master_listings)

    print(
        f"\nSUCCESS! Combined {len(master_listings)} total listings into"
        " 'all_listings.csv'"
    )


if __name__ == "__main__":
    run_scrapers()