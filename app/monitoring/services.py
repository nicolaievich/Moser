"""Detección sencilla de servicios systemd.

Moser observa el estado; no inicia, detiene ni modifica servicios.
"""

import shutil
import subprocess

SERVICES = {
    "Docker": "docker",
    "SSH": "ssh",
    "Cloudflared": "cloudflared",
    "Cron": "cron",
    "n8n": "n8n",
    "Apache": "apache2",
    "Nginx": "nginx",
    "Caddy": "caddy",
}


def _is_active(service: str) -> bool:
    if shutil.which("systemctl") is None:
        return False
    result = subprocess.run(
        ["systemctl", "is-active", "--quiet", service],
        capture_output=True,
        timeout=2,
        check=False,
    )
    return result.returncode == 0


def get_services_status() -> list[dict]:
    return [
        {"name": name, "unit": unit, "active": _is_active(unit)}
        for name, unit in SERVICES.items()
    ]
