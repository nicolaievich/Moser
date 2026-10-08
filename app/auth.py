from pathlib import Path
import sqlite3

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException, Request

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(__import__("os").environ.get("MOSER_DATA_DIR", BASE_DIR / "data"))
DB_PATH = DATA_DIR / "moser.db"
_password_hasher = PasswordHasher()


def _connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    connection.commit()
    return connection


def user_exists() -> bool:
    connection = _connect()
    try:
        return connection.execute("SELECT 1 FROM users LIMIT 1").fetchone() is not None
    finally:
        connection.close()


def create_user(username: str, password: str) -> None:
    username = username.strip()
    if len(username) < 3:
        raise ValueError("El usuario debe tener al menos 3 caracteres.")
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")
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
