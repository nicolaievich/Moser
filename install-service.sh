#!/usr/bin/env bash
set -euo pipefail
umask 077

ROOT="$(cd "$(dirname "$0")" && pwd -P)"
SERVICE_USER="moser"
DATA_DIR="/var/lib/moser"
CONFIG_DIR="/etc/moser"
ENV_FILE="$CONFIG_DIR/moser.env"
UNIT_FILE="/etc/systemd/system/moser.service"

if [ "$EUID" -ne 0 ]; then
  echo "ERROR: este instalador necesita privilegios para crear el usuario y el servicio."
  echo "Ejecutalo desde el directorio del proyecto con: sudo ./install-service.sh"
  exit 1
fi

case "$ROOT/" in
  /home/*|/root/*)
    echo "ERROR: no instales el servicio desde un directorio privado de /home o /root."
    echo "Ubicá el repositorio en /opt o /srv y volvé a intentarlo."
    exit 1
    ;;
esac

if [[ "$ROOT" == *" "* ]]; then
  echo "ERROR: la ruta de instalación no puede contener espacios: $ROOT"
  exit 1
fi

if ! command -v systemctl >/dev/null 2>&1 || ! command -v useradd >/dev/null 2>&1; then
  echo "ERROR: este instalador requiere systemd y useradd (Ubuntu/Debian, por ejemplo)."
  exit 1
fi

if [ ! -x "$ROOT/venv/bin/uvicorn" ] || [ ! -x "$ROOT/venv/bin/python" ]; then
  echo "ERROR: primero instalá Moser como usuario normal:"
  echo "  ./install.sh"
  exit 1
fi

if pgrep -f '[u]vicorn app.main:app' >/dev/null 2>&1; then
  echo "ERROR: parece que Moser ya está ejecutándose manualmente."
  echo "Detenelo con Ctrl+C antes de migrar los datos al servicio."
  exit 1
fi

if find "$ROOT" -maxdepth 0 -perm /022 -print | grep -q .; then
  echo "ERROR: el directorio del código permite escritura al grupo u otros:"
  echo "  $ROOT"
  echo "Quitá esos permisos de escritura antes de instalar el servicio."
  exit 1
fi

if ! id "$SERVICE_USER" >/dev/null 2>&1; then
  if ! getent group "$SERVICE_USER" >/dev/null 2>&1; then
    groupadd --system "$SERVICE_USER"
  fi
  useradd --system --gid "$SERVICE_USER" --home-dir /nonexistent \
    --shell /usr/sbin/nologin --no-create-home "$SERVICE_USER"
fi

install -d -o "$SERVICE_USER" -g "$SERVICE_USER" -m 0750 "$DATA_DIR"
install -d -o root -g "$SERVICE_USER" -m 0750 "$CONFIG_DIR"

SOURCE_DB="$ROOT/data/moser.db"
TARGET_DB="$DATA_DIR/moser.db"
if [ -f "$SOURCE_DB" ] && [ ! -e "$TARGET_DB" ]; then
  echo "==> Migrando la base de datos existente a $TARGET_DB ..."
  MOSER_DB_SOURCE="$SOURCE_DB" MOSER_DB_TARGET="$TARGET_DB" \
    "$ROOT/venv/bin/python" - <<'PY'
import os
import sqlite3

source = os.environ["MOSER_DB_SOURCE"]
target = os.environ["MOSER_DB_TARGET"]
src = sqlite3.connect(f"file:{source}?mode=ro", uri=True, timeout=10)
dst = sqlite3.connect(target, timeout=10)
try:
    src.backup(dst)
finally:
    dst.close()
    src.close()
PY
  chown "$SERVICE_USER:$SERVICE_USER" "$TARGET_DB"
  chmod 0600 "$TARGET_DB"
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "==> Creando configuración privada del servicio..."
  SECRET="$("$ROOT/venv/bin/python" -c 'import secrets; print(secrets.token_urlsafe(48))')"
  cat > "$ENV_FILE" <<EOF
MOSER_SESSION_SECRET=$SECRET
EOF
fi

if ! grep -q '^MOSER_SESSION_SECRET=.' "$ENV_FILE"; then
  echo "ERROR: $ENV_FILE no contiene MOSER_SESSION_SECRET."
  echo "No se sobrescribió la configuración. Agregá una clave segura y volvé a intentarlo."
  exit 1
fi

# En el modo servicio, estos valores son deliberadamente fijos: datos privados,
# cookie HTTPS y escucha local. Se conservan el resto de las variables existentes.
sed -i '/^MOSER_DATA_DIR=/d; /^MOSER_COOKIE_SECURE=/d; /^MOSER_HOST=/d; /^MOSER_PORT=/d' "$ENV_FILE"
cat >> "$ENV_FILE" <<EOF
MOSER_COOKIE_SECURE=true
MOSER_DATA_DIR=$DATA_DIR
MOSER_HOST=127.0.0.1
MOSER_PORT=3000
EOF
chown "root:$SERVICE_USER" "$ENV_FILE"
chmod 0640 "$ENV_FILE"

# Reparar propiedad de datos de un intento anterior sin tocar el código.
chown -R "$SERVICE_USER:$SERVICE_USER" "$DATA_DIR"
chmod 0750 "$DATA_DIR"
if [ -f "$TARGET_DB" ]; then
  chmod 0600 "$TARGET_DB"
fi

sed "s|@MOSER_ROOT@|$ROOT|g" "$ROOT/deploy/moser.service.in" > "$UNIT_FILE"
chmod 0644 "$UNIT_FILE"

systemctl daemon-reload
systemctl enable --now moser.service

echo
echo "Moser quedó instalado como servicio."
echo "Estado: sudo systemctl status moser"
echo "Registros: sudo journalctl -u moser -n 50 --no-pager"
echo "Dirección local: http://127.0.0.1:3000"
echo
echo "Moser se ejecuta como usuario '$SERVICE_USER', no como root."
echo "Los datos están en $DATA_DIR y la configuración privada en $ENV_FILE."
