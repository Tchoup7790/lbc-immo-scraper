from src.scraper import scrape_all_pages
from src.utils import save_to_json
import os

if __name__ == "__main__":
    ads = scrape_all_pages()
    print(f"\nTotal ads scraped: {len(ads)}")
    save_to_json(ads)
