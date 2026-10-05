"""Información básica de interfaces de red."""

import psutil


def get_network_info() -> list[dict]:
    result = []
    addresses = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    for name, addrs in addresses.items():
        interface = stats.get(name)
        result.append({
            "name": name,
            "up": bool(interface.isup) if interface else False,
            "speed_mbps": interface.speed if interface else 0,
            "addresses": [
                {"family": str(address.family), "address": address.address}
                for address in addrs
                if address.address
            ],
        })

    return result
