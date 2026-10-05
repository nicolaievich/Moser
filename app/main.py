from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.monitoring.system import get_hardware_info, get_system_status

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Moser",
    description="Panóptico del servidor: monitor ligero de Linux.",
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def monitor(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Moser"},
    )


@app.get("/api/system/info")
async def system_info():
    return get_hardware_info()


@app.get("/api/system/status")
async def system_status():
    return get_system_status()


@app.get("/health")
async def health():
    return {"status": "ok"}
