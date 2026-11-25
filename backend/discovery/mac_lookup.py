
import re

from mac_vendor_lookup import MacLookup, VendorNotFoundError


_vendor_lookup = MacLookup()


def normalize_mac(mac_address):
    """Validate and normalize a MAC address."""

    if not isinstance(mac_address, str):
        raise ValueError("MAC address must be a string.")

    cleaned = re.sub(r"[:-]", "", mac_address.strip())

    if not re.fullmatch(r"[0-9a-fA-F]{12}", cleaned):
        raise ValueError("Invalid MAC address.")

    return ":".join(
        cleaned[i:i + 2].lower()
        for i in range(0, 12, 2)
    )


def is_locally_administered(mac_address):
    """Check whether a MAC address is locally administered."""

    mac = normalize_mac(mac_address)
    first_octet = int(mac.split(":")[0], 16)

    return bool(first_octet & 0b10)


def lookup_vendor(mac_address):
    """Identify the registered manufacturer using the MAC prefix."""

    mac = normalize_mac(mac_address)

    if is_locally_administered(mac):
        return "Unknown - locally administered"

    try:
        return _vendor_lookup.lookup(mac)

    except VendorNotFoundError:
        return "Unknown manufacturer"

    except Exception:
        return "Manufacturer lookup unavailable"


def identify_mac(mac_address):
    """Generate MAC identity information."""

    mac = normalize_mac(mac_address)
    local = is_locally_administered(mac)

    return {
        "mac_address": mac,
        "address_type": "LOCAL" if local else "UNIVERSAL",
        "vendor": lookup_vendor(mac),
        "device_type": "Unknown"
    }


def enrich_devices(devices):
    """Add MAC identity information to discovered devices."""

    enriched = []

    for device in devices:
        record = device.copy()
        mac = record.get("mac")

        if mac:
            record.update(identify_mac(mac))
        else:
            record.update({
                "mac_address": None,
                "address_type": "UNKNOWN",
                "vendor": "Unknown",
                "device_type": "Unknown"
            })

        enriched.append(record)

    return enriched
