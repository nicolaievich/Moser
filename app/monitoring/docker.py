"""Lectura de Docker sin administrar el host.

Docker es opcional: si el SDK no está instalado o el daemon no responde,
Moser informa el motivo en lugar de romper el monitor completo.
"""

try:
    import docker
except ImportError:
    docker = None


def get_docker_status() -> dict:
    if docker is None:
        return {"available": False, "reason": "Docker SDK no instalado", "containers": []}

    try:
        client = docker.from_env()
        client.ping()
        containers = []
        for container in client.containers.list(all=True):
            containers.append({
                "id": container.short_id,
                "name": container.name,
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else container.image.short_id,
            })
        return {
            "available": True,
            "version": client.version().get("Version"),
            "containers": containers,
        }
    except Exception as exc:
        return {"available": False, "reason": str(exc), "containers": []}
