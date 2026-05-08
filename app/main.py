from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="zapinit")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


def test_sonar_comment():
    """This will trigger SonarCloud warnings"""
    password = "hardcoded123"  # Security issue
    unused_var = 42  # Code smell
    eval("1+1")  # Critical security issue
