from fastapi import APIRouter
from src.scraper import scrape_all_pages
from src.utils import insert_ads_to_db

router = APIRouter()


@router.post("/")
def run_scrap():
    ads = scrape_all_pages(max_pages=2)
    insert_ads_to_db(ads)
    return {"message": f"{len(ads)} ads scraped and inserted."}
