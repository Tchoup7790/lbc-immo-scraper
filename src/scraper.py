import time
import json
import requests
from lxml import html
from config.settings import HEADERS, BASE_URL
from src.utils import anonymize


# Fetch one page and return parsed JSON data from __NEXT_DATA__
def fetch_page(page: int) -> dict | None:
    url = BASE_URL.format(page)
    print(f"Fetching page {page}...")

    response = requests.get(url, headers=HEADERS, timeout=15)
    if response.status_code != 200:
        print(f"Failed to fetch page {page}: HTTP {response.status_code}")
        return None

    tree = html.fromstring(response.text)
    json_data_raw = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')

    if not json_data_raw:
        print("No JSON found in the page.")
        return None

    try:
        data = json.loads(json_data_raw[0])
        return data
    except json.JSONDecodeError:
        print(f"Invalid JSON on page {page}")
        return None


# Extract ads from the JSON structure
def parse_ads(data: dict) -> list[dict]:
    search_data = data.get("props", {}).get("pageProps", {}).get("searchData", {})
    ads = search_data.get("ads", [])
    parsed = []

    for ad in ads:
        location = ad.get("location", {})
        attributes = ad.get("attributes", [])
        images = ad.get("images", {})

        real_estate_type = next(
            (
                a.get("value_label")
                for a in attributes
                if a.get("key") == "real_estate_type"
            ),
            "N/A",
        )

        # Author info
        owner = ad.get("owner", {})
        author_name = owner.get("name", "N/A")
        has_phone = ad.get("has_phone", False)
        contact_info = "Disponible" if has_phone else "Non communiqué"

        parsed.append(
            {
                "title": ad.get("subject", "N/A"),
                "category": ad.get("category_name", "N/A"),
                "type": real_estate_type,
                "price": ad.get("price", [None])[0],
                "city": location.get("city", ""),
                "zipcode": location.get("zipcode", ""),
                "region": location.get("region_name", ""),
                "url": ad.get("url", ""),
                "image_url": images.get("urls", [None])[0],
                "author": author_name,
                "contact": contact_info,
            }
        )
    return parsed


# Scrape multiple pages using pagination until no more ads
def scrape_all_pages(max_pages: int = 10, delay: float = 1.0) -> list[dict]:
    all_ads = []
    for page in range(1, max_pages + 1):
        data = fetch_page(page)
        if not data:
            break
        ads = parse_ads(data)
        if not ads:
            print(f"No more ads on page {page}, stopping.")
            break

        # Anonymize each ad before saving
        anonymized = [anonymize(a) for a in ads]
        all_ads.extend(anonymized)

        print(f"Page {page}: {len(ads)} ads collected")
        time.sleep(delay)
    return all_ads
