
import ipaddress
import subprocess
import xml.etree.ElementTree as ET


def discover_devices(network):

    try:
        subnet = ipaddress.ip_network(network, strict=False)

        if not subnet.is_private:
            raise ValueError("Only private network ranges are allowed.")

        print(f"Starting NetPulse discovery on {subnet}")

        result = subprocess.run(
            [
                "nmap",
                "-sn",
                "-oX",
                "-",
                str(subnet)
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Nmap scan failed.")

        root = ET.fromstring(result.stdout)

        devices = []

        for host in root.findall("host"):

            status = host.find("status")

            if status is None or status.get("state") != "up":
                continue

            for address in host.findall("address"):

                if address.get("addrtype") != "ipv4":
                    continue

                hostname_element = host.find("hostnames/hostname")

                hostname = (
                    hostname_element.get("name")
                    if hostname_element is not None
                    else None
                )

                devices.append({
                    "ip": address.get("addr"),
                    "status": "UP",
                    "hostname": hostname
                })

                break

        print(f"Discovery completed: {len(devices)} hosts found.")

        return devices

    except (ValueError, subprocess.TimeoutExpired, FileNotFoundError,
            ET.ParseError, RuntimeError) as error:

        print(f"Discovery error: {error}")
        return []
