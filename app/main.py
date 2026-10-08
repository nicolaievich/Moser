from pathlib import Path
import os

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.auth import create_user, login_session, logout_session, require_auth, user_exists, verify_user
from app.monitoring.docker import get_docker_status
from app.monitoring.network import get_network_info
from app.monitoring.services import get_services_status
from app.monitoring.system import get_hardware_info, get_system_status

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="Moser", description="Panóptico del servidor: monitor ligero de Linux.", version="0.2.0")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("MOSER_SESSION_SECRET", "change-me-in-production"),
    session_cookie="moser_session",
    https_only=os.environ.get("MOSER_COOKIE_SECURE", "false").lower() == "true",
    same_site="lax",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request):
    if user_exists():
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(request=request, name="login.html", context={
        "title": "Configuración inicial · Moser", "heading": "Configuración inicial",
        "action": "/setup", "button": "Crear acceso", "autocomplete": "new-password", "error": None,
    })


@app.post("/setup", response_class=HTMLResponse)
async def setup(request: Request, username: str = Form(...), password: str = Form(...), password_confirm: str = Form(...)):
    if user_exists():
        return RedirectResponse("/login", status_code=303)
    if password != password_confirm:
        return templates.TemplateResponse(request=request, name="login.html", context={
            "title": "Configuración inicial · Moser", "heading": "Configuración inicial",
            "action": "/setup", "button": "Crear acceso", "autocomplete": "new-password", "error": "Las contraseñas no coinciden.",
        }, status_code=400)
    try:
        create_user(username, password)
    except ValueError as exc:
        return templates.TemplateResponse(request=request, name="login.html", context={
            "title": "Configuración inicial · Moser", "heading": "Configuración inicial",
            "action": "/setup", "button": "Crear acceso", "autocomplete": "new-password", "error": str(exc),
        }, status_code=400)
    login_session(request, username)
    return RedirectResponse("/", status_code=303)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("authenticated"):
        return RedirectResponse("/", status_code=303)
    if not user_exists():
        return RedirectResponse("/setup", status_code=303)
    return templates.TemplateResponse(request=request, name="login.html", context={
        "title": "Acceso · Moser", "heading": "Iniciar sesión", "action": "/login",
        "button": "Ingresar", "autocomplete": "current-password", "error": None,
    })


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if not user_exists():
        return RedirectResponse("/setup", status_code=303)
    if not verify_user(username, password):
        return templates.TemplateResponse(request=request, name="login.html", context={
            "title": "Acceso · Moser", "heading": "Iniciar sesión", "action": "/login",
            "button": "Ingresar", "autocomplete": "current-password",
            "error": "Usuario o contraseña incorrectos.",
        }, status_code=401)
    login_session(request, username)
    return RedirectResponse("/", status_code=303)


@app.post("/logout")
async def logout(request: Request):
    logout_session(request)
    return RedirectResponse("/login", status_code=303)


@app.get("/", response_class=HTMLResponse)
async def monitor(request: Request):
    if not request.session.get("authenticated"):
        return RedirectResponse("/setup" if not user_exists() else "/login", status_code=303)
    return templates.TemplateResponse(request=request, name="index.html", context={"title": "Moser"})


@app.get("/api/system/info")
async def system_info(request: Request):
    require_auth(request)
    return get_hardware_info()


@app.get("/api/system/status")
async def system_status(request: Request):
    require_auth(request)
    return get_system_status()


@app.get("/api/docker")
async def docker_status(request: Request):
    require_auth(request)
    return get_docker_status()


@app.get("/api/services")
async def services_status(request: Request):
    require_auth(request)
    return get_services_status()


@app.get("/api/network")
async def network_info(request: Request):
    require_auth(request)
    return get_network_info()


@app.get("/health")
async def health():
    return {"status": "ok"}
