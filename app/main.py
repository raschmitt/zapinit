from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="zapinit")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, theme: str = None) -> HTMLResponse:
    theme = theme or request.cookies.get("theme")
    if theme not in ("light", "dark"):
        theme = None
    return templates.TemplateResponse(request, "index.html", {"theme": theme})
