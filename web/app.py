from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Mount static files (JS, CSS, etc.)
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="web/templates")


# Route to serve index.html
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
