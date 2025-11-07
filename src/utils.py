import json


# Save all ads into a JSON file
def save_to_json(data: list[dict], filename: str = "./data/ads.json"):
    import os

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nData exported to {filename}")
