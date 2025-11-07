from fastapi import APIRouter, HTTPException, BackgroundTasks
from src.scraper import scrape_all_pages
from src.utils import insert_ads_to_db

router = APIRouter()


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
async def run_scrap(background_tasks: BackgroundTasks, max_pages: int = 10):
    try:
        background_tasks.add_task(run_scraping_task, max_pages)
        return {"message": f"Scraper launched in background (max_pages={max_pages})."}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to launch scraper: {str(e)}"
        )
