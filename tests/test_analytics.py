
from backend.monitoring.analytics import (
    get_device_analytics,
    get_all_device_analytics
)


def test_healthy_device(monkeypatch):

    sample_history = [
        {
            "ip_address": "192.168.1.10",
            "status": "ONLINE",
            "latency_ms": 20.0,
            "packet_loss": 0.0
        },
        {
            "ip_address": "192.168.1.10",
            "status": "ONLINE",
            "latency_ms": 40.0,
            "packet_loss": 0.0
        }
    ]

    monkeypatch.setattr(
        "backend.monitoring.analytics.get_monitoring_history",
        lambda: sample_history
    )

    result = get_device_analytics("192.168.1.10")

    assert result["health"] == "HEALTHY"
    assert result["total_checks"] == 2
    assert result["successful_checks"] == 2
    assert result["average_latency"] == 30.0
    assert result["average_packet_loss"] == 0.0


def test_warning_device(monkeypatch):

    sample_history = [
        {
            "ip_address": "192.168.1.20",
            "status": "ONLINE",
            "latency_ms": 120.0,
            "packet_loss": 3.0
        },
        {
            "ip_address": "192.168.1.20",
            "status": "ONLINE",
            "latency_ms": 160.0,
            "packet_loss": 4.0
        }
    ]

    monkeypatch.setattr(
        "backend.monitoring.analytics.get_monitoring_history",
        lambda: sample_history
    )

    result = get_device_analytics("192.168.1.20")

    assert result["health"] == "WARNING"
    assert result["average_latency"] == 140.0
    assert result["average_packet_loss"] == 3.5


def test_critical_device(monkeypatch):

    sample_history = [
        {
            "ip_address": "192.168.1.30",
            "status": "NO_RESPONSE",
            "latency_ms": None,
            "packet_loss": 100.0
        },
        {
            "ip_address": "192.168.1.30",
            "status": "NO_RESPONSE",
            "latency_ms": None,
            "packet_loss": 100.0
        }
    ]

    monkeypatch.setattr(
        "backend.monitoring.analytics.get_monitoring_history",
        lambda: sample_history
    )

    result = get_device_analytics("192.168.1.30")

    assert result["health"] == "CRITICAL"
    assert result["successful_checks"] == 0
    assert result["failed_checks"] == 2
    assert result["success_percentage"] == 0.0


def test_all_device_analytics(monkeypatch):

    sample_history = [
        {
            "ip_address": "192.168.1.10",
            "status": "ONLINE",
            "latency_ms": 20.0,
            "packet_loss": 0.0
        },
        {
            "ip_address": "192.168.1.20",
            "status": "ONLINE",
            "latency_ms": 120.0,
            "packet_loss": 3.0
        }
    ]

    monkeypatch.setattr(
        "backend.monitoring.analytics.get_monitoring_history",
        lambda: sample_history
    )

    results = get_all_device_analytics()

    assert len(results) == 2

    device_ips = [device["ip"] for device in results]

    assert "192.168.1.10" in device_ips
    assert "192.168.1.20" in device_ips


def test_unknown_device(monkeypatch):

    monkeypatch.setattr(
        "backend.monitoring.analytics.get_monitoring_history",
        lambda: []
    )

    result = get_device_analytics("192.0.2.1")

    assert result is None
