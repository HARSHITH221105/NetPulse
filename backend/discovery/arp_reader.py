
import ipaddress
import re
import subprocess


def get_windows_arp_table():
    """Retrieve the Windows ARP table from WSL."""

    try:
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                "arp.exe -a"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip() or "Unable to retrieve ARP table."
            )

        return result.stdout

    except FileNotFoundError:
        raise RuntimeError(
            "PowerShell was not found. Run NetPulse from WSL2."
        )

    except subprocess.TimeoutExpired:
        raise RuntimeError("Windows ARP retrieval timed out.")


def parse_arp_table(arp_output, interface_ip=None):
    """Parse Windows ARP output and return unicast IP-to-MAC mappings."""

    mappings = {}
    current_interface = None

    for line in arp_output.splitlines():

        interface_match = re.search(
            r"Interface:\s+(\d{1,3}(?:\.\d{1,3}){3})",
            line
        )

        if interface_match:
            current_interface = interface_match.group(1)
            continue

        if interface_ip and current_interface != interface_ip:
            continue

        entry_match = re.match(
            r"\s*(\d{1,3}(?:\.\d{1,3}){3})"
            r"\s+([0-9a-fA-F-]{17})"
            r"\s+(dynamic|static)\s*$",
            line,
            re.IGNORECASE
        )

        if not entry_match:
            continue

        ip_address = entry_match.group(1)
        mac_address = entry_match.group(2)

        try:
            parsed_ip = ipaddress.ip_address(ip_address)
        except ValueError:
            continue

        if (
            parsed_ip.is_multicast
            or parsed_ip.is_unspecified
            or parsed_ip == ipaddress.ip_address("255.255.255.255")
        ):
            continue

        if mac_address.lower() == "ff-ff-ff-ff-ff-ff":
            continue

        mappings[ip_address] = mac_address.replace("-", ":").lower()

    return mappings


def get_arp_mappings(interface_ip=None):
    """Retrieve and parse Windows ARP mappings."""

    arp_output = get_windows_arp_table()

    return parse_arp_table(
        arp_output,
        interface_ip=interface_ip
    )
