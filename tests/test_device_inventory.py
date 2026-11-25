
from backend.discovery import arp_reader, network_scanner
from backend.discovery.device_inventory import (
    build_device_inventory,
    discover_network_inventory,
    resolve_hostname,
    categorize_device
)


def test_build_device_inventory(monkeypatch):
    discovered_devices = [
        {
            "ip": "192.168.0.1",
            "status": "UP",
            "hostname": "router"
        },
        {
            "ip": "192.168.0.100",
            "status": "UP",
            "hostname": None
        }
    ]

    mac_mapping = {
        "192.168.0.1": "a8:6e:84:ca:53:d4",
        "192.168.0.100": "56:9b:d7:bf:23:89"
    }

    monkeypatch.setattr(
        "backend.discovery.device_inventory.resolve_hostname",
        lambda ip: None
    )

    inventory = build_device_inventory(
        discovered_devices,
        mac_mapping,
        resolve_hostnames=False
    )

    assert len(inventory) == 2
    assert inventory[0]["mac_address"] == "a8:6e:84:ca:53:d4"
    assert inventory[0]["vendor"] == "TP-Link Systems Inc"
    assert inventory[1]["address_type"] == "LOCAL"
    assert inventory[1]["vendor"] == "Unknown - locally administered"


def test_device_without_mac():
    discovered_devices = [
        {
            "ip": "192.168.0.101",
            "status": "UP",
            "hostname": None
        }
    ]

    inventory = build_device_inventory(
        discovered_devices,
        {},
        resolve_hostnames=False
    )

    assert inventory[0]["mac_address"] is None
    assert inventory[0]["vendor"] == "Unknown"


def test_unmapped_device_keeps_hostname():
    discovered_devices = [
        {
            "ip": "192.168.0.1",
            "status": "UP",
            "hostname": "gateway"
        }
    ]

    inventory = build_device_inventory(
        discovered_devices,
        {},
        resolve_hostnames=False
    )

    assert inventory[0]["hostname"] == "gateway"


def test_automatic_network_inventory(monkeypatch):
    discovered_devices = [
        {
            "ip": "192.168.0.1",
            "status": "UP",
            "hostname": "router"
        },
        {
            "ip": "192.168.0.100",
            "status": "UP",
            "hostname": None
        }
    ]

    mac_mapping = {
        "192.168.0.1": "a8:6e:84:ca:53:d4",
        "192.168.0.100": "56:9b:d7:bf:23:89"
    }

    monkeypatch.setattr(
        network_scanner,
        "discover_devices",
        lambda network: discovered_devices
    )

    monkeypatch.setattr(
        arp_reader,
        "get_arp_mappings",
        lambda interface_ip=None: mac_mapping
    )

    monkeypatch.setattr(
        "backend.discovery.device_inventory.resolve_hostname",
        lambda ip: None
    )

    inventory = discover_network_inventory(
        "192.168.0.0/24",
        interface_ip="192.168.0.112",
        gateway_ip="192.168.0.1"
    )

    assert len(inventory) == 2
    assert inventory[0]["vendor"] == "TP-Link Systems Inc"
    assert inventory[0]["device_type"] == "GATEWAY"
    assert inventory[1]["address_type"] == "LOCAL"


def test_automatic_inventory_without_mac(monkeypatch):
    discovered_devices = [
        {
            "ip": "192.168.0.101",
            "status": "UP",
            "hostname": None
        }
    ]

    monkeypatch.setattr(
        network_scanner,
        "discover_devices",
        lambda network: discovered_devices
    )

    monkeypatch.setattr(
        arp_reader,
        "get_arp_mappings",
        lambda interface_ip=None: {}
    )

    monkeypatch.setattr(
        "backend.discovery.device_inventory.resolve_hostname",
        lambda ip: None
    )

    inventory = discover_network_inventory(
        "192.168.0.0/24",
        interface_ip="192.168.0.112"
    )

    assert len(inventory) == 1
    assert inventory[0]["mac_address"] is None
    assert inventory[0]["vendor"] == "Unknown"
    assert inventory[0]["device_type"] == "UNKNOWN"


def test_resolve_hostname(monkeypatch):
    class FakeResult:
        returncode = 0
        stdout = "192.168.0.1 router.local\n"

    monkeypatch.setattr(
        "backend.discovery.device_inventory.subprocess.run",
        lambda *args, **kwargs: FakeResult()
    )

    assert resolve_hostname("192.168.0.1") == "router.local"


def test_resolve_hostname_not_found(monkeypatch):
    class FakeResult:
        returncode = 2
        stdout = ""

    monkeypatch.setattr(
        "backend.discovery.device_inventory.subprocess.run",
        lambda *args, **kwargs: FakeResult()
    )

    assert resolve_hostname("192.168.0.100") is None


def test_gateway_categorization():
    device = {"ip": "192.168.0.1", "hostname": None}

    assert categorize_device(
        device,
        gateway_ip="192.168.0.1"
    ) == "GATEWAY"


def test_infrastructure_categorization():
    device = {
        "ip": "192.168.0.5",
        "hostname": "office-router.local"
    }

    assert categorize_device(device) == "NETWORK_INFRASTRUCTURE"


def test_unknown_device_categorization():
    device = {
        "ip": "192.168.0.100",
        "hostname": None
    }

    assert categorize_device(device) == "UNKNOWN"
