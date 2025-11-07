import time
import json
import requests
from lxml import html
from config.settings import HEADERS, BASE_URL


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
        print(f"__NEXT_DATA__ not found on page {page}")
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
    parsed_ads = []

    for ad in ads:
        title = ad.get("subject", "N/A")
        category = ad.get("category_name", "N/A")
        price = ad.get("price", [None])[0]
        url = ad.get("url", "N/A")
        location = ad.get("location", {})
        city = location.get("city", "")
        zipcode = location.get("zipcode", "")
        department = location.get("department_name", "")
        region = location.get("region_name", "")

        attributes = ad.get("attributes", [])
        real_estate_type = next(
            (
                a.get("value_label")
                for a in attributes
                if a.get("key") == "real_estate_type"
            ),
            "N/A",
        )

        parsed_ads.append(
            {
                "title": title,
                "category": category,
                "type": real_estate_type,
                "price": price,
                "city": city,
                "zipcode": zipcode,
                "department": department,
                "region": region,
                "url": url,
            }
        )

    return parsed_ads


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

        all_ads.extend(ads)
        print(f"Page {page}: {len(ads)} ads (total {len(all_ads)})")

        time.sleep(delay)

    return all_ads
