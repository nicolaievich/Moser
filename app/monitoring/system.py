"""Lectura de información del sistema."""

import os
import platform
import socket
from pathlib import Path

import psutil


def _read_file(path: str) -> str | None:
    try:
        value = Path(path).read_text(encoding="utf-8").strip()
        return value or None
    except (OSError, UnicodeDecodeError):
        return None


def _bytes_to_gb(value: int) -> float:
    return round(value / (1024**3), 2)


def get_hardware_info() -> dict:
    """Devuelve la ficha relativamente estable de la máquina."""
    cpu_freq = psutil.cpu_freq()

    disks = []
    seen_devices: set[str] = set()
    for partition in psutil.disk_partitions(all=False):
        device = partition.device
        if device in seen_devices:
            continue
        seen_devices.add(device)
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except OSError:
            continue
        disks.append(
            {
                "device": device,
                "mountpoint": partition.mountpoint,
                "filesystem": partition.fstype,
                "total_gb": _bytes_to_gb(usage.total),
            }
        )

    return {
        "hostname": socket.gethostname(),
        "os": {
            "system": platform.system(),
            "distribution": _read_file("/etc/os-release"),
            "kernel": platform.release(),
            "architecture": platform.machine(),
        },
        "cpu": {
            "model": _read_file("/sys/devices/virtual/dmi/id/product_name")
            or platform.processor()
            or "Desconocido",
            "cores_physical": psutil.cpu_count(logical=False),
            "cores_logical": psutil.cpu_count(logical=True),
            "frequency_mhz": round(cpu_freq.max if cpu_freq else 0, 0),
        },
        "motherboard": {
            "manufacturer": _read_file("/sys/class/dmi/id/board_vendor"),
            "model": _read_file("/sys/class/dmi/id/board_name"),
            "version": _read_file("/sys/class/dmi/id/board_version"),
        },
        "memory": {
            "total_gb": _bytes_to_gb(psutil.virtual_memory().total),
        },
        "disks": disks,
    }


def get_system_status() -> dict:
    """Devuelve métricas que cambian continuamente."""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    load = os.getloadavg() if hasattr(os, "getloadavg") else (0, 0, 0)

    return {
        "cpu": {
            "usage_percent": psutil.cpu_percent(interval=None),
            "load_1": round(load[0], 2),
            "load_5": round(load[1], 2),
            "load_15": round(load[2], 2),
        },
        "memory": {
            "total_gb": _bytes_to_gb(memory.total),
            "used_gb": _bytes_to_gb(memory.used),
            "available_gb": _bytes_to_gb(memory.available),
            "usage_percent": memory.percent,
        },
        "disk": {
            "total_gb": _bytes_to_gb(disk.total),
            "used_gb": _bytes_to_gb(disk.used),
            "free_gb": _bytes_to_gb(disk.free),
            "usage_percent": disk.percent,
        },
        "boot_time": psutil.boot_time(),
        "processes": len(psutil.pids()),
    }
