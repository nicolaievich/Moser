#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [ "${EUID}" -eq 0 ]; then
  echo "ERROR: Moser no debe ejecutarse como root."
  echo "Para desarrollo, iniciá sesión con tu usuario y ejecutá ./start.sh."
  echo "Para uso permanente, instalá el servicio con sudo ./install-service.sh."
  exit 1
fi

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

HOST="${MOSER_HOST:-127.0.0.1}"
PORT="${MOSER_PORT:-3000}"

echo "Moser iniciando en http://$HOST:$PORT"
if [ "$HOST" = "127.0.0.1" ] || [ "$HOST" = "localhost" ]; then
  echo "Acceso local únicamente. Para acceso remoto, configurá conscientemente la red y el proxy."
fi
exec "$ROOT/venv/bin/uvicorn" app.main:app --host "$HOST" --port "$PORT"
