#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "==> Instalando Moser"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: Python 3 no está instalado."
  echo "En Ubuntu/Debian: sudo apt install python3 python3-venv"
  exit 1
fi

if ! python3 -m venv --help >/dev/null 2>&1; then
  echo "ERROR: falta el módulo venv de Python."
  echo "En Ubuntu/Debian: sudo apt install python3-venv"
  exit 1
fi

if [ ! -x "$ROOT/venv/bin/python" ]; then
  echo "==> Creando entorno virtual..."
  python3 -m venv "$ROOT/venv"
fi

echo "==> Instalando dependencias..."
"$ROOT/venv/bin/python" -m pip install --upgrade pip >/dev/null
"$ROOT/venv/bin/python" -m pip install -r "$ROOT/requirements.txt"

mkdir -p "$ROOT/data"

if [ ! -f "$ROOT/.env" ]; then
  echo "==> Generando configuración inicial..."
  SECRET="$("$ROOT/venv/bin/python" -c 'import secrets; print(secrets.token_urlsafe(48))')"
  cat > "$ROOT/.env" <<EOF
MOSER_SESSION_SECRET=$SECRET
MOSER_COOKIE_SECURE=false
EOF
fi

chmod +x "$ROOT/start.sh" 2>/dev/null || true

echo
echo "Moser quedó instalado."
echo
echo "Para iniciarlo:"
echo "  ./start.sh"
echo
echo "Luego abrí: http://localhost:3000"
