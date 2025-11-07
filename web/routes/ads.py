from fastapi import APIRouter
import pymysql
from config.settings import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME

router = APIRouter()


def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
    )


@router.get("/")
def list_ads(
    city: str | None = None, min_price: int | None = None, max_price: int | None = None
):
    query = "SELECT * FROM ads WHERE 1=1"
    params = []

    if city:
        query += " AND city LIKE %s"
        params.append(f"%{city}%")
    if min_price:
        query += " AND price >= %s"
        params.append(min_price)
    if max_price:
        query += " AND price <= %s"
        params.append(max_price)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            data = cur.fetchall()

    return {"count": len(data), "ads": data}
