
import ipaddress
import subprocess

from backend.discovery import arp_reader, network_scanner
from backend.discovery.mac_lookup import enrich_devices


def resolve_hostname(ip_address, timeout=2):
    """Resolve an IP address using the system's reverse DNS lookup."""

    try:
        ipaddress.ip_address(ip_address)

        result = subprocess.run(
            ["getent", "hosts", ip_address],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode != 0 or not result.stdout.strip():
            return None

        parts = result.stdout.strip().split()

        if len(parts) >= 2:
            return parts[1].rstrip(".")

        return None

    except (ValueError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def categorize_device(device, gateway_ip=None):
    """Categorize devices using evidence, without guessing."""

    ip_address = device.get("ip")
    hostname = (device.get("hostname") or "").lower()

    if gateway_ip and ip_address == gateway_ip:
        return "GATEWAY"

    gateway_keywords = (
        "router",
        "gateway",
        "access-point",
        "accesspoint",
        "switch"
    )

    if any(keyword in hostname for keyword in gateway_keywords):
        return "NETWORK_INFRASTRUCTURE"

    return "UNKNOWN"


def build_device_inventory(
    discovered_devices,
    mac_mapping,
    gateway_ip=None,
    resolve_hostnames=True
):
    """Combine IP, MAC, manufacturer and hostname information."""

    inventory_devices = []

    for device in discovered_devices:
        record = device.copy()

        ip_address = record.get("ip")
        record["mac"] = mac_mapping.get(ip_address)

        if not record.get("hostname") and resolve_hostnames:
            record["hostname"] = resolve_hostname(ip_address)

        inventory_devices.append(record)

    enriched_devices = enrich_devices(inventory_devices)

    for device in enriched_devices:
        device["device_type"] = categorize_device(
            device,
            gateway_ip=gateway_ip
        )

    return enriched_devices


def discover_network_inventory(
    network,
    interface_ip=None,
    gateway_ip=None
):
    """Run discovery and automatically build the device inventory."""

    discovered_devices = network_scanner.discover_devices(network)

    mac_mapping = arp_reader.get_arp_mappings(
        interface_ip=interface_ip
    )

    return build_device_inventory(
        discovered_devices,
        mac_mapping,
        gateway_ip=gateway_ip
    )
