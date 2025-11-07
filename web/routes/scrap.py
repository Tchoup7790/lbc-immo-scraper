from fastapi import APIRouter, HTTPException
from src.scraper import scrape_all_pages
from src.utils import insert_ads_to_db
import threading

router = APIRouter()

# global flag
scraping_lock = threading.Lock()
scraping_in_progress = False


# Async background task: scrape and insert ads
async def run_scraping_task(max_pages: int):
    try:
        ads = scrape_all_pages(max_pages=max_pages)
        if ads:
            insert_ads_to_db(ads)
            print(f"[SCRAPER:OK] {len(ads)} ads scraped and inserted.")
        else:
            print("[SCRAPER:WARN] No ads found.")
    except Exception as e:
        print(f"[SCRAPER:KO] Error: {e}")


# Launch scraper in background
@router.post("/")
def run_scrap():
    global scraping_in_progress

    # Prevent concurrent runs
    if scraping_in_progress:
        raise HTTPException(status_code=409, detail="Scraping already in progress")

    def task():
        global scraping_in_progress
        try:
            print("Scraping started...")
            ads = scrape_all_pages(max_pages=10)
            insert_ads_to_db(ads)
            print(f"Scraping finished — {len(ads)} ads inserted.")
        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            scraping_in_progress = False
            scraping_lock.release()  # release the lock

    # Try acquiring the lock
    if scraping_lock.acquire(blocking=False):
        scraping_in_progress = True
        threading.Thread(target=task, daemon=True).start()
        return {"message": "Scraping started in background."}
    else:
        raise HTTPException(status_code=409, detail="Scraping already in progress")


@router.get("/status")
def scrap_status():
    return {"scraping": scraping_in_progress}
