#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [ ! -x "$ROOT/venv/bin/uvicorn" ]; then
  echo "Moser no está instalado todavía."
  echo "Ejecutá: ./install.sh"
  exit 1
fi

if [ -f "$ROOT/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$ROOT/.env"
  set +a
fi

echo "Moser iniciando en http://0.0.0.0:3000"
exec "$ROOT/venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 3000
