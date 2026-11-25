
import pytest

from backend.discovery.mac_lookup import (
    normalize_mac,
    is_locally_administered,
    identify_mac,
    enrich_devices
)


def test_normalize_mac():
    assert normalize_mac("A8-6E-84-CA-53-D4") == (
        "a8:6e:84:ca:53:d4"
    )


def test_local_mac_detection():
    assert is_locally_administered("56:9b:d7:bf:23:89")


def test_universal_mac_detection():
    assert not is_locally_administered("a8:6e:84:ca:53:d4")


def test_invalid_mac():
    with pytest.raises(ValueError):
        normalize_mac("invalid-mac")


def test_identify_mac():
    result = identify_mac("e2-87-2b-6f-e6-2c")

    assert result["address_type"] == "LOCAL"
    assert result["device_type"] == "Unknown"


def test_enrich_devices():
    devices = [
        {"ip": "192.168.0.1", "mac": "a8-6e-84-ca-53-d4"},
        {"ip": "192.168.0.100", "mac": "56-9b-d7-bf-23-89"}
    ]

    results = enrich_devices(devices)

    assert len(results) == 2
    assert results[0]["address_type"] == "UNIVERSAL"
    assert results[1]["address_type"] == "LOCAL"
