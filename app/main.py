from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


def build_wa_url(e164: str) -> str:
    cleaned = e164.lstrip("+").replace(" ", "").replace("-", "")
    if not cleaned:
        raise ValueError("E.164 number is empty")
    return f"https://wa.me/{cleaned}"


app = FastAPI(title="zapinit")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")
