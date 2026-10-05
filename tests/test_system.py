from app.monitoring.system import get_hardware_info, get_system_status


def test_hardware_info_has_expected_sections():
    data = get_hardware_info()
    assert "cpu" in data
    assert "memory" in data
    assert "motherboard" in data
    assert "disks" in data


def test_system_status_has_live_metrics():
    data = get_system_status()
    assert 0 <= data["memory"]["usage_percent"] <= 100
    assert 0 <= data["disk"]["usage_percent"] <= 100
    assert data["processes"] > 0
