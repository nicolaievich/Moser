"""Autenticación local y almacenamiento SQLite de Moser."""

from pathlib import Path
import os
import sqlite3

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException, Request

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("MOSER_DATA_DIR", BASE_DIR / "data")).expanduser()
DB_PATH = DATA_DIR / "moser.db"
_password_hasher = PasswordHasher()


def _connect():
    """Abre SQLite creando archivos nuevos con permisos privados por defecto."""
    DATA_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    old_umask = os.umask(0o077)
    try:
        connection = sqlite3.connect(DB_PATH, timeout=5)
    finally:
        os.umask(old_umask)

    try:
        connection.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        connection.commit()
        return connection
    except Exception:
        connection.close()
        raise


def check_storage_writable() -> None:
    """Falla al iniciar si Moser no puede escribir en su base de datos.

    Detecta errores de permisos al arrancar, en vez de mostrarlos como un
    bucle de registro o un error 500 cuando el usuario intenta crear su cuenta.
    """
    connection = None
    try:
        connection = _connect()
        connection.execute("SAVEPOINT moser_permission_check")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS _moser_permission_check (id INTEGER PRIMARY KEY)"
        )
        connection.execute("INSERT INTO _moser_permission_check DEFAULT VALUES")
        connection.execute("DELETE FROM _moser_permission_check")
        connection.execute("DROP TABLE _moser_permission_check")
        connection.execute("RELEASE SAVEPOINT moser_permission_check")
        connection.commit()
    except (OSError, sqlite3.Error) as exc:
        raise RuntimeError(
            f"Moser no puede escribir en la base de datos {DB_PATH}. "
            f"Revisá el propietario y los permisos del directorio {DATA_DIR}. "
            "No ejecutes Moser con sudo para solucionar este problema."
        ) from exc
    finally:
        if connection is not None:
            connection.close()


def user_exists() -> bool:
    connection = _connect()
    try:
        return connection.execute("SELECT 1 FROM users LIMIT 1").fetchone() is not None
    finally:
        connection.close()


def password_strength_error(password: str) -> str | None:
    if len(password) < 10:
        return "La contraseña debe tener al menos 10 caracteres."
    checks = [
        any(char.islower() for char in password),
        any(char.isupper() for char in password),
        any(char.isdigit() for char in password),
        any(not char.isalnum() for char in password),
    ]
    if sum(checks) < 3:
        return "La contraseña debe combinar mayúsculas, minúsculas, números y símbolos (al menos 3 de estos 4 tipos)."
    return None


def create_user(username: str, password: str) -> None:
    username = username.strip()
    if len(username) < 3:
        raise ValueError("El usuario debe tener al menos 3 caracteres.")
    password_error = password_strength_error(password)
    if password_error:
        raise ValueError(password_error)
    password_hash = _password_hasher.hash(password)
    connection = _connect()
    try:
        connection.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        connection.commit()
    finally:
        connection.close()


def verify_user(username: str, password: str) -> bool:
    connection = _connect()
    try:
        row = connection.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()
    finally:
        connection.close()
    if row is None:
        return False
    try:
        return _password_hasher.verify(row[0], password)
    except VerifyMismatchError:
        return False


def require_auth(request: Request):
    if not request.session.get("authenticated"):
        raise HTTPException(status_code=401, detail="Autenticación requerida.")


def login_session(request: Request, username: str):
    request.session.clear()
    request.session["authenticated"] = True
    request.session["username"] = username.strip()


def logout_session(request: Request):
    request.session.clear()
