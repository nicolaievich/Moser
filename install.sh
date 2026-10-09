#!/usr/bin/env bash
set -euo pipefail
umask 077

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [ "${EUID}" -eq 0 ]; then
  echo "ERROR: no ejecutes ./install.sh con sudo."
  echo "La instalación de Python debe pertenecer a tu usuario."
  echo "Para el servicio permanente existe ./install-service.sh, que sí usa sudo."
  exit 1
fi

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

if [ ! -w "$ROOT" ]; then
  echo "ERROR: tu usuario no puede escribir en $ROOT."
  echo "Usá una copia de trabajo que pertenezca a tu usuario."
  exit 1
fi

if [ -e "$ROOT/data" ] && [ ! -w "$ROOT/data" ]; then
  echo "ERROR: no podés escribir en $ROOT/data."
  echo "Esto suele ocurrir si Moser se ejecutó antes con sudo."
  echo "Si esta es la instalación de desarrollo, corregí la propiedad con:"
  printf '  sudo chown -R %q:%q %q\n' "$(id -un)" "$(id -gn)" "$ROOT/data"
  echo "No borres la base de datos. Luego volvé a ejecutar ./install.sh."
  exit 1
fi

if [ -e "$ROOT/data/moser.db" ] && [ ! -w "$ROOT/data/moser.db" ]; then
  echo "ERROR: la base de datos existe, pero tu usuario no puede escribir en ella:"
  echo "  $ROOT/data/moser.db"
  echo "No la borres. Para una instalación de desarrollo, corregí su propiedad con:"
  printf '  sudo chown %q:%q %q\n' "$(id -un)" "$(id -gn)" "$ROOT/data/moser.db"
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
chmod 700 "$ROOT/data"

if [ ! -f "$ROOT/.env" ]; then
  echo "==> Generando configuración inicial..."
  SECRET="$("$ROOT/venv/bin/python" -c 'import secrets; print(secrets.token_urlsafe(48))')"
  cat > "$ROOT/.env" <<EOF
MOSER_SESSION_SECRET=$SECRET
MOSER_COOKIE_SECURE=false
MOSER_HOST=127.0.0.1
MOSER_PORT=3000
EOF
  chmod 600 "$ROOT/.env"
elif [ ! -r "$ROOT/.env" ] || [ ! -w "$ROOT/.env" ]; then
  echo "ERROR: .env existe, pero tu usuario no puede leerlo y modificarlo."
  echo "Revisá su propietario; no lo borres porque contiene la clave de sesión."
  exit 1
else
  chmod 600 "$ROOT/.env"
fi

chmod +x "$ROOT/start.sh" 2>/dev/null || true

echo
echo "Moser quedó instalado para desarrollo."
echo "Datos: $ROOT/data (solo accesibles por tu usuario)"
echo "Configuración: $ROOT/.env (solo accesible por tu usuario)"
echo
echo "Para iniciarlo: ./start.sh"
echo "No uses sudo para ejecutar Moser."
echo "Para instalarlo como servicio permanente: sudo ./install-service.sh"
