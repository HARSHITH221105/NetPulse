
from backend.discovery.arp_reader import parse_arp_table


SAMPLE_ARP = """
Interface: 192.168.0.112 --- 0x8
  Internet Address      Physical Address      Type
  192.168.0.1           a8-6e-84-ca-53-d4     dynamic
  192.168.0.100         56-9b-d7-bf-23-89     dynamic
  224.0.0.251           01-00-5e-00-00-fb     static
  192.168.0.255         ff-ff-ff-ff-ff-ff     static

Interface: 192.168.80.1 --- 0x2f
  Internet Address      Physical Address      Type
  192.168.92.52         00-15-5d-79-58-26     dynamic
"""


def test_parse_arp_table():
    mappings = parse_arp_table(SAMPLE_ARP)

    assert len(mappings) == 3
    assert mappings["192.168.0.1"] == "a8:6e:84:ca:53:d4"
    assert mappings["192.168.0.100"] == "56:9b:d7:bf:23:89"


def test_filter_multicast_and_broadcast():
    mappings = parse_arp_table(SAMPLE_ARP)

    assert "224.0.0.251" not in mappings
    assert "192.168.0.255" not in mappings


def test_filter_by_interface():
    mappings = parse_arp_table(
        SAMPLE_ARP,
        interface_ip="192.168.0.112"
    )

    assert "192.168.0.1" in mappings
    assert "192.168.92.52" not in mappings


def test_empty_arp_table():
    assert parse_arp_table("") == {}


def test_unknown_interface():
    mappings = parse_arp_table(
        SAMPLE_ARP,
        interface_ip="10.0.0.1"
    )

    assert mappings == {}


def test_invalid_interface_entries():
    arp_output = """
Interface: 192.168.0.112 --- 0x8
  Internet Address      Physical Address      Type
  invalid-ip            a8-6e-84-ca-53-d4     dynamic
  192.168.0.1           invalid-mac            dynamic
"""

    assert parse_arp_table(arp_output) == {}
